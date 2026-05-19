from Database.database import DBSession
from models.profile_layout import ProfileLayout


class ProfileLayoutDAO():
    def __init__(self):
        self.db = DBSession.get()

    
    def create_profile_layout(self, user, profile_id, channel_id, scene_id, value=0):
        try:
            profile_layout = ProfileLayout(user_username = user, profile_id = profile_id, channel_id = channel_id, scene_id=scene_id, value= value)

            self.db.add(profile_layout)
            self.db.commit()

        except Exception as e:
            print(f"Error creating profile layout: {e}")
            return False

    def update_profile_layout(self, user, profile_id, channel_id, scene_id, value = 0):
        try:
            profile_layout = (
                self.db.query(ProfileLayout)
                .filter_by(
                    user_username=user,
                    profile_id=profile_id,
                    channel_id=channel_id,
                    scene_id=scene_id
                )
                .first()
            )

            if profile_layout:
                profile_layout.value = value


            self.db.add(profile_layout)
            self.db.commit()

        except Exception as e:
            self.db.rollback()  
            print(f"Error update profile layout: {e}")
            return False

    def get_profile_layout_user_scene(self, user, profile_id, scene_id):
        try:
            return self.db.query(ProfileLayout).filter(ProfileLayout.user_username == user, ProfileLayout.profile_id == profile_id, ProfileLayout.scene_id == scene_id)

        except Exception as e:
            print(f"Error retrieve profile layout: {e}")
            return False      

    def update_profiles_layout(self, profile_id, user, scene_id, profiles):
        try:
            profiles_stored = self.get_profile_layout_user_scene(user, profile_id, scene_id)

            for profile in profiles:
                key = int(profile["channel"])
                value = int(profile["value"])

                
                if any(key == obj.channel_id for obj in profiles_stored):
                    self.update_profile_layout(user, profile_id, key, scene_id, value)
                else:
                    self.create_profile_layout(user, profile_id, profile["channel"], scene_id, profile["value"])


        except Exception as e:
            print(f"Error updating profiles layout: {e}")
            return False    