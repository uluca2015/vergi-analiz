import openpyxl
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import io
import re


HESAP_GRUPLARI = {
    "1": "Dönen Varlıklar",
    "10": "Hazır Değerler",
    "100": "Kasa",
    "101": "Alınan Çekler",
    "102": "Bankalar",
    "103": "Verilen Çekler ve Ödeme Emirleri (-)",
    "108": "Diğer Hazır Değerler",
    "11": "Menkul Kıymetler",
    "12": "Ticari Alacaklar",
    "120": "Alıcılar",
    "121": "Alacak Senetleri",
    "126": "Verilen Depozito ve Teminatlar",
    "13": "Diğer Alacaklar",
    "15": "Stoklar",
    "150": "İlk Madde ve Malzeme",
    "151": "Yarı Mamuller",
    "152": "Mamuller",
    "153": "Ticari Mallar",
    "2": "Duran Varlıklar",
    "25": "Maddi Duran Varlıklar",
    "250": "Arazi ve Arsalar",
    "251": "Yeraltı ve Yerüstü Düzenleri",
    "252": "Binalar",
    "253": "Tesis, Makine ve Cihazlar",
    "254": "Taşıtlar",
    "255": "Demirbaşlar",
    "257": "Birikmiş Amortismanlar (-)",
    "26": "Maddi Olmayan Duran Varlıklar",
    "3": "Kısa Vadeli Yabancı Kaynaklar",
    "30": "Mali Borçlar",
    "300": "Banka Kredileri",
    "32": "Ticari Borçlar",
    "320": "Satıcılar",
    "321": "Borç Senetleri",
    "33": "Diğer Borçlar",
    "36": "Ödenecek Vergi ve Yükümlülükler",
    "360": "Ödenecek Vergi ve Fonlar",
    "361": "Ödenecek Sosyal Güvenlik Kesintileri",
    "368": "Vadesi Geçmiş Ertelenmiş veya Taksitlendirilmiş Vergi",
    "37": "Borç ve Gider Karşılıkları",
    "370": "Dönem Kârı Vergi ve Diğer Yasal Yükümlülük Karşılıkları",
    "371": "Dönem Kârının Peşin Ödenen Vergi ve Diğer Yükümlülükleri (-)",
    "4": "Uzun Vadeli Yabancı Kaynaklar",
    "40": "Mali Borçlar",
    "400": "Banka Kredileri",
    "5": "Özkaynaklar",
    "50": "Ödenmiş Sermaye",
    "500": "Sermaye",
    "570": "Geçmiş Yıllar Kârları",
    "580": "Geçmiş Yıllar Zararları (-)",
    "590": "Dönem Net Kârı",
    "591": "Dönem Net Zararı (-)",
    "6": "Gelir Tablosu",
    "60": "Brüt Satışlar",
    "600": "Yurt İçi Satışlar",
    "601": "Yurt Dışı Satışlar",
    "61": "Satış İndirimleri (-)",
    "610": "Satıştan İadeler (-)",
    "611": "Satış İskontoları (-)",
    "62": "Satışların Maliyeti (-)",
    "620": "Satılan Mamuller Maliyeti (-)",
    "621": "Satılan Ticari Mallar Maliyeti (-)",
    "622": "Satılan Hizmet Maliyeti (-)",
    "63": "Faaliyet Giderleri (-)",
    "630": "Araştırma ve Geliştirme Giderleri (-)",
    "631": "Pazarlama, Satış ve Dağıtım Giderleri (-)",
    "632": "Genel Yönetim Giderleri (-)",
    "64": "Diğer Faaliyetlerden Olağan Gelir ve Kârlar",
    "640": "İştiraklerden Temettü Gelirleri",
    "641": "Bağlı Ortaklıklardan Temettü Gelirleri",
    "642": "Faiz Gelirleri",
    "643": "Komisyon Gelirleri",
    "644": "Konusu Kalmayan Karşılıklar",
    "645": "Menkul Kıymet Satış Kârları",
    "646": "Kambiyo Kârları",
    "647": "Reeskont Faiz Gelirleri",
    "649": "Diğer Olağan Gelir ve Kârlar",
    "65": "Diğer Faaliyetlerden Olağan Gider ve Zararlar (-)",
    "653": "Komisyon Giderleri (-)",
    "654": "Karşılık Giderleri (-)",
    "655": "Menkul Kıymet Satış Zararları (-)",
    "656": "Kambiyo Zararları (-)",
    "657": "Reeskont Faiz Giderleri (-)",
    "659": "Diğer Olağan Gider ve Zararlar (-)",
    "66": "Finansman Giderleri (-)",
    "660": "Kısa Vadeli Borçlanma Giderleri (-)",
    "661": "Uzun Vadeli Borçlanma Giderleri (-)",
    "67": "Olağan Dışı Gelir ve Kârlar",
    "671": "Önceki Dönem Gelir ve Kârları",
    "679": "Diğer Olağan Dışı Gelir ve Kârlar",
    "68": "Olağan Dışı Gider ve Zararlar (-)",
    "680": "Çalışmayan Kısım Gider ve Zararları (-)",
    "681": "Önceki Dönem Gider ve Zararları (-)",
    "689": "Diğer Olağan Dışı Gider ve Zararlar (-)",
    "69": "Dönem Net Kârı veya Zararı",
    "690": "Dönem Kârı veya Zararı",
    "691": "Dönem Kârı Vergi ve Diğer Yasal Yükümlülük Karşılıkları (-)",
    "692": "Dönem Net Kârı veya Zararı",
    "7": "Maliyet Hesapları",
}


