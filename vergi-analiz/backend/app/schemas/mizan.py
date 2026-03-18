from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from app.models.mizan import VergilendirmeDonemi


class MizanKalemSchema(BaseModel):
    hesap_kodu: str
    hesap_adi: str
    borc_bakiye: float = 0
    alacak_bakiye: float = 0
    borc_hareket: float = 0
    alacak_hareket: float = 0


class MizanCreate(BaseModel):
    mizan_tarihi: date
    vergilendirme_donemi: VergilendirmeDonemi
    donem_yili: int
    notlar: Optional[str] = None


class MizanResponse(BaseModel):
    id: int
    firma_id: int
    mizan_tarihi: date
    vergilendirme_donemi: VergilendirmeDonemi
    donem_yili: int
    dosya_adi: Optional[str] = None
    notlar: Optional[str] = None
    created_at: datetime
    hesaplar_ozet: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class MizanDetay(MizanResponse):
    kalemleri: List[MizanKalemSchema] = []
