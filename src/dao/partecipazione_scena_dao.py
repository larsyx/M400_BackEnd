from Database.database import DBSession
from models.aux_ import Aux
from models.scene_participation import SceneParticipation
from models.user import RuoloUtente, User


class PartecipazioneScenaDAO:
    def __init__(self):
        self.db = DBSession.get()

    def get_aux_user(self, userID, scenaID):
        try:
            partecipazione = (
                self.db.query(SceneParticipation)
                .filter(
                    SceneParticipation.user_username == userID,
                    SceneParticipation.scene_id == scenaID,
                )
                .first()
            )

            if partecipazione:
                aux = self.db.query(Aux).filter(partecipazione.aux_id == Aux.id).first()
                return aux if aux else None
            return None
        except Exception as e:
            print(f"Error retrieving aux for user: {e}")
            return None
        
    def get_participants_scene(self, sceneId):
        try:
            partecipanti = self.db.query(SceneParticipation).filter(SceneParticipation.scene_id == sceneId)
            return partecipanti
        
        except Exception as e:
            print(f"Error get partecipant for user: {e}")
            return None
        
    def get_aux_not_in_scene(self, scenaID):
        try:
            subquery = self.db.query(SceneParticipation.aux_id).filter(SceneParticipation.scene_id == scenaID)
            aux = self.db.query(Aux).filter(Aux.id.not_in(subquery))
            return aux
        except Exception as e:
            print(f"Error get partecipant for user: {e}")
            return None
        
    def get_user_not_in_scene(self, scenaID):
        try:
            subquery = self.db.query(SceneParticipation.user_username).filter(SceneParticipation.scene_id == scenaID)
            users = self.db.query(User).filter(User.username.not_in(subquery), User.role == RuoloUtente.utente).order_by(User.name.asc())
            return users
        except Exception as e:
            print(f"Error get partecipant for user: {e}")
            return None
        
    def add_participants(self, sceneId, User, aux):
        try:
            partecipazione = SceneParticipation(scene_id = sceneId, user_username = User, aux_id = aux)
            self.db.add(partecipazione)
            self.db.commit()
            return partecipazione
        except Exception as e:
            print(f"Error add for user: {e}")
            return None
        
    def remove_participants(self, sceneId, user):
        try:
            partecipazione = self.db.query(SceneParticipation).filter(SceneParticipation.scene_id == sceneId, SceneParticipation.user_username == user).first()

            self.db.delete(partecipazione)
            self.db.commit()
            return partecipazione
        except Exception as e:
            print(f"Error add for user: {e}")
            return None

    def change_aux_user(self, sceneId, user, aux):

        partecipante = self.db.query(SceneParticipation).filter(
            SceneParticipation.user_username == user,
            SceneParticipation.scene_id == int(sceneId)
        ).first()

        auxObj = self.db.query(Aux).filter(
            Aux.id == aux
        ).first()

        if partecipante and aux:
            partecipante.aux_id = aux

            self.db.commit()