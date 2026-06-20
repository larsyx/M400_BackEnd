from fastapi import HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dao.layout_canale_dao import LayoutCanaleDAO
from dto.request.user_dto import UserDTO
from dto.response.channel_dto import ChannelDTO
from dto.response.channel_layout_dto import ChannelLayoutDTO
from models.user import RuoloUtente
from dao.channel_dao import ChannelDAO
from dao.scene_dao import SceneDAO
from dao.user_dao import UserDAO
from dao.dca_dao import DCA_DAO
from dao.partecipazione_scena_dao import PartecipazioneScenaDAO
from fastapi.responses import RedirectResponse
import os
import json

from services.aux_service import AuxService

class AdminService:
    def __init__(self):
        self.user_dao = UserDAO()
        self.scene_dao = SceneDAO()
        self.channel_dao = ChannelDAO()
        self.dca_dao = DCA_DAO()
        self.scene_partecipation_dao = PartecipazioneScenaDAO()
        self.layout_channel_dao = LayoutCanaleDAO()
        self.aux_service = AuxService()

    # Users
    def get_users(self, user_id):
        users = self.user_dao.get_all_users()
        return [UserDTO.model_validate(user) for user in users]  
 
    def create_user(self, user_id, user):
        try:
            if self.user_dao.is_admin(user_id):
                if not self.user_dao.get_user_by_username(user.username):
                    new_user = self.user_dao.create_user(username=user.username, nome=user.name, ruolo=user.role)
                    return UserDTO.model_validate(new_user)
                else: 
                    return "Errore utente già presente"

            else:
                return HTTPException(status_code=403, detail="Non hai i permessi per accedere a questa risorsa")
            
        except Exception as e:
            print(f"Error creating user: {e}")
            return HTTPException(status_code=403, detail="Non hai i permessi per accedere a questa risorsa")

    def update_user(self, user_id, old_username, user):
        try:
            if self.user_dao.is_admin(user_id):
                new_user = self.user_dao.update_user(old_username=old_username, username=user.username, name=user.name, role=user.role)
                return UserDTO.model_validate(new_user)
            else:
                return HTTPException(status_code=403, detail="Non hai i permessi per accedere a questa risorsa")
        except Exception as e:
            print(f"Error creating user: {e}")
            return HTTPException(status_code=403, detail="Non hai i permessi per accedere a questa risorsa")

    def delete_user(self, user_id, username):
        try:
            if self.user_dao.is_admin(user_id):
                self.user_dao.delete_user(username)
                return True
            else:
                return HTTPException(status_code=403, content="Non hai i permessi per accedere a questa risorsa")
        except Exception as e:
            print(f"Error deleting user: {e}")
            return HTTPException(status_code=403, content="Non hai i permessi per accedere a questa risorsa")

    # channel 
    def load_channels(self, user):
        try:
            if self.user_dao.is_admin(user) or self.user_dao.is_mixer(user):
                channels = self.channel_dao.get_all_channels()
                return [ChannelDTO(id=ch.id, name=ch.name, description= ch.description if ch.description else '' , type=ch.type_channel, position=ch.position) for ch in channels]
            else:
                return HTTPException(status_code=403, detail="Non hai i permessi per accedere a questa risorsa")
        except Exception as e:
            print(f"Error loading manage channels: {e}")
            return None

    def set_channel(self, user, channels):
        try:
            if self.user_dao.is_admin(user) or self.user_dao.is_mixer(user):
                for channel in channels:
                    self.channel_dao.update_channel(channel.id, channel.description, channel.position)
        except Exception as e:
            print(f"Error loading manage channels: {e}")
            return None

    #mixer scene
    def load_mixer_scene(self, request):
        file_path = os.path.join(os.path.dirname(__file__), "..", "Database", "scenes.json")
        with open(file_path, "r") as json_data:
            scene = json.load(json_data)

            scenes = scene.get('scenes', [])

            return self.templates.TemplateResponse(request, "manage_mixer_scene.html", {"scenes" : scenes})

    def add_mixer_scene(self, idScene, name):
        file_path = os.path.join(os.path.dirname(__file__), "..", "Database", "scenes.json")
        with open(file_path, "r") as json_data:
            scene = json.load(json_data)

            scenes = scene.get('scenes', [])

            if any(s["id"] == idScene for s in scenes):
                print("Scena con questo ID già esistente.")
            else:
                scena = {
                    "id" : idScene,
                    "name" : name
                }

                scenes.append(scena)

                scenes.sort(key=lambda s: s["id"])

                with open(file_path, "w") as f:
                    json.dump({"scenes": scenes}, f, indent=4)


            return RedirectResponse(url="/admin/manageSceneMixer", status_code=303)

    def remove_mixer_scene(self, idScene):
        file_path = os.path.join(os.path.dirname(__file__), "..", "Database", "scenes.json")
        with open(file_path, "r") as json_data:
            data = json.load(json_data)

            data["scenes"] = [scene for scene in data["scenes"] if scene.get("id") != idScene]

            # Sovrascrivi il file con i dati aggiornati
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)


            return RedirectResponse(url="/admin/manageSceneMixer", status_code=303)

    def change_aux_user(self, user, aux, scene):
        self.partecipazioneScenaDAO.change_aux_user(scene, user, aux)


    #Edit layout file   
    def load_default_layout(self, user_id):
        channel_names = self.aux_service.load_fader_names(None)
        layouts = self.layout_channel_dao.get_layout_channel(user_id, -1)
  
        channel_map = {
            channel.id: ChannelLayoutDTO(
                channel_id=channel.id,
                name=channel.name,
                description=channel.description if channel.description else channel.name,
                type=None
            )
            for channel in channel_names
        }
        
        for layout in layouts:
            if layout.channel_id in channel_map:
                ch = channel_map[layout.channel_id]
                ch.position = layout.position
                ch.type = layout.type_channel
                ch.selected = True

        return list(channel_map.values())

    def save_default_layout(self, user_id, layouts):     
        self.layout_channel_dao.remove_layout_channel(user_id, -1)
        
        for layout in layouts:
            if layout.selected:
                self.layout_channel_dao.set_layout_channel(user_id, -1, layout.channel_id, layout.position, layout.description, layout.type)

        return True