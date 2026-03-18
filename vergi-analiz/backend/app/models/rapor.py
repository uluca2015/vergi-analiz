from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.database import Base


class RaporTuru(str, enum.Enum):
    VERGI_ANALIZ = "vergi_analiz"
    FINANSAL_ANALIZ = "finansal_analiz"
    RISK_RAPORU = "risk_raporu"
    KREDI_UYGUNLUK = "kredi_uygunluk"
    TAM_RAPOR = "tam_rapor"


class Rapor(Base):
    __tablename__ = "raporlar"

    id = Column(Integer, primary_key=True, index=True)
    firma_id = Column(Integer, ForeignKey("firmalar.id"), nullable=False)
    mizan_id = Column(Integer, ForeignKey("mizanlar.id"), nullable=True)

    rapor_turu = Column(Enum(RaporTuru), nullable=False)
    baslik = Column(String(500), nullable=False)

    # Mali tablo verileri (JSON)
    bilanco = Column(Text, nullable=True)           # JSON
    gelir_tablosu = Column(Text, nullable=True)     # JSON
    finansal_oranlar = Column(Text, nullable=True)  # JSON

    # Vergi hesaplamaları (JSON)
    vergi_hesaplama = Column(Text, nullable=True)   # JSON

    # Risk skorları
    vergi_risk_skoru = Column(Numeric(5, 2), nullable=True)  # 0-100
    kredi_uygunluk_skoru = Column(Numeric(5, 2), nullable=True)  # 0-100

    # AI rapor içeriği
    ai_rapor = Column(Text, nullable=True)
    ai_oneriler = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # İlişkiler
    firma = relationship("Firma", back_populates="raporlar")
    mizan = relationship("Mizan", back_populates="raporlar")
