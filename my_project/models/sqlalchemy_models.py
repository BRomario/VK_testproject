from sqlalchemy import Column, String, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class EngineState(enum.Enum):
    NEW = "NEW"
    INSTALLING = "INSTALLING"
    RUNNING = "RUNNING"


class EngineModel(Base):
    __tablename__ = "apps"

    id = Column(String, primary_key=True, index=True)
    kind = Column(String, index=True)
    name = Column(String, index=True)
    version = Column(String)
    description = Column(String)
    state = Column(Enum(EngineState), default=EngineState.NEW)
    json = Column(JSON)
