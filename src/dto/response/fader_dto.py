from pydantic import BaseModel

from models.layout_channel import TypeChannel

class FaderDTO(BaseModel):
    id: int
    name: str
    description: str = ''
    value: float
    switch: bool
    link: bool = False
    type: TypeChannel | None = None