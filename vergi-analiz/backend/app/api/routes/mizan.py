from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import json
from datetime import date
from app.db.database import get_db
from app.models.firma import Firma
from app.models.mizan import Mizan, MizanKalem, VergilendirmeDonemi
from app.models.user import User
from app.schemas.mizan import MizanResponse, MizanDetay
from app.core.security import get_current_user
from app.services.mizan_parser import parse_excel_mizan
from app.services.vergi_hesaplama import tam_vergi_hesapla
from app.services.finansal_analiz import hesapla_finansal_oranlar, hesapla_vergi_risk_skoru, hesapla_kredi_uygunluk

router = APIRouter(prefix="/api/mizanlar", tags=["mizanlar"])


@router.get("/firma/{firma_id}", response_model=List[MizanResponse])
def firma_mizanlari(firma_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    firma = db.query(Firma).filter(Firma.id == firma_id, Firma.user_id == current_user.id).first()
    if not firma:
        raise HTTPException(status_code=404, detail="Firma bulunamadı")
    return db.query(Mizan).filter(Mizan.firma_id == firma_id).all()


@router.post("/yukle/{firma_id}")
async def mizan_yukle(
    firma_id: int,
    dosya: UploadFile = File(...),
    mizan_tarihi: str = Form(...),
    vergilendirme_donemi: VergilendirmeDonemi = Form(...),
    donem_yili: int = Form(...),
    notlar: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    firma = db.query(Firma).filter(Firma.id == firma_id, Firma.user_id == current_user.id).first()
    if not firma:
        raise HTTPException(status_code=404, detail="Firma bulunamadı")

    if not dosya.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Sadece Excel (.xlsx/.xls) dosyası kabul edilir")

    icerik = await dosya.read()

    try:
        kalemleri, ozet = parse_excel_mizan(icerik, dosya.filename)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Mizan kaydı oluştur
    mizan = Mizan(
        firma_id=firma_id,
        mizan_tarihi=date.fromisoformat(mizan_tarihi),
        vergilendirme_donemi=vergilendirme_donemi,
        donem_yili=donem_yili,
        dosya_adi=dosya.filename,
        notlar=notlar,
        hesaplar_ozet=json.dumps(ozet, ensure_ascii=False),
        ham_veri=json.dumps(kalemleri[:500], ensure_ascii=False),  # max 500 satır sakla
    )
    db.add(mizan)
    db.flush()

    # Kalem detaylarını kaydet
    for k in kalemleri:
        kalem = MizanKalem(
            mizan_id=mizan.id,
            hesap_kodu=k["hesap_kodu"],
            hesap_adi=k["hesap_adi"],
            borc_bakiye=k["borc_bakiye"],
            alacak_bakiye=k["alacak_bakiye"],
            borc_hareket=k.get("borc_hareket", 0),
            alacak_hareket=k.get("alacak_hareket", 0),
        )
        db.add(kalem)

    db.commit()
    db.refresh(mizan)

    # Vergi + finansal analiz hesapla
    vergi = tam_vergi_hesapla(ozet, firma.mukellef_turu.value, donem_yili)
    oranlar = hesapla_finansal_oranlar(ozet)
    risk = hesapla_vergi_risk_skoru(ozet, vergi, oranlar)
    kredi = hesapla_kredi_uygunluk(ozet, oranlar)

    return {
        "mizan_id": mizan.id,
        "firma_id": firma_id,
        "kalem_sayisi": len(kalemleri),
        "ozet": ozet,
        "vergi_hesaplama": vergi,
        "finansal_oranlar": oranlar,
        "vergi_risk": risk,
        "kredi_uygunluk": kredi,
    }


@router.get("/{mizan_id}", response_model=MizanDetay)
def mizan_detay(mizan_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    mizan = db.query(Mizan).join(Firma).filter(
        Mizan.id == mizan_id,
        Firma.user_id == current_user.id
    ).first()
    if not mizan:
        raise HTTPException(status_code=404, detail="Mizan bulunamadı")

    kalemleri = db.query(MizanKalem).filter(MizanKalem.mizan_id == mizan_id).all()
    ozet = json.loads(mizan.hesaplar_ozet) if mizan.hesaplar_ozet else {}

    return {
        **MizanResponse.from_orm(mizan).model_dump(),
        "hesaplar_ozet": ozet,
        "kalemleri": [
            {
                "hesap_kodu": k.hesap_kodu,
                "hesap_adi": k.hesap_adi,
                "borc_bakiye": float(k.borc_bakiye or 0),
                "alacak_bakiye": float(k.alacak_bakiye or 0),
                "borc_hareket": float(k.borc_hareket or 0),
                "alacak_hareket": float(k.alacak_hareket or 0),
            }
            for k in kalemleri
        ],
    }


@router.delete("/{mizan_id}")
def mizan_sil(mizan_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    mizan = db.query(Mizan).join(Firma).filter(
        Mizan.id == mizan_id,
        Firma.user_id == current_user.id
    ).first()
    if not mizan:
        raise HTTPException(status_code=404, detail="Mizan bulunamadı")
    db.delete(mizan)
    db.commit()
    return {"mesaj": "Mizan silindi"}
