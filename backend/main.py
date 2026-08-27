from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, date
from pydantic import BaseModel
from fastapi.concurrency import run_in_threadpool
import uvicorn
import asyncio

import models, database, snmp_service
from database import SessionLocal, engine

def parse_printer_date(date_str):
    if not date_str or date_str == "N/A": return None
    months = {'ene':'Jan','feb':'Feb','mar':'Mar','abr':'Apr','may':'May','jun':'Jun',
              'jul':'Jul','ago':'Aug','sep':'Sep','oct':'Oct','nov':'Nov','dic':'Dec'}
    d = date_str.lower()
    for es, en in months.items():
        if es in d:
            d = d.replace(es, en.lower())
            break
    for fmt in ["%b %d, %Y", "%d/%m/%Y", "%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d-%m-%Y"]:
        try:
            return datetime.strptime(d.title(), fmt).date()
        except ValueError:
            pass
    return None

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def update_printer_sync(db: Session, p: models.Printer, status: dict):
    """Toma el resultado del scraping y actualiza BD (histórico + snapshot cacheado). Síncrono a propósito."""
    today = date.today()

    if status["status"] == "Online":
        if status["toner_install_date"] != "N/A" and status["toner_install_date"] != p.last_toner_install_date:
            if p.last_toner_install_date is not None:
                db.add(models.Notification(
                    printer_id=p.id,
                    message=f'Tóner cambiado en la impresora {p.name} (Nueva fecha: {status["toner_install_date"]})'
                ))
            p.last_toner_install_date = status["toner_install_date"]
            install_date = parse_printer_date(status["toner_install_date"])
            if install_date:
                hist = db.query(models.PrinterHistory).filter_by(printer_id=p.id, date=install_date).first()
                if not hist:
                    db.add(models.PrinterHistory(printer_id=p.id, date=install_date, toner_changed=True))
                else:
                    hist.toner_changed = True

        first_log = db.query(models.DailyLog).filter(
            models.DailyLog.printer_id == p.id,
            models.DailyLog.date >= datetime.combine(today, datetime.min.time())
        ).order_by(models.DailyLog.date.asc()).first()

        if not first_log:
            first_log = models.DailyLog(
                printer_id=p.id, total_pages=status["page_count"], copied_pages=status["copied_count"],
                printed_pages=status["printed_count"],
                two_sided_copied_pages=status["two_sided_copied_count"],
                two_sided_printed_pages=status["two_sided_printed_count"],
                toner_percent=status["toner_percent"]
            )
            db.add(first_log)
            db.flush()

        daily_copied = status["copied_count"] - first_log.copied_pages
        daily_printed = status["printed_count"] - first_log.printed_pages
        daily_ts_copied = status["two_sided_copied_count"] - (first_log.two_sided_copied_pages or 0)
        daily_ts_printed = status["two_sided_printed_count"] - (first_log.two_sided_printed_pages or 0)
        daily_toner_drop = round(first_log.toner_percent - status["toner_percent"], 2)
        daily_total = status["page_count"] - first_log.total_pages

        hist_today = db.query(models.PrinterHistory).filter_by(printer_id=p.id, date=today).first()
        if not hist_today:
            hist_today = models.PrinterHistory(printer_id=p.id, date=today)
            db.add(hist_today)
        hist_today.daily_printed = daily_printed
        hist_today.daily_copied = daily_copied
        hist_today.daily_two_sided_copied = daily_ts_copied
        hist_today.daily_two_sided_printed = daily_ts_printed
        hist_today.daily_toner_drop = daily_toner_drop

        # snapshot cacheado
        p.last_status = "Online"
        p.serial = status["serial"]
        p.location = status["location"]
        p.page_count = status["page_count"]
        p.copied_count = status["copied_count"]
        p.printed_count = status["printed_count"]
        p.two_sided_copied_count = status["two_sided_copied_count"]
        p.two_sided_printed_count = status["two_sided_printed_count"]
        p.toner_percent = status["toner_percent"]
        p.daily_total = daily_total
        p.daily_copied = daily_copied
        p.daily_printed = daily_printed
        p.daily_two_sided_copied = daily_ts_copied
        p.daily_two_sided_printed = daily_ts_printed
        p.daily_toner_drop = daily_toner_drop
    else:
        p.last_status = "Offline"

    p.last_checked_at = datetime.utcnow()
    db.commit()

