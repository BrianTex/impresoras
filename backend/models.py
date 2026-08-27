from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Printer(Base):
    __tablename__ = "printers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    ip_address = Column(String, unique=True, index=True)
    last_toner_install_date = Column(String, nullable=True)

    # --- NUEVO: snapshot cacheado del último scraping ---
    last_status = Column(String, default="Offline")
    last_checked_at = Column(DateTime, nullable=True)
    serial = Column(String, default="N/A")
    location = Column(String, default="N/A")
    page_count = Column(Integer, default=0)
    copied_count = Column(Integer, default=0)
    printed_count = Column(Integer, default=0)
    two_sided_copied_count = Column(Integer, default=0)
    two_sided_printed_count = Column(Integer, default=0)
    toner_percent = Column(Float, default=0)
    daily_total = Column(Integer, default=0)
    daily_copied = Column(Integer, default=0)
    daily_printed = Column(Integer, default=0)
    daily_two_sided_copied = Column(Integer, default=0)
    daily_two_sided_printed = Column(Integer, default=0)
    daily_toner_drop = Column(Float, default=0.0)

    logs = relationship("DailyLog", back_populates="printer")
    notifications = relationship("Notification", back_populates="printer")

class DailyLog(Base):
    __tablename__ = "daily_logs"

    id = Column(Integer, primary_key=True, index=True)
    printer_id = Column(Integer, ForeignKey("printers.id"))
    date = Column(DateTime, default=datetime.utcnow)
    
    total_pages = Column(Integer, default=0)
    copied_pages = Column(Integer, default=0)
    printed_pages = Column(Integer, default=0)
    two_sided_copied_pages = Column(Integer, default=0)
    two_sided_printed_pages = Column(Integer, default=0)
    toner_percent = Column(Float)
    
    printer = relationship("Printer", back_populates="logs")

class PrinterHistory(Base):
    __tablename__ = "printer_history"

    id = Column(Integer, primary_key=True, index=True)
    printer_id = Column(Integer, ForeignKey("printers.id"))
    date = Column(Date, index=True)
    
    daily_printed = Column(Integer, default=0)
    daily_copied = Column(Integer, default=0)
    daily_two_sided_printed = Column(Integer, default=0)
    daily_two_sided_copied = Column(Integer, default=0)
    daily_toner_drop = Column(Float, default=0.0)
    toner_changed = Column(Boolean, default=False)

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    printer_id = Column(Integer, ForeignKey("printers.id"))
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    read = Column(Boolean, default=False)
    
    printer = relationship("Printer", back_populates="notifications")
