from pydantic import BaseModel

from models.layout_channel import TypeChannel

class ChannelLayoutDTO(BaseModel):
    channel_id: int
    name: str
    description: str = ''
    position: int = -1
    type: TypeChannel | None = None
    selected: bool = False