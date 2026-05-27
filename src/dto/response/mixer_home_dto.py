from pydantic import BaseModel

from dto.response.aux_dto import AuxDTO
from dto.response.fader_dto import FaderDTO

class MixerHomeDTO(BaseModel):
    dca : list[FaderDTO]
    fader : list[FaderDTO]
    aux : list[AuxDTO]