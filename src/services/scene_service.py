from http.client import HTTPResponse
from fastapi import HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from dao.aux_dao import AuxDAO
from dao.partecipazione_scena_dao import PartecipazioneScenaDAO
from dao.scene_dao import SceneDAO
from dao.user_dao import UserDAO
from dao.layout_canale_dao import LayoutCanaleDAO
from dotenv import load_dotenv
from dto.request.admin_scene_dto import AdminSceneDTO
from dto.response.scene_dto import SceneDTO
from midi.midi_controller import MidiListener, call_type, MidiController
import json
from services.user_service import UserService
from settings import POST_NAME 

class SceneService:
    def __init__(self):
        self.scene_dao = SceneDAO()
        self.aux_dao = AuxDAO()
        self.user_dao = UserDAO()
        self.scene_partecipation_dao = PartecipazioneScenaDAO()
        self.layout_channel_dao = LayoutCanaleDAO()
        self.user_service = UserService()
        self._midiController = None

    @property
    def midiController(self):
        if self._midiController is None:
            self._midiController = MidiController()
        return self._midiController

    def get_scenes(self, user_id):
        if self.user_dao.is_admin(user_id):
            scenes = self.scene_dao.get_all_scenes()
            # remove default scene
            scenes = [scene for scene in scenes if scene.id != -1]

            return [AdminSceneDTO.model_validate(scene) for scene in scenes]
        else:    
            raise HTTPException(status_code=403, detail="Unauthorized")

    def get_scene_by_id(self, user_id, scene_id):
        if self.user_dao.is_admin(user_id):
            scene = self.scene_dao.get_scene_by_id(scene_id)

            return AdminSceneDTO.model_validate(scene)
        else:    
            raise HTTPException(status_code=403, detail="Unauthorized")

    def create_scene(self, user_id, scene):
        if self.user_dao.is_admin(user_id) == False:
            return HTTPException(status_code=403, detail="Non hai i permessi per accedere a questa risorsa")
        
        try:
            new_scene = self.scene_dao.create_scene(scene.name, scene.description)
            return SceneDTO.model_validate(new_scene)
        except Exception as e:
            print(f"Error creating scene: {e}")
            return False

    def update_scene(self, user_id, scene):
        if self.user_dao.is_admin(user_id) == False:
            return HTTPException(status_code=403, detail="Non hai i permessi per accedere a questa risorsa")

        self.scene_dao.update_scene(scene.id, scene.name, scene.description)

        partecipazioni_attuali = list(self.scene_partecipation_dao.get_participants_scene(scene.id))
        attuali_map = {p.user_username: p.aux_id for p in partecipazioni_attuali}
        nuovi_map = {p.username: p.aux_id for p in scene.scene_partecipation}

        for username in attuali_map.keys() - nuovi_map.keys():
            self.scene_partecipation_dao.remove_participants(scene.id, username)

        for username, aux_id in nuovi_map.items():
            if username not in attuali_map:
                self.scene_partecipation_dao.add_participants(scene.id, username, aux_id)
                self.user_service.set_default_layout(username, scene.id)
            elif attuali_map[username] != aux_id:
                self.scene_partecipation_dao.change_aux_user(scene.id, username, aux_id)

        return None

    def delete_scene(self, user_id, scene_id):
        if self.user_dao.is_admin(user_id) == False:
            return HTTPException(status_code=403, detail="Non hai i permessi per accedere a questa risorsa")

        try:
            self.scene_dao.delete_scene(scene_id)
            return True
            
        except Exception as e:
            print(f"Error retrieving all scenes: {e}")
            return False
        
    def get_all_user_scene(self, username):
        try:
            scenes = self.scene_dao.get_all_user_scene(username)

            return [SceneDTO.model_validate(s) for s in scenes]
        
        except Exception as e:
            print(f"Error retrieving all user scenes: {e}")
            return None