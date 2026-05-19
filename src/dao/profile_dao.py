from Database.database import DBSession
from models.profile import Profile

class ProfileDAO:
    def __init__(self):
        self.db = DBSession.get()

    def create_profile(self, name, scene_id, user):
        try:
            profile = Profile(name = name, scene_id = scene_id, user_username = user)
            self.db.add(profile)
            self.db.commit()
            return profile
        except Exception as e:
            print(f"Error create profile for user: {e}")
            return False

    def delete_profile(self, id, user, scene_id):
        try:
            profile = self.db.query(Profile).filter(Profile.id == id, Profile.user_username == user, Profile.scene_id == scene_id).first()

            self.db.delete(profile)
            self.db.commit()

            return True
        except Exception as e:
            print(f"Error delete profile : {e}")
            return False

    def get_all_profile_user(self, user, scene_id):
        try:
            profiles = self.db.query(Profile).filter(Profile.user_username == user, Profile.scene_id == scene_id)

            return profiles
        except Exception as e:
            print(f"Error retrieve profiles: {e}")
            return None