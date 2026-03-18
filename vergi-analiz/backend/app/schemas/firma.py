from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.firma import MukellefTuru, SirketTuru, VergilendirmeSekli


class FirmaBase(BaseModel):
    unvan: str
    mukellef_turu: MukellefTuru
    sirket_turu: Optional[SirketTuru] = None
    vergilendirme_sekli: VergilendirmeSekli = VergilendirmeSekli.GERCEK_USUL
    vergi_no: str
    vergi_dairesi: str
    ticaret_sicil_no: Optional[str] = None
    mersis_no: Optional[str] = None
    adres: Optional[str] = None
    il: Optional[str] = None
    ilce: Optional[str] = None
    telefon: Optional[str] = None
    email: Optional[str] = None
    faaliyet_konusu: Optional[str] = None
    nace_kodu: Optional[str] = None
    kurulis_tarihi: Optional[str] = None
    notlar: Optional[str] = None


class FirmaCreate(FirmaBase):
    pass


class FirmaUpdate(BaseModel):
    unvan: Optional[str] = None
    sirket_turu: Optional[SirketTuru] = None
    vergilendirme_sekli: Optional[VergilendirmeSekli] = None
    vergi_dairesi: Optional[str] = None
    ticaret_sicil_no: Optional[str] = None
    adres: Optional[str] = None
    il: Optional[str] = None
    ilce: Optional[str] = None
    telefon: Optional[str] = None
    email: Optional[str] = None
    faaliyet_konusu: Optional[str] = None
    notlar: Optional[str] = None


class FirmaResponse(FirmaBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class FirmaListItem(BaseModel):
    id: int
    unvan: str
    vergi_no: str
    mukellef_turu: MukellefTuru
    sirket_turu: Optional[SirketTuru] = None
    il: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