async def refresh_printer(printer_id: int):
    db = SessionLocal()
    try:
        p = db.query(models.Printer).filter(models.Printer.id == printer_id).first()
        if not p:
            return
        status = await snmp_service.get_printer_data(p.ip_address)
        await run_in_threadpool(update_printer_sync, db, p, status)
    finally:
        db.close()

async def background_status_updater():
    while True:
        try:
            db = SessionLocal()
            printer_ids = [p.id for p in db.query(models.Printer.id).all()]
            db.close()
            for pid in printer_ids:
                await refresh_printer(pid)
        except Exception as e:
            print("Error en tarea de fondo:", e)
        await asyncio.sleep(3600)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(background_status_updater())

@app.get("/printers")
def read_printers(db: Session = Depends(get_db)):
    return db.query(models.Printer).all()

class PrinterCreate(BaseModel):
    name: str
    ip_address: str

@app.post("/printers")
def create_printer(printer: PrinterCreate, db: Session = Depends(get_db)):
    if db.query(models.Printer).filter(models.Printer.ip_address == printer.ip_address).first():
        raise HTTPException(status_code=400, detail="IP ya registrada")
    db_p = models.Printer(name=printer.name, ip_address=printer.ip_address)
    db.add(db_p)
    db.commit()
    db.refresh(db_p)
    # dispara un primer scraping en segundo plano sin bloquear la respuesta
    asyncio.create_task(refresh_printer(db_p.id))
    return db_p

@app.get("/printers/status")
def get_all_status(db: Session = Depends(get_db)):
    """Ahora es una simple lectura de BD: responde en milisegundos."""
    printers = db.query(models.Printer).all()
    return [{
        "db_id": p.id, "name": p.name, "ip": p.ip_address,
        "status": p.last_status, "serial": p.serial, "location": p.location,
        "page_count": p.page_count, "copied_count": p.copied_count, "printed_count": p.printed_count,
        "two_sided_copied_count": p.two_sided_copied_count, "two_sided_printed_count": p.two_sided_printed_count,
        "toner_percent": p.toner_percent, "toner_install_date": p.last_toner_install_date or "N/A",
        "daily_total": p.daily_total, "daily_copied": p.daily_copied, "daily_printed": p.daily_printed,
        "daily_two_sided_copied": p.daily_two_sided_copied, "daily_two_sided_printed": p.daily_two_sided_printed,
        "daily_toner_drop": p.daily_toner_drop,
        "last_checked_at": p.last_checked_at,
    } for p in printers]

@app.post("/printers/{printer_id}/refresh")
async def force_refresh(printer_id: int):
    """Botón 'Actualizar' del frontend: dispara scraping real de UNA impresora, sin bloquear a las demás."""
    p_exists = SessionLocal().query(models.Printer.id).filter(models.Printer.id == printer_id).first()
    if not p_exists:
        raise HTTPException(status_code=404, detail="Impresora no encontrada")
    await refresh_printer(printer_id)
    return {"status": "ok"}

@app.get("/printers/{printer_id}/history")
def get_printer_history(printer_id: int, db: Session = Depends(get_db)):
    return db.query(models.PrinterHistory).filter(
        models.PrinterHistory.printer_id == printer_id
    ).order_by(models.PrinterHistory.date.desc()).all()

@app.get("/notifications")
def get_notifications(db: Session = Depends(get_db)):
    return db.query(models.Notification).order_by(models.Notification.created_at.desc()).all()

@app.post("/notifications/{notif_id}/read")
def read_notification(notif_id: int, db: Session = Depends(get_db)):
    notif = db.query(models.Notification).filter(models.Notification.id == notif_id).first()
    if notif:
        notif.read = True
        db.commit()
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
