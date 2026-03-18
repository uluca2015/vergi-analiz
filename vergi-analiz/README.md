# Vergi & Finansal Analiz Platformu

Türk vergi sistemi çerçevesinde vergi hesaplama, risk analizi, finansal analiz ve kredi uygunluk raporlaması yapan tam yığın web uygulaması.

## Özellikler

- **Firma Yönetimi** — Şahıs / şirket kaydı (A.Ş., Ltd., vb.), vergi no, vergi dairesi, ticaret sicil bilgileri
- **Mizan Yükleme** — Excel (.xlsx) mizan dosyası yükleme ve otomatik ayrıştırma
- **Vergi Hesaplama** — Gelir Vergisi (GVK md. 103 dilimleri), Kurumlar Vergisi (%25), Asgari KV, Geçici Vergi
- **Mali Tablolar** — Bilanço ve gelir tablosu otomatik oluşturma
- **Finansal Analiz** — Cari oran, borç/özkaynak, kârlılık, aktivite oranları
- **Vergi Risk Skoru** — Brüt kâr marjı, finansman giderleri, örtülü sermaye, asgari KV riski
- **Kredi Uygunluk Analizi** — Basel III kriterleri (cari oran, faiz karşılama, özkaynak oranı)
- **AI Rapor** — Claude Haiku ile Türkçe analiz raporu ve aksiyon önerileri

## Teknoloji Yığını

| Katman | Teknoloji |
|--------|-----------|
| Backend | Python 3.11 + FastAPI + SQLAlchemy |
| Veritabanı | PostgreSQL |
| Frontend | React 18 + Vite + Tailwind CSS |
| AI | Anthropic Claude API (claude-haiku-4-5) |
| Deploy | Render.com |

---

## Yerel Geliştirme Ortamı

### Gereksinimler
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

### 1. Repo'yu klonla

```bash
git clone https://github.com/KULLANICI_ADI/vergi-analiz.git
cd vergi-analiz
```

### 2. Backend kurulumu

```bash
cd backend
python -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# .env içine DATABASE_URL, SECRET_KEY ve ANTHROPIC_API_KEY ekle
```

`.env` örneği:
```
DATABASE_URL=postgresql://postgres:sifre@localhost:5432/vergi_analiz
SECRET_KEY=cok-gizli-bir-anahtar-degistir
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
```

### 3. Veritabanı

```bash
psql -U postgres -c "CREATE DATABASE vergi_analiz;"
# Tablolar ilk çalıştırmada otomatik oluşur
```

### 4. Backend başlat

```bash
uvicorn app.main:app --reload --port 8000
# API Docs: http://localhost:8000/docs
```

### 5. Frontend başlat

```bash
cd ../frontend
npm install
npm run dev
# http://localhost:5173
```

---

## Render.com Deploy

1. GitHub'a push et
2. Render Dashboard → **New Blueprint** → Repoyu seç
3. `render.yaml` otomatik algılanır
4. **ANTHROPIC_API_KEY** environment variable ekle
5. **Apply** → ~5 dakikada deploy tamamlanır

---

## Proje Yapısı

```
vergi-analiz/
├── backend/
│   ├── app/
│   │   ├── api/routes/      # auth, firma, mizan, rapor
│   │   ├── core/            # config, security (JWT)
│   │   ├── db/              # SQLAlchemy session
│   │   ├── models/          # User, Firma, Mizan, Rapor
│   │   ├── schemas/         # Pydantic şemaları
│   │   ├── services/        # mizan_parser, vergi_hesaplama,
│   │   │                    #   finansal_analiz, ai_rapor
│   │   └── main.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── src/
│       ├── pages/           # Login, Dashboard, Firma, Mizan, Rapor
│       ├── components/ui/   # Layout, Sidebar
│       ├── store/           # Zustand auth store
│       └── utils/           # Axios API client
├── render.yaml
└── README.md
```

---

## Vergi Hesaplama (2024)

**Gelir Vergisi Tarifeleri:**
| Dilim | Oran |
|-------|------|
| 0 – 110.000 TL | %15 |
| 110.001 – 230.000 TL | %20 |
| 230.001 – 580.000 TL | %27 |
| 580.001 – 3.000.000 TL | %35 |
| 3.000.001+ TL | %40 |

**Kurumlar Vergisi:** %25 (borsada işlem gören: %20)  
**Asgari KV:** Hasılat × %10  
**Geçici Vergi:** %25 (3 aylık dönemler)

---

## API Uç Noktaları

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| POST | `/api/auth/register` | Kayıt |
| POST | `/api/auth/login` | Giriş (JWT) |
| GET/POST | `/api/firmalar/` | Firma listesi / ekle |
| GET/PUT/DELETE | `/api/firmalar/{id}` | Firma detay / güncelle / sil |
| POST | `/api/mizanlar/yukle/{firma_id}` | Excel mizan yükle |
| GET | `/api/mizanlar/{id}` | Mizan detay |
| POST | `/api/raporlar/olustur/{mizan_id}` | Tam rapor üret (AI dahil) |
| GET | `/api/raporlar/{id}` | Rapor detay |

---

## Lisans
MIT
