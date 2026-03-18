from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.database import Base


class MukellefTuru(str, enum.Enum):
    SAHIS = "sahis"
    SIRKET = "sirket"


class SirketTuru(str, enum.Enum):
    ANONIM = "anonim_sirket"
    LIMITED = "limited_sirket"
    KOLEKTIF = "kolektif_sirket"
    KOMANDIT = "komandit_sirket"
    KOOPERATIF = "kooperatif"
    SERBEST_MESLEK = "serbest_meslek"
    DIGER = "diger"


class VergilendirmeSekli(str, enum.Enum):
    GERCEK_USUL = "gercek_usul"
    BASIT_USUL = "basit_usul"
    GOTURU = "goturu"


class Firma(Base):
    __tablename__ = "firmalar"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Temel bilgiler
    unvan = Column(String(500), nullable=False)
    mukellef_turu = Column(Enum(MukellefTuru), nullable=False)
    sirket_turu = Column(Enum(SirketTuru), nullable=True)
    vergilendirme_sekli = Column(Enum(VergilendirmeSekli), default=VergilendirmeSekli.GERCEK_USUL)

    # Vergi / Ticaret bilgileri
    vergi_no = Column(String(20), unique=True, index=True, nullable=False)
    vergi_dairesi = Column(String(200), nullable=False)
    ticaret_sicil_no = Column(String(50), nullable=True)
    mersis_no = Column(String(50), nullable=True)

    # İletişim
    adres = Column(Text, nullable=True)
    il = Column(String(100), nullable=True)
    ilce = Column(String(100), nullable=True)
    telefon = Column(String(20), nullable=True)
    email = Column(String(200), nullable=True)

    # Faaliyet
    faaliyet_konusu = Column(Text, nullable=True)
    nace_kodu = Column(String(10), nullable=True)
    kurulis_tarihi = Column(String(10), nullable=True)

    # Meta
    notlar = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # İlişkiler
    user = relationship("User", back_populates="firmalar")
    mizanlar = relationship("Mizan", back_populates="firma", cascade="all, delete-orphan")
    raporlar = relationship("Rapor", back_populates="firma", cascade="all, delete-orphan")
