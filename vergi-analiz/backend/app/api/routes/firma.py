from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.firma import Firma
from app.models.user import User
from app.schemas.firma import FirmaCreate, FirmaUpdate, FirmaResponse, FirmaListItem
from app.core.security import get_current_user

router = APIRouter(prefix="/api/firmalar", tags=["firmalar"])


@router.get("/", response_model=List[FirmaListItem])
def firma_listesi(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Firma).filter(Firma.user_id == current_user.id).all()


@router.post("/", response_model=FirmaResponse)
def firma_olustur(data: FirmaCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    mevcut = db.query(Firma).filter(Firma.vergi_no == data.vergi_no).first()
    if mevcut:
        raise HTTPException(status_code=400, detail="Bu vergi numarası zaten kayıtlı")
    firma = Firma(**data.model_dump(exclude_none=False), user_id=current_user.id)
    db.add(firma)
    db.commit()
    db.refresh(firma)
    return firma


@router.get("/{firma_id}", response_model=FirmaResponse)
def firma_detay(firma_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    firma = db.query(Firma).filter(Firma.id == firma_id, Firma.user_id == current_user.id).first()
    if not firma:
        raise HTTPException(status_code=404, detail="Firma bulunamadı")
    return firma


@router.put("/{firma_id}", response_model=FirmaResponse)
def firma_guncelle(firma_id: int, data: FirmaUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    firma = db.query(Firma).filter(Firma.id == firma_id, Firma.user_id == current_user.id).first()
    if not firma:
        raise HTTPException(status_code=404, detail="Firma bulunamadı")
    for key, val in data.model_dump(exclude_none=True).items():
        setattr(firma, key, val)
    db.commit()
    db.refresh(firma)
    return firma


@router.delete("/{firma_id}")
def firma_sil(firma_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    firma = db.query(Firma).filter(Firma.id == firma_id, Firma.user_id == current_user.id).first()
    if not firma:
        raise HTTPException(status_code=404, detail="Firma bulunamadı")
    db.delete(firma)
    db.commit()
    return {"mesaj": "Firma silindi"}
