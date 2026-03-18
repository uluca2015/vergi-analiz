from typing import Dict, Any, List


def hesapla_finansal_oranlar(ozet: Dict[str, Any]) -> Dict[str, Any]:
    """Temel finansal oranları hesaplar."""

    def safe_div(a, b):
        return round(a / b, 4) if b and b != 0 else None

    dv = ozet.get("donen_varliklar", 0)
    duran_v = ozet.get("duran_varliklar", 0)
    kvyk = ozet.get("kvyk", 0)
    uvyk = ozet.get("uvyk", 0)
    ozkaynak = ozet.get("ozkaynak", 0)
    toplam_aktif = ozet.get("toplam_aktif", dv + duran_v)
    toplam_pasif = kvyk + uvyk + ozkaynak
    net_satislar = ozet.get("net_satislar", 0)
    brut_kar = ozet.get("brut_kar", 0)
    faaliyet_kari = ozet.get("faaliyet_kari", 0)
    donem_kari = ozet.get("donem_kari", 0)
    kasa_banka = ozet.get("kasa_banka", 0)
    alicilar = ozet.get("alicilar", 0)
    stoklar = ozet.get("stoklar", 0)
    saticiler = ozet.get("saticiler", 0)
    fin_gid = ozet.get("finansman_giderleri", 0)

    oranlar = {}

    # LİKİDİTE ORANLARI
    oranlar["cari_oran"] = safe_div(dv, kvyk)
    oranlar["asit_test_orani"] = safe_div(dv - stoklar, kvyk)
    oranlar["nakit_orani"] = safe_div(kasa_banka, kvyk)

    # FİNANSAL YAPI ORANLARI
    toplam_borc = kvyk + uvyk
    oranlar["borc_oz_kaynak"] = safe_div(toplam_borc, ozkaynak)
    oranlar["finansal_kaldiraci"] = safe_div(toplam_aktif, ozkaynak)
    oranlar["oz_kaynak_orani"] = safe_div(ozkaynak, toplam_aktif)
    oranlar["borc_orani"] = safe_div(toplam_borc, toplam_aktif)

    # KÂRLILIK ORANLARI
    oranlar["brut_kar_marji"] = safe_div(brut_kar, net_satislar)
    oranlar["faaliyet_kar_marji"] = safe_div(faaliyet_kari, net_satislar)
    oranlar["net_kar_marji"] = safe_div(donem_kari, net_satislar)
    oranlar["aktif_karlilik"] = safe_div(donem_kari, toplam_aktif)
    oranlar["oz_kaynak_karlilik"] = safe_div(donem_kari, ozkaynak)

    # AKTİVİTE ORANLARI
    oranlar["alacak_devir_hizi"] = safe_div(net_satislar, alicilar)
    oranlar["stok_devir_hizi"] = safe_div(ozet.get("satislar_maliyeti", 0), stoklar)
    oranlar["aktif_devir_hizi"] = safe_div(net_satislar, toplam_aktif)

    # FAİZ KARŞILAMA
    ebitda = faaliyet_kari + fin_gid  # Basit yaklaşım
    oranlar["faiz_karsilama"] = safe_div(ebitda, fin_gid) if fin_gid > 0 else None

    # Oranlara yorum ekle
    oranlar["yorumlar"] = _oran_yorumla(oranlar)

    return oranlar


def _oran_yorumla(oranlar: Dict) -> List[Dict]:
    yorumlar = []

    cari = oranlar.get("cari_oran")
    if cari is not None:
        if cari >= 2:
            durum, mesaj = "iyi", f"Cari oran {cari:.2f} — güçlü likidite"
        elif cari >= 1:
            durum, mesaj = "orta", f"Cari oran {cari:.2f} — yeterli ancak takip edilmeli"
        else:
            durum, mesaj = "kotu", f"Cari oran {cari:.2f} — kısa vadeli ödeme güçlüğü riski"
        yorumlar.append({"oran": "cari_oran", "durum": durum, "mesaj": mesaj})

    boz = oranlar.get("borc_oz_kaynak")
    if boz is not None:
        if boz <= 1:
            durum, mesaj = "iyi", f"Borç/Özkaynak {boz:.2f} — dengeli finansman"
        elif boz <= 2:
            durum, mesaj = "orta", f"Borç/Özkaynak {boz:.2f} — yüksek finansal kaldıraç"
        else:
            durum, mesaj = "kotu", f"Borç/Özkaynak {boz:.2f} — aşırı borçluluk riski"
        yorumlar.append({"oran": "borc_oz_kaynak", "durum": durum, "mesaj": mesaj})

    nkm = oranlar.get("net_kar_marji")
    if nkm is not None:
        if nkm >= 0.10:
            durum, mesaj = "iyi", f"Net kâr marjı %{nkm*100:.1f} — yüksek kârlılık"
        elif nkm >= 0:
            durum, mesaj = "orta", f"Net kâr marjı %{nkm*100:.1f} — düşük marj"
        else:
            durum, mesaj = "kotu", f"Net kâr marjı %{nkm*100:.1f} — zarar durumu"
        yorumlar.append({"oran": "net_kar_marji", "durum": durum, "mesaj": mesaj})

    return yorumlar