def normalize_number(val) -> float:
    if val is None or val == "":
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip().replace(" ", "").replace(".", "").replace(",", ".")
    s = re.sub(r"[^\d.\-]", "", s)
    try:
        return float(s) if s else 0.0
    except ValueError:
        return 0.0


def parse_excel_mizan(file_bytes: bytes, filename: str) -> Tuple[List[Dict], Dict[str, Any]]:
    """
    Excel mizanını okur. Farklı formatlara uyum sağlar.
    Döndürür: (kalemler_listesi, ozet_dict)
    """
    try:
        df = pd.read_excel(io.BytesIO(file_bytes), header=None, dtype=str)
    except Exception as e:
        raise ValueError(f"Excel dosyası okunamadı: {str(e)}")

    kalemleri = []
    header_row = None

    # Başlık satırını bul
    hesap_keywords = ["hesap kodu", "hesap no", "kod", "account"]
    for i, row in df.iterrows():
        row_lower = [str(c).lower().strip() for c in row if pd.notna(c)]
        if any(kw in " ".join(row_lower) for kw in hesap_keywords):
            header_row = i
            break

    if header_row is None:
        # Başlık bulunamadıysa ilk satırı dene
        header_row = 0

    df.columns = df.iloc[header_row]
    df = df.iloc[header_row + 1:].reset_index(drop=True)

    # Sütun eşlemesi
    col_map = {}
    for col in df.columns:
        col_str = str(col).lower().strip()
        if any(k in col_str for k in ["kod", "no", "code"]):
            col_map.setdefault("hesap_kodu", col)
        elif any(k in col_str for k in ["ad", "açıklama", "name", "description"]):
            col_map.setdefault("hesap_adi", col)
        elif "borç" in col_str and "bakiye" in col_str:
            col_map.setdefault("borc_bakiye", col)
        elif "alacak" in col_str and "bakiye" in col_str:
            col_map.setdefault("alacak_bakiye", col)
        elif "borç" in col_str and "hareket" in col_str:
            col_map.setdefault("borc_hareket", col)
        elif "alacak" in col_str and "hareket" in col_str:
            col_map.setdefault("alacak_hareket", col)
        elif "borç" in col_str:
            col_map.setdefault("borc_bakiye", col)
        elif "alacak" in col_str:
            col_map.setdefault("alacak_bakiye", col)

    for _, row in df.iterrows():
        hesap_kodu = str(row.get(col_map.get("hesap_kodu", ""), "")).strip()
        if not hesap_kodu or hesap_kodu in ["nan", "None", ""]:
            continue
        # Sayısal olmayan satırları atla (ara toplam başlıkları)
        if not re.match(r"^\d+", hesap_kodu):
            continue

        hesap_adi = str(row.get(col_map.get("hesap_adi", ""), "")).strip()
        if not hesap_adi or hesap_adi == "nan":
            hesap_adi = HESAP_GRUPLARI.get(hesap_kodu, f"Hesap {hesap_kodu}")

        kalem = {
            "hesap_kodu": hesap_kodu,
            "hesap_adi": hesap_adi,
            "borc_bakiye": normalize_number(row.get(col_map.get("borc_bakiye"))),
            "alacak_bakiye": normalize_number(row.get(col_map.get("alacak_bakiye"))),
            "borc_hareket": normalize_number(row.get(col_map.get("borc_hareket"), 0)),
            "alacak_hareket": normalize_number(row.get(col_map.get("alacak_hareket"), 0)),
        }
        kalemleri.append(kalem)

    ozet = _hesapla_ozet(kalemleri)
    return kalemleri, ozet


