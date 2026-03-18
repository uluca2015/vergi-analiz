from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine
from app.api.routes import auth, firma, mizan, rapor
import app.models.user  # noqa - register models
import app.models.firma  # noqa
import app.models.mizan  # noqa
import app.models.rapor  # noqa

# Tabloları oluştur
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Vergi & Finansal Analiz API",
    description="Türk vergi sistemi çerçevesinde vergi ve finansal analiz platformu",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Prod'da frontend URL ile sınırla
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(firma.router)
app.include_router(mizan.router)
app.include_router(rapor.router)


@app.get("/")
def root():
    return {"mesaj": "Vergi & Finansal Analiz API çalışıyor", "versiyon": "1.0.0"}


@app.get("/health")
def health():
    return {"durum": "sağlıklı"}