def hesapla_vergi_risk_skoru(ozet: Dict, vergi_hesap: Dict, oranlar: Dict) -> Dict[str, Any]:
    """
    Vergi inceleme riskini 0-100 arası skorla.
    Risk faktörleri: matrah düşüklüğü, brüt kâr marjı, aktifler vs beyan, finansman giderleri.
    """
    riskler = []
    toplam_skor = 0

    net_satislar = ozet.get("net_satislar", 0)
    brut_kar_marji = oranlar.get("brut_kar_marji")
    net_kar_marji = oranlar.get("net_kar_marji")
    fin_gid = ozet.get("finansman_giderleri", 0)
    donem_kari = ozet.get("donem_kari", 0)

    # Risk 1: Brüt kâr marjı sektör ortalamasının altında mı?
    if brut_kar_marji is not None:
        if brut_kar_marji < 0.05:
            skor = 25
            riskler.append({
                "kategori": "Brüt Kâr Marjı",
                "risk": "Yüksek",
                "skor": skor,
                "aciklama": f"Brüt kâr marjı %{brut_kar_marji*100:.1f} — sektör ortalamasının belirgin altında. İnceleme riski yüksek.",
                "oneri": "Maliyet kalemlerini dokümante edin, transfer fiyatlandırması varsa raporlayın."
            })
            toplam_skor += skor
        elif brut_kar_marji < 0.15:
            skor = 10
            riskler.append({
                "kategori": "Brüt Kâr Marjı",
                "risk": "Orta",
                "skor": skor,
                "aciklama": f"Brüt kâr marjı %{brut_kar_marji*100:.1f} — dikkat çekici düzeyde düşük.",
                "oneri": "Maliyet belgelerini düzenli tutun."
            })
            toplam_skor += skor

    # Risk 2: Yüksek finansman giderleri
    if net_satislar > 0 and fin_gid > 0:
        fin_oran = fin_gid / net_satislar
        if fin_oran > 0.10:
            skor = 20
            riskler.append({
                "kategori": "Finansman Giderleri",
                "risk": "Yüksek",
                "skor": skor,
                "aciklama": f"Finansman giderleri cironun %{fin_oran*100:.1f}'i — örtülü kazanç aktarımı riski.",
                "oneri": "Kredi belgelerini ve faiz oranlarının emsallerine uygunluğunu kontrol edin."
            })
            toplam_skor += skor

    # Risk 3: Dönem kârı negatif / sıfır
    if donem_kari <= 0:
        skor = 15
        riskler.append({
            "kategori": "Dönem Kârı",
            "risk": "Orta",
            "skor": skor,
            "aciklama": "Dönem kârı sıfır veya negatif — sürekli zarar beyanı inceleme riski taşır.",
            "oneri": "Zararın gerçek ticari gerekçesi belgelenmelidir."
        })
        toplam_skor += skor

    # Risk 4: Asgari KV uygulanabilirliği
    if vergi_hesap.get("asgari_kv_uygulanir"):
        skor = 15
        riskler.append({
            "kategori": "Asgari Kurumlar Vergisi",
            "risk": "Orta",
            "skor": skor,
            "aciklama": "Hasılat üzerinden hesaplanan asgari KV, beyan edilecek KV'den yüksek.",
            "oneri": "2024'ten itibaren geçerli asgari KV (%10 hasılat) dikkate alınmalıdır."
        })
        toplam_skor += skor

    # Risk 5: Borç/Özkaynak dengesi
    boz = oranlar.get("borc_oz_kaynak")
    if boz and boz > 3:
        skor = 15
        riskler.append({
            "kategori": "Örtülü Sermaye",
            "risk": "Yüksek",
            "skor": skor,
            "aciklama": f"Borç/Özkaynak oranı {boz:.2f} — KVK md. 12 örtülü sermaye sınırı (3x) aşılmış.",
            "oneri": "Ortaklardan alınan borçların örtülü sermaye kapsamında değerlendirilip değerlendirilmediğini inceleyin."
        })
        toplam_skor += skor

    final_skor = min(toplam_skor, 100)

    if final_skor >= 60:
        risk_seviyesi = "YÜKSEK"
    elif final_skor >= 30:
        risk_seviyesi = "ORTA"
    else:
        risk_seviyesi = "DÜŞÜK"

    return {
        "skor": final_skor,
        "seviye": risk_seviyesi,
        "riskler": riskler,
        "risk_sayisi": len(riskler),
    }


