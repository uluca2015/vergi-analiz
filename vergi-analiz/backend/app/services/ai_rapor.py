import anthropic
from typing import Dict, Any
from app.core.config import settings


def _build_prompt(firma_bilgi: Dict, vergi: Dict, oranlar: Dict, risk: Dict, kredi: Dict) -> str:
    return f"""Sen Türk vergi hukuku ve muhasebe alanında uzman bir mali müşavirsin. 
Aşağıdaki firma ve mali analiz verilerine dayanarak kapsamlı bir rapor hazırla.

## FİRMA BİLGİLERİ
- Unvan: {firma_bilgi.get('unvan')}
- Tür: {firma_bilgi.get('mukellef_turu')} / {firma_bilgi.get('sirket_turu', '-')}
- Vergi No: {firma_bilgi.get('vergi_no')}
- Vergi Dairesi: {firma_bilgi.get('vergi_dairesi')}

## VERGİ HESAPLAMALARI
- Dönem Kârı: {vergi.get('donem_kari', 0):,.2f} TL
- Vergi Yükü: {vergi.get('toplam_vergi_yuku', 0):,.2f} TL
- Net Kâr (vergi sonrası): {vergi.get('net_kar_vergi_sonrasi', 0):,.2f} TL
{f"- Asgari KV Uygulanır: EVET" if vergi.get('asgari_kv_uygulanir') else ""}

## FİNANSAL ORANLAR
- Cari Oran: {oranlar.get('cari_oran', 'N/A')}
- Borç/Özkaynak: {oranlar.get('borc_oz_kaynak', 'N/A')}
- Net Kâr Marjı: {oranlar.get('net_kar_marji', 'N/A')}
- Özkaynak Kârlılığı: {oranlar.get('oz_kaynak_karlilik', 'N/A')}

## VERGİ RİSK ANALİZİ
- Risk Skoru: {risk.get('skor')}/100 — {risk.get('seviye')}
- Tespit Edilen Riskler:
{chr(10).join([f"  * {r['kategori']}: {r['aciklama']}" for r in risk.get('riskler', [])])}

## KREDİ UYGUNLUK
- Skor: {kredi.get('skor')}/100 — {kredi.get('sonuc')}
- Değerlendirme: {kredi.get('sonuc_aciklama')}

---

Lütfen şu başlıkları içeren Türkçe bir rapor yaz:

1. **YÖNETİCİ ÖZETİ** (3-4 cümle)
2. **VERGİ ANALİZİ VE RİSKLER** — tespit edilen vergi riskleri, yasal dayanak (GVK/KVK madde numaraları) ve acil önlemler
3. **FİNANSAL DURUM DEĞERLENDİRMESİ** — güçlü ve zayıf yönler
4. **KREDİ BAŞVURUSU ÖNCESİ YAPILMASI GEREKENLER** — somut, uygulanabilir adımlar
5. **VERGİ PLANLAMASI ÖNERİLERİ** — yasal vergi optimizasyonu fırsatları
6. **SONUÇ VE ACİL EYLEMLER** — öncelik sırasına göre

Raporun dili açık, anlaşılır ve uygulamaya yönelik olsun. Teknik terimleri Türkçe açıklamalarla destekle."""


async def generate_ai_rapor(
    firma_bilgi: Dict,
    vergi: Dict,
    oranlar: Dict,
    risk: Dict,
    kredi: Dict,
) -> Dict[str, str]:
    """Claude API ile AI destekli rapor üretir."""
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    prompt = _build_prompt(firma_bilgi, vergi, oranlar, risk, kredi)

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        rapor_metni = message.content[0].text

        # Kısa öneri listesi de üret
        oneri_prompt = f"""Aynı firma için 5 maddelik kısa aksiyon listesi yap:
Firma: {firma_bilgi.get('unvan')}, Risk: {risk.get('seviye')}, Kredi: {kredi.get('sonuc')}
Her madde tek satır, başında numara olsun. Sadece listeyi yaz, başlık ekleme."""

        oneri_msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            messages=[{"role": "user", "content": oneri_prompt}]
        )
        oneriler = oneri_msg.content[0].text

        return {"rapor": rapor_metni, "oneriler": oneriler, "hata": None}

    except Exception as e:
        return {
            "rapor": "AI raporu oluşturulamadı. Lütfen tekrar deneyin.",
            "oneriler": "",
            "hata": str(e)
        }