def _hesapla_ozet(kalemleri: List[Dict]) -> Dict[str, Any]:
    """Mizan kalemlerinden özet finansal veriler hesaplar."""
    ozet = {
        "toplam_borc": 0, "toplam_alacak": 0,
        "donen_varliklar": 0, "duran_varliklar": 0,
        "kvyk": 0, "uvyk": 0, "ozkaynak": 0,
        "net_satislar": 0, "satislar_maliyeti": 0,
        "brut_kar": 0, "faaliyet_giderleri": 0,
        "faaliyet_kari": 0, "finansman_giderleri": 0,
        "donem_kari": 0,
        "kasa_banka": 0, "alicilar": 0, "stoklar": 0,
        "saticiler": 0, "banka_kredileri_kv": 0,
        "vergi_karsiligi": 0, "gecici_vergi": 0,
    }

    for k in kalemleri:
        kod = k["hesap_kodu"]
        borc = k["borc_bakiye"]
        alacak = k["alacak_bakiye"]
        net = borc - alacak  # Borç bakiye = aktif

        ozet["toplam_borc"] += borc
        ozet["toplam_alacak"] += alacak

        # Aktif
        if kod.startswith("1"):
            ozet["donen_varliklar"] += net
        if kod.startswith("2"):
            ozet["duran_varliklar"] += net

        # Pasif
        if kod.startswith("3"):
            ozet["kvyk"] += (alacak - borc)
        if kod.startswith("4"):
            ozet["uvyk"] += (alacak - borc)
        if kod.startswith("5"):
            ozet["ozkaynak"] += (alacak - borc)

        # Gelir tablosu
        if kod.startswith("60"):
            ozet["net_satislar"] += (alacak - borc)
        if kod.startswith("61"):
            ozet["net_satislar"] -= (alacak - borc)  # İndirimler
        if kod.startswith("62"):
            ozet["satislar_maliyeti"] += (alacak - borc)
        if kod.startswith("63"):
            ozet["faaliyet_giderleri"] += (alacak - borc)
        if kod.startswith("66"):
            ozet["finansman_giderleri"] += (alacak - borc)

        # Özel hesaplar
        if kod in ["100", "101", "102"]:
            ozet["kasa_banka"] += net
        if kod.startswith("120"):
            ozet["alicilar"] += net
        if kod.startswith("15"):
            ozet["stoklar"] += net
        if kod.startswith("320"):
            ozet["saticiler"] += (alacak - borc)
        if kod == "300":
            ozet["banka_kredileri_kv"] += (alacak - borc)
        if kod == "370":
            ozet["vergi_karsiligi"] += (alacak - borc)
        if kod == "371":
            ozet["gecici_vergi"] += net

    ozet["brut_kar"] = ozet["net_satislar"] - ozet["satislar_maliyeti"]
    ozet["faaliyet_kari"] = ozet["brut_kar"] - ozet["faaliyet_giderleri"]
    ozet["donem_kari"] = ozet["faaliyet_kari"] - ozet["finansman_giderleri"]

    # Toplam aktif = pasif kontrolü
    ozet["toplam_aktif"] = ozet["donen_varliklar"] + ozet["duran_varliklar"]
    ozet["toplam_pasif"] = ozet["kvyk"] + ozet["uvyk"] + ozet["ozkaynak"]

    return ozet
