from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, date
import uvicorn
import asyncio

import models, database, snmp_service
from database import SessionLocal, engine

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
                            toner_percent=status["toner_percent"]
                        )
                        db.add(first_log)
                        db.commit()

                    daily_total = status["page_count"] - first_log.total_pages
                    daily_copied = status["copied_count"] - first_log.copied_pages
                    daily_printed = status["printed_count"] - first_log.printed_pages
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
                            daily_toner_drop=daily_toner_drop
                        )
                        db.add(history_record)
                    else:
                        history_record.daily_printed = daily_printed
                        history_record.daily_copied = daily_copied
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

@app.post("/printers")
def create_printer(name: str, ip_address: str, db: Session = Depends(get_db)):
    existing = db.query(models.Printer).filter(models.Printer.ip_address == ip_address).first()
    if existing:
        raise HTTPException(status_code=400, detail="IP ya registrada")
    db_p = models.Printer(name=name, ip_address=ip_address)
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
                    toner_percent=status["toner_percent"]
                )
                db.add(first_log)
                db.commit()

            daily_total = status["page_count"] - first_log.total_pages
            daily_copied = status["copied_count"] - first_log.copied_pages
            daily_printed = status["printed_count"] - first_log.printed_pages
            daily_toner_drop = round(first_log.toner_percent - status["toner_percent"], 2)

            status["daily_total"] = daily_total
            status["daily_copied"] = daily_copied
            status["daily_printed"] = daily_printed
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
                    daily_toner_drop=daily_toner_drop
                )
                db.add(history_record)
            else:
                history_record.daily_printed = daily_printed
                history_record.daily_copied = daily_copied
                history_record.daily_toner_drop = daily_toner_drop
            db.commit()

        else:
            status["daily_total"] = 0
            status["daily_copied"] = 0
            status["daily_printed"] = 0
            status["daily_toner_drop"] = 0
            
        results.append(status)
    
    return results

@app.get("/printers/{printer_id}/history")
def get_printer_history(printer_id: int, db: Session = Depends(get_db)):
    history = db.query(models.PrinterHistory).filter(
        models.PrinterHistory.printer_id == printer_id
    ).order_by(models.PrinterHistory.date.desc()).all()
    return history


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
