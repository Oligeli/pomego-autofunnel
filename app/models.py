from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    website = Column(String, index=True)
    email = Column(String)
    phone = Column(String)
    address = Column(String)
    segment = Column(String)
    status = Column(String, default="new")  
    lead_score = Column(Integer, default=0)

    audits = relationship("Audit", back_populates="company")
    emails = relationship("EmailLog", back_populates="company")


class Audit(Base):
    __tablename__ = "audits"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    audit_text = Column(Text)
    score = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="audits")


class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    email_type = Column(String)
    content = Column(Text)
    sent_at = Column(DateTime, default=datetime.utcnow)
    opened = Column(Boolean, default=False)

    company = relationship("Company", back_populates="emails")

