from Database.database import DBSession
from models.aux_ import Aux


class AuxDAO:
    def __init__(self):
        self.db = DBSession.get()

    def get_all_aux(self):
        try:
            aux = self.db.query(Aux).all()
            return aux
        except Exception as e:
            print(f"Error retrieving all aux: {e}")
            return None

    def get_aux_by_id(self, id):
        try:
            aux = self.db.query(Aux).filter(Aux.id == id).first()
            return aux
        except Exception as e:
            print(f"Error retrieving aux by id: {e}")
            return None
        