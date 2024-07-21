from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import uuid
from sqlalchemy.orm import Session
from database import engine, get_db
from models.sqlalchemy_models import EngineModel, Base
from kafka_client import send_message

app = FastAPI()

Base.metadata.create_all(bind=engine)


class Configuration(BaseModel):
    specification: dict
    settings: dict


class Engine(BaseModel):
    kind: str
    name: str
    version: str
    description: str
    configuration: Configuration

    class Config:
        orm_mode = True


@app.post("/engine/")
def create_engine(engine: Engine, db: Session = Depends(get_db)):
    engine_id = str(uuid.uuid4())
    db_engine = EngineModel(
        id=engine_id,
        kind=engine.kind,
        name=engine.name,
        version=engine.version,
        description=engine.description,
        json=engine.configuration.dict()
    )
    db.add(db_engine)
    db.commit()
    db.refresh(db_engine)
    send_message({"id": engine_id, "engine": engine.dict()})
    return {"id": engine_id}


@app.get("/engine/{engine_id}")
def read_engine(engine_id: str, db: Session = Depends(get_db)):
    db_engine = db.query(EngineModel).filter(EngineModel.id == engine_id).first()
    if db_engine is None:
        raise HTTPException(status_code=404, detail="Engine not found")
    return db_engine


@app.put("/engine/{engine_id}/configuration/")
def update_configuration(engine_id: str, config: Configuration, db: Session = Depends(get_db)):
    db_engine = db.query(EngineModel).filter(EngineModel.id == engine_id).first()
    if db_engine is None:
        raise HTTPException(status_code=404, detail="Engine not found")
    db_engine.configuration = config.dict()
    db.commit()
    db.refresh(db_engine)
    send_message({"id": engine_id, "configuration": config.dict()})
    return db_engine


@app.put("/engine/{engine_id}/settings/")
def update_settings(engine_id: str, settings: dict, db: Session = Depends(get_db)):
    db_engine = db.query(EngineModel).filter(EngineModel.id == engine_id).first()
    if db_engine is None:
        raise HTTPException(status_code=404, detail="Engine not found")
    db_engine.configuration["settings"] = settings
    db.commit()
    db.refresh(db_engine)
    send_message({"id": engine_id, "settings": settings})
    return db_engine


@app.delete("/engine/{engine_id}/")
def delete_engine(engine_id: str, db: Session = Depends(get_db)):
    db_engine = db.query(EngineModel).filter(EngineModel.id == engine_id).first()
    if db_engine is None:
        raise HTTPException(status_code=404, detail="Engine not found")
    db.delete(db_engine)
    db.commit()
    send_message({"id": engine_id, "action": "delete"})
    return {"detail": "Engine deleted"}


@app.get("/engine/{engine_id}/state")
def get_engine_state(engine_id: str, db: Session = Depends(get_db)):
    db_engine = db.query(EngineModel).filter(EngineModel.id == engine_id).first()
    if db_engine is None:
        raise HTTPException(status_code=404, detail="Engine not found")
    return {"state": "active"}
