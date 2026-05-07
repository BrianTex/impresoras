from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Printer(Base):
    __tablename__ = "printers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    ip_address = Column(String, unique=True, index=True)
    
    logs = relationship("DailyLog", back_populates="printer")

class DailyLog(Base):
    __tablename__ = "daily_logs"

    id = Column(Integer, primary_key=True, index=True)
    printer_id = Column(Integer, ForeignKey("printers.id"))
    date = Column(DateTime, default=datetime.utcnow)
    
    total_pages = Column(Integer, default=0)
    copied_pages = Column(Integer, default=0)
    printed_pages = Column(Integer, default=0)
    toner_percent = Column(Float)
    
    printer = relationship("Printer", back_populates="logs")

class PrinterHistory(Base):
    __tablename__ = "printer_history"

    id = Column(Integer, primary_key=True, index=True)
    printer_id = Column(Integer, ForeignKey("printers.id"))
    date = Column(Date, index=True)
    
    daily_printed = Column(Integer, default=0)
    daily_copied = Column(Integer, default=0)
    daily_toner_drop = Column(Float, default=0.0)
