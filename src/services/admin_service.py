from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from models.user import RuoloUtente
from dao.channel_dao import ChannelDAO
from dao.scene_dao import SceneDAO
from dao.user_dao import UserDAO
from dao.dca_dao import DCA_DAO
from dao.partecipazione_scena_dao import PartecipazioneScenaDAO
from fastapi.responses import RedirectResponse
import os
import json

class AdminService:
    def __init__(self):
        self.userDAO = UserDAO()
        self.sceneDAO = SceneDAO()
        self.channelDAO = ChannelDAO()
        self.dcaDAO = DCA_DAO()
        self.partecipazioneScenaDAO = PartecipazioneScenaDAO()
        self.templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "..", "view", "administration"))

    def load_manage_user(self, request, adminUser):
        users = self.get_all_users(adminUser)
        return self.templates.TemplateResponse(request, "manage_user.html", {"users": users})
 
    def create_user(self, request, adminUser, username, nome, ruolo):
        try:
            if self.userDAO.is_admin(adminUser):
                message=""
                users = self.get_all_users(adminUser)
                if username != None and username != "" and nome != None and nome != "" and ruolo != None and ruolo in [ r.value for r in RuoloUtente ]:
                    if not self.userDAO.get_user_by_username(username):
                        new_user = self.userDAO.create_user(username=username, nome=nome, ruolo=ruolo)
                        users.append(new_user)
                        message = "Utente inserito con successo"
                    else: 
                        message = "Errore utente già presente"
                else:
                    message = "Errore inserimento parametri"
                
                return self.templates.TemplateResponse(request, "manage_user.html", {"users": users, "message": message})
            else:
                return HTMLResponse(status_code=403, content="Non hai i permessi per accedere a questa risorsa")
        except Exception as e:
            print(f"Error creating user: {e}")
            return self.templates.TemplateResponse(request, "manage_user.html", {"users": users, "message": f"Errore durante l'inserimento {e}"})
        
    def delete_user(self, request, adminUser, username):
        users = self.get_all_users(adminUser)
        try:
            if self.userDAO.is_admin(adminUser):
                message = ""
                if self.userDAO.get_user_by_username(username) != None:
                    user = self.userDAO.delete_user(username)
                    message = f"utente {user.name} rimosso correttamente"
                    users.remove(user)
                else:
                    message = f"utente {username} inesistente"
                return self.templates.TemplateResponse(request, "manage_user.html", {"users": users, "message": message})
            else:
                return HTMLResponse(status_code=403, content="Non hai i permessi per accedere a questa risorsa")
        except Exception as e:
            print(f"Error deleting user: {e}")
            return self.templates.TemplateResponse(request, "manage_user.html", {"users": users, "message": f"Errore durante la cancellazione {e}"})
        
    def update_user(self, adminUser, username, nome, ruolo):
        try:
            if self.userDAO.is_admin(adminUser):
                user = self.userDAO.update_user(username)
                return True
            else:
                return False
        except Exception as e:
            print(f"Error updating user: {e}")
            return False

    def get_all_users(self, adminUser):
        try:
            if self.userDAO.is_admin(adminUser):
                users = self.userDAO.get_all_users()
                return users
            else:
                return HTMLResponse(status_code=403, content="Non hai i permessi per accedere a questa risorsa")
        except Exception as e:
            print(f"Error retrieving all users: {e}")
            return None
        
    def load_manage_channels(self, request, user):
        try:
            if self.userDAO.is_admin(user):
                channels = self.channelDAO.get_all_channels()
                dcas = self.dcaDAO.get_dca()
                return self.templates.TemplateResponse(request, "manage_channels.html", {"channels": channels, "dcas": dcas})
            else:
                return HTMLResponse(status_code=403, content="Non hai i permessi per accedere a questa risorsa")
        except Exception as e:
            print(f"Error loading manage channels: {e}")
            return None

    def change_description(self, user, type, id, value):
        try:
            if self.userDAO.is_admin(user):
                if value == "":
                    value = None
                if type == "channel":
                    self.channelDAO.update_channel_description(id, value)
                    return True
                elif type == "dca":
                    self.dcaDAO.update_dca_description(id, value)
                    return True
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

    def add_mixer_scene(self, request, idScene, name):
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

    def remove_mixer_scene(self, request, idScene):
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

    def load_default_user_layout(self, request):
        file_path = os.path.join(os.path.dirname(__file__), "..", "Database", "default_layout.json")
        with open(file_path, "r") as json_data:
            data = json.load(json_data)


            channels = self.channelDAO.get_all_channels()
            
            channel_ids = [ch["id"] for ch in data["channels"]]
            channels_layout = [x for x in channels if x.id in channel_ids]
            drums_ids = [ch["id"] for ch in data["drums"]]
            drums_layout = [x for x in channels if x.id in drums_ids]

            channels = [x for x in channels if x.id not in channel_ids and x.id not in drums_ids]

        return self.templates.TemplateResponse(request, "default_layout.html", {"canali": channels, "channels_layout": channels_layout, "drums_layout": drums_layout})

    def save_default_user_layout(self, channels, drums):
        file_path = os.path.join(os.path.dirname(__file__), "..", "Database", "default_layout.json")
        with open(file_path, "r") as json_data:
            data = json.load(json_data)

            data["channels"] = channels
            data["drums"] = drums

            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)

        return "Layout salvato con successo"