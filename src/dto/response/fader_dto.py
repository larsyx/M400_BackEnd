from pydantic import BaseModel

class FaderDTO(BaseModel):
    id: int
    name: str
    description: str = ''
    value: float
    switch: bool
    link: bool = False