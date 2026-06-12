from pydantic import BaseModel
from typing import List

from dto.response.fader_dto import FaderDTO
from dto.response.profile_dto import ProfileDTO

class CreateProfileDTO(BaseModel):
    profile: ProfileDTO
    faders: List[FaderDTO]
