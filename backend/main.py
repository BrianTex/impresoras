from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, date
from pydantic import BaseModel
import uvicorn
import asyncio

import models, database, snmp_service
from database import SessionLocal, engine
import re

def parse_printer_date(date_str):
    if not date_str or date_str == "N/A": return None
    months = {
        'ene': 'Jan', 'feb': 'Feb', 'mar': 'Mar', 'abr': 'Apr', 'may': 'May', 'jun': 'Jun',
        'jul': 'Jul', 'ago': 'Aug', 'sep': 'Sep', 'oct': 'Oct', 'nov': 'Nov', 'dic': 'Dec'
    }
    date_str_lower = date_str.lower()
    for es, en in months.items():
        if es in date_str_lower:
            date_str = date_str_lower.replace(es, en.lower())
            break
            
    formats = [
        "%b %d, %Y", "%d/%m/%Y", "%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d-%m-%Y"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.title(), fmt).date()
        except ValueError:
            pass
    return None

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

async def background_status_updater():
    while True:
        try:
            db = SessionLocal()
            printers = db.query(models.Printer).all()
            today = date.today()

            for p in printers:
                status = await snmp_service.get_printer_data(p.ip_address)
                
                if status["status"] == "Online":
                    if status["toner_install_date"] != "N/A" and status["toner_install_date"] != p.last_toner_install_date:
                        if p.last_toner_install_date is not None:
                            notif = models.Notification(
                                printer_id=p.id,
                                message=f'Tóner cambiado en la impresora {p.name} (Nueva fecha: {status["toner_install_date"]})'
                            )
                            db.add(notif)
                        
                        p.last_toner_install_date = status["toner_install_date"]
                        db.commit()

                        install_date = parse_printer_date(status["toner_install_date"])
                        if install_date:
                            hist = db.query(models.PrinterHistory).filter(
                                models.PrinterHistory.printer_id == p.id,
                                models.PrinterHistory.date == install_date
                            ).first()
                            if not hist:
                                hist = models.PrinterHistory(printer_id=p.id, date=install_date, toner_changed=True)
                                db.add(hist)
                            else:
                                hist.toner_changed = True
                            db.commit()

                    first_log = db.query(models.DailyLog).filter(
                        models.DailyLog.printer_id == p.id,
                        models.DailyLog.date >= datetime.combine(today, datetime.min.time())
                    ).order_by(models.DailyLog.date.asc()).first()

                    if not first_log:
                        first_log = models.DailyLog(
                            printer_id=p.id,
                            total_pages=status["page_count"],
                            copied_pages=status["copied_count"],
                            printed_pages=status["printed_count"],
                            two_sided_copied_pages=status.get("two_sided_copied_count", 0),
                            two_sided_printed_pages=status.get("two_sided_printed_count", 0),
                            toner_percent=status["toner_percent"]
                        )
                        db.add(first_log)
                        db.commit()

                    daily_total = status["page_count"] - first_log.total_pages
                    daily_copied = status["copied_count"] - first_log.copied_pages
                    daily_printed = status["printed_count"] - first_log.printed_pages
                    daily_two_sided_copied = status.get("two_sided_copied_count", 0) - (first_log.two_sided_copied_pages or 0)
                    daily_two_sided_printed = status.get("two_sided_printed_count", 0) - (first_log.two_sided_printed_pages or 0)
                    daily_toner_drop = round(first_log.toner_percent - status["toner_percent"], 2)

                    history_record = db.query(models.PrinterHistory).filter(
                        models.PrinterHistory.printer_id == p.id,
                        models.PrinterHistory.date == today
                    ).first()

                    if not history_record:
                        history_record = models.PrinterHistory(
                            printer_id=p.id,
                            date=today,
                            daily_printed=daily_printed,
                            daily_copied=daily_copied,
                            daily_two_sided_copied=daily_two_sided_copied,
                            daily_two_sided_printed=daily_two_sided_printed,
                            daily_toner_drop=daily_toner_drop
                        )
                        db.add(history_record)
                    else:
                        history_record.daily_printed = daily_printed
                        history_record.daily_copied = daily_copied
                        history_record.daily_two_sided_copied = daily_two_sided_copied
                        history_record.daily_two_sided_printed = daily_two_sided_printed
                        history_record.daily_toner_drop = daily_toner_drop
                    db.commit()
            db.close()
        except Exception as e:
            print("Error en tarea de fondo:", e)
        
        await asyncio.sleep(3600)  # 1 hora

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(background_status_updater())

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/printers")
def read_printers(db: Session = Depends(get_db)):
    return db.query(models.Printer).all()

class PrinterCreate(BaseModel):
    name: str
    ip_address: str

