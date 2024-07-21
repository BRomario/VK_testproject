from pydantic import BaseModel
from typing import Dict, Any


class Engine(BaseModel):
    kind: str
    name: str
    version: str
    description: str
    state: str = "NEW"
    json: Dict[str, Any]

    class Config:
        orm_mode = True
