from http.client import HTTPResponse
import os
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from dao.aux_dao import AuxDAO
from dao.partecipazione_scena_dao import PartecipazioneScenaDAO
from dao.scene_dao import SceneDAO
from dao.user_dao import UserDAO
from dao.layout_canale_dao import LayoutCanaleDAO
from dotenv import load_dotenv
from dto.response.scene_dto import SceneDTO
from midi.midi_controller import MidiListener, call_type, MidiController
import json
from settings import POST_NAME 

class SceneService:
    def __init__(self):
        self.scene_dao = SceneDAO()
        self.aux_dao = AuxDAO()
        self.user_dao = UserDAO()
        self.scene_partecipation_dao = PartecipazioneScenaDAO()
        self.layout_channel_dao = LayoutCanaleDAO()
        self.midiController = MidiController()

    def manage_scene(self, request, adminUser):
        if self.user_dao.is_admin(adminUser):
            scenes = self.scene_dao.get_all_scenes()
            return self.templates.TemplateResponse(request, "manage_scene.html", {"scenes" : scenes, })
        
        else:    
            return HTMLResponse(status_code=403, content="Non hai i permessi per accedere a questa risorsa")

    def create_scene(self, request, adminUser, nome, descrizione):
        if self.user_dao.is_admin(adminUser) == False:
            return HTTPResponse(status_code=403, content="Non hai i permessi per accedere a questa risorsa")
        
        scenes = self.scene_dao.get_all_scenes()

        try:
            new_scene = self.scene_dao.create_scene(nome, descrizione)
            scenes.append(new_scene)
            return self.templates.TemplateResponse(request, "manage_scene.html", {"scenes" : scenes, "message" : f"scena {new_scene.name} creata con successo" })
        except Exception as e:
            print(f"Error creating scene: {e}")
            return self.templates.TemplateResponse(request, "manage_scene.html", {"scenes" : scenes, "message" : f"errore creazione scena {e}" })

    def get_scene(self, request, adminUser, id):
        if self.user_dao.is_admin(adminUser) == False:
            return HTTPResponse(status_code=403, content="Non hai i permessi per accedere a questa risorsa")

        try:
            scene = self.scene_dao.get_scene_by_id(id)
            auxs = self.aux_dao.get_all_aux()
            partecipazioni = self.scene_partecipation_dao.get_participants_scene(id)
            utenti = self.scene_partecipation_dao.get_user_not_in_scene(id)


            # auxs name
            listenAddressAuxName = []
            for aux in auxs:
                auxAddress = [int(x,16) for x in aux.midi_address_main.split(",")]

                listenAddressAuxName.append(auxAddress + self.postName)
            
            resultsValueAuxName = MidiListener.init_and_listen(listenAddressAuxName, call_type.NAME)
            
            resultsValueAuxSetName = []

            for aux in auxs:
                auxAddress = [int(x,16) for x in aux.midi_address_main.split(",")] 
                try:
                    resultsValueAuxSetName.append(resultsValueAuxName[tuple(auxAddress + self.postName)])
                except KeyError as k:
                    print("errore chiave ", k)
                    resultsValueAuxSetName.append("")

            auxs = list(zip(auxs, resultsValueAuxSetName))
        
            return self.templates.TemplateResponse(request, "update_scene.html", {"scene" : scene, "partecipanti" : partecipazioni, "users" : utenti, "auxs" : auxs })
        
        except Exception as e:
            print(f"Error retrieving scenes: {e}")
            return self.templates.TemplateResponse(request, "update_scene.html")

    def add_partecipante(self, request, adminUser, sceneId, user, aux):
        if self.user_dao.is_admin(adminUser) == False:
            return HTTPResponse(status_code=403, content="Non hai i permessi per accedere a questa risorsa")

        result = None

        try:
            scene = self.scene_dao.get_scene_by_id(sceneId)
            
            auxs = self.aux_dao.get_all_aux()
            utenti = self.scene_partecipation_dao.get_user_not_in_scene(sceneId)

            if user in [u.username for u in utenti] and int(aux) in [a.id for a in auxs]:
                self.scene_partecipation_dao.add_participants(sceneId, user, aux)
                partecipazioni = self.scene_partecipation_dao.get_participants_scene(sceneId)

                utenti = self.scene_partecipation_dao.get_user_not_in_scene(sceneId)

                result = {
                    'status' : True,
                    'message' :"utente assegnato con successo" 
                }


                # create default layout for the user
                self.layout_channel_dao.add_default_layout_channel(user, sceneId)

            else:
                result = {
                    'status' : False,
                    'message' : "utente ha già un aux assegnato" 
                }

            partecipazioni = self.partecipazioneScenaDAO.get_participants_scene(sceneId)
            return json.dumps(result)

        except Exception as e:
            print(f"Error retrieving scenes: {e}")
            result = {
                'status' : False,
                'message' : 'errore interno'
            }
            return json.dumps(result)

    def remove_partecipante(self, request, adminUser, sceneId, user):
        if self.user_dao.is_admin(adminUser) == False:
            return HTTPResponse(status_code=403, content="Non hai i permessi per accedere a questa risorsa")

        try:
            scene = self.scene_dao.get_scene_by_id(sceneId)

            partecipazioni = self.scene_partecipation_dao.get_participants_scene(sceneId)

            partecipazioni = list(partecipazioni)

            if user in [u.user_username for u in partecipazioni]:
                self.scene_partecipation_dao.remove_participants(sceneId, user)

                partecipazioni = self.scene_partecipation_dao.get_participants_scene(sceneId)
                utenti = self.scene_partecipation_dao.get_user_not_in_scene(sceneId)

                result = {
                    'status' : True,
                    'message' : "utente rimosso con successo"
                } 
            else:
                result = {
                    'status' : False,
                    'message' : "utente non ha una precedente assegnazione"
                }

            utenti = self.scene_partecipation_dao.get_user_not_in_scene(sceneId)

            return json.dumps(result)
                        
        except Exception as e:
            print(f"Error retrieving scenes: {e}")
            result = {
                'status' : False,
                'message' :"utente assegnato con successo" 
            }
            return json.dumps(result)

    def get_all_scene(self, adminUser):
        if self.user_dao.is_admin(adminUser) == False:
            return HTTPResponse(status_code=403, content="Non hai i permessi per accedere a questa risorsa")

        try:
            scenes = self.scene_dao.get_all_scenes()
            return scenes
        except Exception as e:
            print(f"Error retrieving all scenes: {e}")
            return None

    def delete_scene(self, request, adminUser, sceneId):
        if self.user_dao.is_admin(adminUser) == False:
            return HTTPResponse(status_code=403, content="Non hai i permessi per accedere a questa risorsa")

        try:
            scenes = self.scene_dao.delete_scene(sceneId)
            return RedirectResponse(url="/admin/manageScene", status_code=303)
            
        except Exception as e:
            print(f"Error retrieving all scenes: {e}")
            return None

    def update_scene(self, adminUser, id, nome, descrizione):

        if self.user_dao.is_admin(adminUser) == False:
            return HTTPResponse(status_code=403, content="Non hai i permessi per accedere a questa risorsa")

        try:
            scene = self.scene_dao.updateScene(id, nome, descrizione)
            return scene != None
        except Exception as e:
            print(f"Error updating scene: {e}")
            return False
        
    def get_all_user_scene(self, username):
        try:
            scenes = self.scene_dao.get_all_user_scene(username)

            return [SceneDTO.model_validate(s) for s in scenes]
        
        except Exception as e:
            print(f"Error retrieving all user scenes: {e}")
            return None