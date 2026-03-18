from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Text, Enum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.database import Base


class VergilendirmeDonemi(str, enum.Enum):
    Q1 = "Q1"   # Ocak-Mart
    Q2 = "Q2"   # Nisan-Haziran
    Q3 = "Q3"   # Temmuz-Eylül
    Q4 = "Q4"   # Ekim-Aralık
    YILLIK = "YILLIK"


class Mizan(Base):
    __tablename__ = "mizanlar"

    id = Column(Integer, primary_key=True, index=True)
    firma_id = Column(Integer, ForeignKey("firmalar.id"), nullable=False)

    # Dönem bilgisi
    mizan_tarihi = Column(Date, nullable=False)
    vergilendirme_donemi = Column(Enum(VergilendirmeDonemi), nullable=False)
    donem_yili = Column(Integer, nullable=False)

    # Dosya
    dosya_adi = Column(String(500), nullable=True)
    dosya_yolu = Column(String(1000), nullable=True)

    # Ham veri (JSON olarak saklanır)
    ham_veri = Column(Text, nullable=True)  # JSON string

    # İşlenmiş hesaplar özeti (JSON)
    hesaplar_ozet = Column(Text, nullable=True)  # JSON string

    # Meta
    notlar = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # İlişkiler
    firma = relationship("Firma", back_populates="mizanlar")
    raporlar = relationship("Rapor", back_populates="mizan")


class MizanKalem(Base):
    __tablename__ = "mizan_kalemleri"

    id = Column(Integer, primary_key=True, index=True)
    mizan_id = Column(Integer, ForeignKey("mizanlar.id"), nullable=False)

    hesap_kodu = Column(String(20), nullable=False, index=True)
    hesap_adi = Column(String(500), nullable=False)
    borc_bakiye = Column(Numeric(20, 2), default=0)
    alacak_bakiye = Column(Numeric(20, 2), default=0)
    borc_hareket = Column(Numeric(20, 2), default=0)
    alacak_hareket = Column(Numeric(20, 2), default=0)

    mizan = relationship("Mizan", foreign_keys=[mizan_id])