@app.post("/printers")
def create_printer(printer: PrinterCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Printer).filter(models.Printer.ip_address == printer.ip_address).first()
    if existing:
        raise HTTPException(status_code=400, detail="IP ya registrada")
    db_p = models.Printer(name=printer.name, ip_address=printer.ip_address)
    db.add(db_p)
    db.commit()
    db.refresh(db_p)
    return db_p

@app.get("/printers/status")
async def get_all_status(db: Session = Depends(get_db)):
    printers = db.query(models.Printer).all()
    results = []
    today = date.today()

    for p in printers:
        status = await snmp_service.get_printer_data(p.ip_address)
        status["name"] = p.name
        status["db_id"] = p.id
        
        if status["status"] == "Online":
            if status["toner_install_date"] != "N/A" and status["toner_install_date"] != p.last_toner_install_date:
                if p.last_toner_install_date is not None:
                    notif = models.Notification(
                        printer_id=p.id,
                        message=f'Tóner cambiado en la impresora {p.name} (Nueva fecha: {status["toner_install_date"]})'
                    )
                    db.add(notif)
                    
                p.last_toner_install_date = status["toner_install_date"]
                db.commit()

                install_date = parse_printer_date(status["toner_install_date"])
                if install_date:
                    hist = db.query(models.PrinterHistory).filter(
                        models.PrinterHistory.printer_id == p.id,
                        models.PrinterHistory.date == install_date
                    ).first()
                    if not hist:
                        hist = models.PrinterHistory(printer_id=p.id, date=install_date, toner_changed=True)
                        db.add(hist)
                    else:
                        hist.toner_changed = True
                    db.commit()

            first_log = db.query(models.DailyLog).filter(
                models.DailyLog.printer_id == p.id,
                models.DailyLog.date >= datetime.combine(today, datetime.min.time())
            ).order_by(models.DailyLog.date.asc()).first()

            if not first_log:
                first_log = models.DailyLog(
                    printer_id=p.id,
                    total_pages=status["page_count"],
                    copied_pages=status["copied_count"],
                    printed_pages=status["printed_count"],
                    two_sided_copied_pages=status.get("two_sided_copied_count", 0),
                    two_sided_printed_pages=status.get("two_sided_printed_count", 0),
                    toner_percent=status["toner_percent"]
                )
                db.add(first_log)
                db.commit()

            daily_total = status["page_count"] - first_log.total_pages
            daily_copied = status["copied_count"] - first_log.copied_pages
            daily_printed = status["printed_count"] - first_log.printed_pages
            daily_two_sided_copied = status.get("two_sided_copied_count", 0) - (first_log.two_sided_copied_pages or 0)
            daily_two_sided_printed = status.get("two_sided_printed_count", 0) - (first_log.two_sided_printed_pages or 0)
            daily_toner_drop = round(first_log.toner_percent - status["toner_percent"], 2)

            status["daily_total"] = daily_total
            status["daily_copied"] = daily_copied
            status["daily_printed"] = daily_printed
            status["daily_two_sided_copied"] = daily_two_sided_copied
            status["daily_two_sided_printed"] = daily_two_sided_printed
            status["daily_toner_drop"] = daily_toner_drop

            # Actualizar o crear registro histórico del día
            history_record = db.query(models.PrinterHistory).filter(
                models.PrinterHistory.printer_id == p.id,
                models.PrinterHistory.date == today
            ).first()

            if not history_record:
                history_record = models.PrinterHistory(
                    printer_id=p.id,
                    date=today,
                    daily_printed=daily_printed,
                    daily_copied=daily_copied,
                    daily_two_sided_copied=daily_two_sided_copied,
                    daily_two_sided_printed=daily_two_sided_printed,
                    daily_toner_drop=daily_toner_drop
                )
                db.add(history_record)
            else:
                history_record.daily_printed = daily_printed
                history_record.daily_copied = daily_copied
                history_record.daily_two_sided_copied = daily_two_sided_copied
                history_record.daily_two_sided_printed = daily_two_sided_printed
                history_record.daily_toner_drop = daily_toner_drop
            db.commit()

        else:
            status["daily_total"] = 0
            status["daily_copied"] = 0
            status["daily_printed"] = 0
            status["daily_two_sided_copied"] = 0
            status["daily_two_sided_printed"] = 0
            status["daily_toner_drop"] = 0
            
        results.append(status)
    
    return results

@app.get("/printers/{printer_id}/history")
def get_printer_history(printer_id: int, db: Session = Depends(get_db)):
    history = db.query(models.PrinterHistory).filter(
        models.PrinterHistory.printer_id == printer_id
    ).order_by(models.PrinterHistory.date.desc()).all()
    return history

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
