from pydantic import BaseModel

from models.layout_channel import TypeChannel

class ChannelDTO(BaseModel):
    id: int
    name: str
    description: str = ''
    type: TypeChannel | None = None
    position: int | None = None