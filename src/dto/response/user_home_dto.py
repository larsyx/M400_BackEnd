from pydantic import BaseModel, Field

from dto.response.aux_dto import AuxDTO
from dto.response.fader_dto import FaderDTO
from dto.response.profile_dto import ProfileDTO

class UserHomeDTO(BaseModel):
    fader : list[FaderDTO]
    aux : list[AuxDTO]
    profile: list[ProfileDTO]
    aux_user: AuxDTO = Field(alias="auxUser")