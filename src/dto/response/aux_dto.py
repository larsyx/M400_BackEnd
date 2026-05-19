from pydantic import BaseModel

class AuxDTO(BaseModel):
    id: int
    name: str
    