def hesapla_kredi_uygunluk(ozet: Dict, oranlar: Dict) -> Dict[str, Any]:
    """Banka kredi değerlendirme kriterleri (Basel III uyumlu)."""
    kriterler = []
    toplam_puan = 0
    max_puan = 0

    def ekle_kriter(ad, deger, esik_iyi, esik_orta, agirlik, yorum_iyi, yorum_orta, yorum_kotu, birim=""):
        nonlocal toplam_puan, max_puan
        max_puan += agirlik
        if deger is None:
            kriterler.append({"kriter": ad, "deger": "Hesaplanamadı", "puan": 0, "durum": "bilinmiyor"})
            return
        if deger >= esik_iyi:
            puan, durum, yorum = agirlik, "iyi", yorum_iyi
        elif deger >= esik_orta:
            puan, durum, yorum = agirlik * 0.5, "orta", yorum_orta
        else:
            puan, durum, yorum = 0, "kotu", yorum_kotu
        toplam_puan += puan
        kriterler.append({
            "kriter": ad,
            "deger": f"{deger:.2f}{birim}",
            "puan": puan,
            "max_puan": agirlik,
            "durum": durum,
            "yorum": yorum,
        })

    ekle_kriter(
        "Cari Oran", oranlar.get("cari_oran"),
        2.0, 1.2, 20,
        "Güçlü likidite — kısa vadeli borç ödeme kapasitesi iyi.",
        "Yeterli likidite — yakından takip edilmeli.",
        "Zayıf likidite — kısa vadeli kredi riski yüksek."
    )
    ekle_kriter(
        "Borç/Özkaynak", oranlar.get("borc_oz_kaynak"),
        0, 2.0, 20,
        "Çok yüksek kaldıraç.",  # Ters mantık — düşük iyi
        "Orta kaldıraç.",
        "Düşük borçluluk — güçlü özkaynak yapısı.",
        # Burada ters skor mantığı uygulayacağız
    )
    ekle_kriter(
        "Net Kâr Marjı", oranlar.get("net_kar_marji"),
        0.10, 0.03, 20,
        "Yüksek kârlılık — borç geri ödeme kapasitesi güçlü.",
        "Düşük kârlılık — dikkatli değerlendirilmeli.",
        "Zarar durumu — kredi için risk oluşturuyor.", "%"
    )
    ekle_kriter(
        "Faiz Karşılama", oranlar.get("faiz_karsilama"),
        3.0, 1.5, 20,
        "Faiz yükü rahatça karşılanıyor.",
        "Faiz karşılama sınırda.",
        "Faiz ödeme güçlüğü riski var."
    )
    ekle_kriter(
        "Özkaynak Oranı", oranlar.get("oz_kaynak_orani"),
        0.40, 0.20, 20,
        "Güçlü özkaynak yapısı.",
        "Orta özkaynak — ek teminat gerekebilir.",
        "Zayıf özkaynak — kredi güvenilirliği düşük.", "%"
    )

    uygunluk_skoru = (toplam_puan / max_puan * 100) if max_puan > 0 else 0

    if uygunluk_skoru >= 70:
        sonuc = "UYGUN"
        sonuc_aciklama = "Mali tablolar banka kredi değerlendirmesi için genel olarak olumlu görünüyor."
    elif uygunluk_skoru >= 40:
        sonuc = "KOŞULLU UYGUN"
        sonuc_aciklama = "Bazı zayıf noktalar var — ek teminat veya düzeltici önlemler gerekebilir."
    else:
        sonuc = "UYGUN DEĞİL"
        sonuc_aciklama = "Mevcut finansal tablo ile kredi başvurusu reddedilebilir. İyileştirici önlemler alınmalı."

    return {
        "skor": round(uygunluk_skoru, 1),
        "sonuc": sonuc,
        "sonuc_aciklama": sonuc_aciklama,
        "kriterler": kriterler,
    }
