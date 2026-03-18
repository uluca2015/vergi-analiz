from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json
from app.db.database import get_db
from app.models.firma import Firma
from app.models.mizan import Mizan
from app.models.rapor import Rapor, RaporTuru
from app.models.user import User
from app.core.security import get_current_user
from app.services.vergi_hesaplama import tam_vergi_hesapla
from app.services.finansal_analiz import hesapla_finansal_oranlar, hesapla_vergi_risk_skoru, hesapla_kredi_uygunluk
from app.services.ai_rapor import generate_ai_rapor

router = APIRouter(prefix="/api/raporlar", tags=["raporlar"])


@router.post("/olustur/{mizan_id}")
async def rapor_olustur(
    mizan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    mizan = db.query(Mizan).join(Firma).filter(
        Mizan.id == mizan_id,
        Firma.user_id == current_user.id
    ).first()
    if not mizan:
        raise HTTPException(status_code=404, detail="Mizan bulunamadı")

    firma = mizan.firma
    ozet = json.loads(mizan.hesaplar_ozet) if mizan.hesaplar_ozet else {}

    # Hesaplamalar
    vergi = tam_vergi_hesapla(ozet, firma.mukellef_turu.value, mizan.donem_yili)
    oranlar = hesapla_finansal_oranlar(ozet)
    risk = hesapla_vergi_risk_skoru(ozet, vergi, oranlar)
    kredi = hesapla_kredi_uygunluk(ozet, oranlar)

    # Bilanço oluştur
    bilanco = _bilanco_olustur(ozet)
    gelir_tablosu = _gelir_tablosu_olustur(ozet)

    # AI raporu
    firma_bilgi = {
        "unvan": firma.unvan,
        "mukellef_turu": firma.mukellef_turu.value,
        "sirket_turu": firma.sirket_turu.value if firma.sirket_turu else None,
        "vergi_no": firma.vergi_no,
        "vergi_dairesi": firma.vergi_dairesi,
    }
    ai_sonuc = await generate_ai_rapor(firma_bilgi, vergi, oranlar, risk, kredi)

    # Raporu kaydet
    rapor = Rapor(
        firma_id=firma.id,
        mizan_id=mizan.id,
        rapor_turu=RaporTuru.TAM_RAPOR,
        baslik=f"{firma.unvan} — {mizan.donem_yili} {mizan.vergilendirme_donemi.value} Tam Analiz Raporu",
        bilanco=json.dumps(bilanco, ensure_ascii=False),
        gelir_tablosu=json.dumps(gelir_tablosu, ensure_ascii=False),
        finansal_oranlar=json.dumps(oranlar, ensure_ascii=False),
        vergi_hesaplama=json.dumps(vergi, ensure_ascii=False),
        vergi_risk_skoru=risk["skor"],
        kredi_uygunluk_skoru=kredi["skor"],
        ai_rapor=ai_sonuc["rapor"],
        ai_oneriler=ai_sonuc["oneriler"],
    )
    db.add(rapor)
    db.commit()
    db.refresh(rapor)

    return {
        "rapor_id": rapor.id,
        "baslik": rapor.baslik,
        "bilanco": bilanco,
        "gelir_tablosu": gelir_tablosu,
        "finansal_oranlar": oranlar,
        "vergi_hesaplama": vergi,
        "vergi_risk": risk,
        "kredi_uygunluk": kredi,
        "ai_rapor": ai_sonuc["rapor"],
        "ai_oneriler": ai_sonuc["oneriler"],
    }


@router.get("/firma/{firma_id}")
def firma_raporlari(firma_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    firma = db.query(Firma).filter(Firma.id == firma_id, Firma.user_id == current_user.id).first()
    if not firma:
        raise HTTPException(status_code=404, detail="Firma bulunamadı")
    raporlar = db.query(Rapor).filter(Rapor.firma_id == firma_id).order_by(Rapor.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "baslik": r.baslik,
            "rapor_turu": r.rapor_turu.value,
            "vergi_risk_skoru": float(r.vergi_risk_skoru) if r.vergi_risk_skoru else None,
            "kredi_uygunluk_skoru": float(r.kredi_uygunluk_skoru) if r.kredi_uygunluk_skoru else None,
            "created_at": r.created_at.isoformat(),
        }
        for r in raporlar
    ]


@router.get("/{rapor_id}")
def rapor_detay(rapor_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rapor = db.query(Rapor).join(Firma).filter(
        Rapor.id == rapor_id,
        Firma.user_id == current_user.id
    ).first()
    if not rapor:
        raise HTTPException(status_code=404, detail="Rapor bulunamadı")
    return {
        "id": rapor.id,
        "baslik": rapor.baslik,
        "bilanco": json.loads(rapor.bilanco) if rapor.bilanco else {},
        "gelir_tablosu": json.loads(rapor.gelir_tablosu) if rapor.gelir_tablosu else {},
        "finansal_oranlar": json.loads(rapor.finansal_oranlar) if rapor.finansal_oranlar else {},
        "vergi_hesaplama": json.loads(rapor.vergi_hesaplama) if rapor.vergi_hesaplama else {},
        "vergi_risk_skoru": float(rapor.vergi_risk_skoru) if rapor.vergi_risk_skoru else None,
        "kredi_uygunluk_skoru": float(rapor.kredi_uygunluk_skoru) if rapor.kredi_uygunluk_skoru else None,
        "ai_rapor": rapor.ai_rapor,
        "ai_oneriler": rapor.ai_oneriler,
        "created_at": rapor.created_at.isoformat(),
    }


def _bilanco_olustur(ozet: dict) -> dict:
    return {
        "aktif": {
            "donen_varliklar": {
                "kasa_banka": round(ozet.get("kasa_banka", 0), 2),
                "alicilar": round(ozet.get("alicilar", 0), 2),
                "stoklar": round(ozet.get("stoklar", 0), 2),
                "toplam": round(ozet.get("donen_varliklar", 0), 2),
            },
            "duran_varliklar": {
                "toplam": round(ozet.get("duran_varliklar", 0), 2),
            },
            "toplam_aktif": round(ozet.get("toplam_aktif", 0), 2),
        },
        "pasif": {
            "kvyk": {
                "saticiler": round(ozet.get("saticiler", 0), 2),
                "banka_kredileri": round(ozet.get("banka_kredileri_kv", 0), 2),
                "vergi_borclar": round(ozet.get("vergi_karsiligi", 0), 2),
                "toplam": round(ozet.get("kvyk", 0), 2),
            },
            "uvyk": {
                "toplam": round(ozet.get("uvyk", 0), 2),
            },
            "ozkaynak": {
                "toplam": round(ozet.get("ozkaynak", 0), 2),
            },
            "toplam_pasif": round(ozet.get("toplam_pasif", 0), 2),
        },
    }


def _gelir_tablosu_olustur(ozet: dict) -> dict:
    ns = ozet.get("net_satislar", 0)
    sm = ozet.get("satislar_maliyeti", 0)
    bk = ozet.get("brut_kar", 0)
    fg = ozet.get("faaliyet_giderleri", 0)
    fk = ozet.get("faaliyet_kari", 0)
    fingid = ozet.get("finansman_giderleri", 0)
    dk = ozet.get("donem_kari", 0)

    return {
        "net_satislar": round(ns, 2),
        "satislar_maliyeti": round(sm, 2),
        "brut_kar": round(bk, 2),
        "brut_kar_marji_yuzde": round((bk / ns * 100) if ns else 0, 2),
        "faaliyet_giderleri": round(fg, 2),
        "faaliyet_kari": round(fk, 2),
        "faaliyet_kar_marji_yuzde": round((fk / ns * 100) if ns else 0, 2),
        "finansman_giderleri": round(fingid, 2),
        "donem_kari": round(dk, 2),
        "net_kar_marji_yuzde": round((dk / ns * 100) if ns else 0, 2),
    }
