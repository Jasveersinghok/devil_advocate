from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from config import get_settings

settings = get_settings()
engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class ResearchJob(Base):
    __tablename__ = "research_jobs"

    id = Column(String, primary_key=True)  # UUID
    claim = Column(Text, nullable=False)
    status = Column(String, default="pending")  # pending | running | done | error
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Results
    sub_claims = Column(JSON, nullable=True)         # List[str]
    pro_evidence = Column(JSON, nullable=True)       # List[EvidenceItem]
    counter_evidence = Column(JSON, nullable=True)   # List[EvidenceItem]
    confidence_score = Column(Float, nullable=True)  # 0-100
    report_markdown = Column(Text, nullable=True)
    report_json = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
