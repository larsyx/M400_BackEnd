from pydantic import BaseModel, ConfigDict

from models.user import RuoloUtente

class UserDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    name: str
    role: RuoloUtente