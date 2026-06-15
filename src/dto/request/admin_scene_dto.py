from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from dto.request.scene_partecipant_dto import ScenePartecipantDTO


class AdminSceneDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    scene_partecipation: list[ScenePartecipantDTO] = Field(
        validation_alias=AliasChoices("scene_participation", "ScenePartecipant"),
        alias="ScenePartecipant",
    )