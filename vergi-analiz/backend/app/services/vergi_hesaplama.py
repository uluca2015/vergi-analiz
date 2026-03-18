from typing import Dict, Any, Optional
from decimal import Decimal


# 2024 Gelir Vergisi Tarifeleri (GVK md. 103)
GV_TARIFELERI_2024 = [
    {"alt": 0,         "ust": 110_000,    "oran": 0.15, "sabit": 0},
    {"alt": 110_000,   "ust": 230_000,    "oran": 0.20, "sabit": 16_500},
    {"alt": 230_000,   "ust": 580_000,    "oran": 0.27, "sabit": 40_500},
    {"alt": 580_000,   "ust": 3_000_000,  "oran": 0.35, "sabit": 135_000},
    {"alt": 3_000_000, "ust": float("inf"), "oran": 0.40, "sabit": 982_000},
]

# 2024 Kurumlar Vergisi Oranı (KVK md. 32)
KURUMLAR_VERGISI_ORANI_2024 = 0.25  # %25 (borsada işlem gören %20)
GECICI_VERGI_ORANI = 0.25

# Asgari Kurumlar Vergisi oranı (2024 - hasılat bazlı)
ASGARI_KV_ORANI = 0.10

# KDV Oranları
KDV_ORANLARI = {
    "genel": 0.20,    # Genel oran %20 (2023'te %18'den güncellendi)
    "indirimli_1": 0.10,
    "indirimli_2": 0.01,
}


def hesapla_gelir_vergisi(matrah: float, yil: int = 2024) -> Dict[str, Any]:
    """Gelir vergisi hesaplar (GVK md. 103 tarifeleri)."""
    if matrah <= 0:
        return {"matrah": 0, "vergi": 0, "efektif_oran": 0, "dilim_detay": []}

    tarife = GV_TARIFELERI_2024  # yıla göre genişletilebilir
    vergi = 0.0
    dilim_detay = []

    for dilim in tarife:
        if matrah <= dilim["alt"]:
            break
        ust = min(matrah, dilim["ust"])
        dilim_matrah = ust - dilim["alt"]
        dilim_vergi = dilim_matrah * dilim["oran"]
        vergi += dilim_vergi
        dilim_detay.append({
            "dilim": f"{dilim['alt']:,.0f} - {dilim['ust'] if dilim['ust'] != float('inf') else '∞':}",
            "oran": f"%{int(dilim['oran'] * 100)}",
            "matrah": round(dilim_matrah, 2),
            "vergi": round(dilim_vergi, 2),
        })
        if matrah <= dilim["ust"]:
            break

    efektif_oran = (vergi / matrah * 100) if matrah > 0 else 0

    return {
        "matrah": round(matrah, 2),
        "vergi": round(vergi, 2),
        "efektif_oran": round(efektif_oran, 2),
        "dilim_detay": dilim_detay,
        "yil": yil,
    }


def hesapla_kurumlar_vergisi(matrah: float, borsada_islem_goren: bool = False, yil: int = 2024) -> Dict[str, Any]:
    """Kurumlar vergisi hesaplar (KVK md. 32)."""
    if matrah <= 0:
        return {"matrah": 0, "vergi": 0, "oran": KURUMLAR_VERGISI_ORANI_2024, "asgari_kv": 0}

    oran = 0.20 if borsada_islem_goren else KURUMLAR_VERGISI_ORANI_2024
    vergi = matrah * oran

    return {
        "matrah": round(matrah, 2),
        "vergi": round(vergi, 2),
        "oran": oran,
        "yuzde": f"%{int(oran * 100)}",
        "borsada_islem_goren": borsada_islem_goren,
        "yil": yil,
    }


def hesapla_gecici_vergi(donem_kari: float, onceki_gecici_vergiler: float = 0) -> Dict[str, Any]:
    """Geçici vergi hesaplar."""
    if donem_kari <= 0:
        return {"matrah": 0, "vergi": 0, "odenmesi_gereken": 0}

    vergi = donem_kari * GECICI_VERGI_ORANI
    odenmesi_gereken = max(vergi - onceki_gecici_vergiler, 0)

    return {
        "matrah": round(donem_kari, 2),
        "vergi": round(vergi, 2),
        "onceki_tahakkuk": round(onceki_gecici_vergiler, 2),
        "odenmesi_gereken": round(odenmesi_gereken, 2),
        "oran": GECICI_VERGI_ORANI,
    }


def hesapla_kdv_beyan(hesaplanan_kdv: float, indirilecek_kdv: float) -> Dict[str, Any]:
    """KDV beyan sonucunu hesaplar."""
    odenmesi_gereken = hesaplanan_kdv - indirilecek_kdv
    return {
        "hesaplanan_kdv": round(hesaplanan_kdv, 2),
        "indirilecek_kdv": round(indirilecek_kdv, 2),
        "odenmesi_gereken": round(max(odenmesi_gereken, 0), 2),
        "devreden_kdv": round(abs(min(odenmesi_gereken, 0)), 2),
    }


def tam_vergi_hesapla(ozet: Dict[str, Any], mukellef_turu: str, yil: int = 2024) -> Dict[str, Any]:
    """
    Mizan özetinden tam vergi hesaplaması yapar.
    mukellef_turu: 'sahis' veya 'sirket'
    """
    donem_kari = max(ozet.get("donem_kari", 0), 0)
    net_satislar = ozet.get("net_satislar", 0)
    gecici_vergi_odendi = ozet.get("gecici_vergi", 0)

    sonuc = {
        "donem_kari": round(donem_kari, 2),
        "mukellef_turu": mukellef_turu,
        "yil": yil,
    }

    if mukellef_turu == "sahis":
        # Şahıs → Gelir Vergisi
        gv = hesapla_gelir_vergisi(donem_kari, yil)
        gecici = hesapla_gecici_vergi(donem_kari, gecici_vergi_odendi)
        sonuc["gelir_vergisi"] = gv
        sonuc["gecici_vergi"] = gecici
        sonuc["toplam_vergi_yuku"] = round(gv["vergi"], 2)
        sonuc["net_kar_vergi_sonrasi"] = round(donem_kari - gv["vergi"], 2)

    else:
        # Şirket → Kurumlar Vergisi
        kv = hesapla_kurumlar_vergisi(donem_kari, yil=yil)
        gecici = hesapla_gecici_vergi(donem_kari, gecici_vergi_odendi)

        # Asgari KV kontrolü (2024: hasılat × %10 ile karşılaştır)
        asgari_kv = net_satislar * ASGARI_KV_ORANI
        efektif_kv = max(kv["vergi"], asgari_kv)

        sonuc["kurumlar_vergisi"] = kv
        sonuc["asgari_kv"] = round(asgari_kv, 2)
        sonuc["asgari_kv_uygulanir"] = efektif_kv > kv["vergi"]
        sonuc["efektif_kv"] = round(efektif_kv, 2)
        sonuc["gecici_vergi"] = gecici
        sonuc["toplam_vergi_yuku"] = round(efektif_kv, 2)
        sonuc["net_kar_vergi_sonrasi"] = round(donem_kari - efektif_kv, 2)

    return sonuc
