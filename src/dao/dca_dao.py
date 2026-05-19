from Database.database import DBSession
from models.dca import DCA


class DCA_DAO:

    def __init__(self):
        self.db = DBSession.get()

    def get_dca(self):
        return self.db.query(DCA).all()
        
    def get_dca_by_id(self, dca_id):
        return self.db.query(DCA).filter(DCA.id == dca_id).first()
    
    def edit_dca(self, dca_id, description):
        dca = self.get_dca_by_id(dca_id)
        if dca:
            dca.description = description
            self.db.commit()
            return dca
        
    def get_dca_by_address(self, address):
        return self.db.query(DCA).filter(DCA.midi_address == address).first()
    

    def update_dca_description(self, id, value):
        try:
            self.db.query(DCA).filter(DCA.id == id).update({DCA.description: value})
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error updating dca: {e}")
            return False