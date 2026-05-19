from Database.database import DBSession
from models.scene import Scene


class SceneDAO:
    def __init__(self):
        self.db = DBSession.get()


    def get_scene_by_id(self, id):
        try:
            scene = self.db.query(Scene).filter(Scene.id == id).first()
            return scene
        except Exception as e:
            print(f"Error retrieving scene: {e}")
            return None

    def get_all_scenes(self):
        try:
            scenes = self.db.query(Scene).all()
            return scenes
        except Exception as e:
            print(f"Scene dao error retrieving scenes: {e}")
            return None


    def create_scene(self, nome, descrizione):
        try:
            new_scene = Scene(name=nome, description=descrizione)
            self.db.add(new_scene)
            self.db.commit()
            return new_scene
        except Exception as e:
            print(f"Error creating scene: {e}")
            return None
        

    def update_scene(self, id, nome, descrizione):
        try:
            scene = self.get_scene_by_id(id)
            if scene:
                scene.name = nome
                scene.description = descrizione
                self.db.commit()
                return scene
            else:
                return None
        except Exception as e:
            print(f"Error updating scene: {e}")
            return None
        
    
    def delete_scene(self, id):
        try:
            scene = self.get_scene_by_id(id)
            if scene:
                self.db.delete(scene)
                self.db.commit()
                return scene
            else:
                return None
        except Exception as e:
            print(f"Error deleting scene: {e}")
            return None
        
    def get_all_user_scene(self, username):
        try:
            scenes = self.db.query(Scene).filter(Scene.scene_participation.any(user_username=username)).all()
            return scenes
        except Exception as e:
            print(f"Error retrieving user scenes: {e}")
            return None