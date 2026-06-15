from pydantic import BaseModel, ConfigDict, Field

class ScenePartecipantDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    aux_id: int = Field(alias="auxId")