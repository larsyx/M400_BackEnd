from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.engine import Engine
from models.scene_participation import SceneParticipation
from models.layout_channel import LayoutChannel
import os
DATABASE_URL = "sqlite:///Database/database.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)


@event.listens_for(Engine, "connect")
def enable_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@event.listens_for(SceneParticipation, 'after_delete')
def delete_layout_canale(mapper, connection, target):
    connection.execute(
        LayoutChannel.__table__.delete().where(
            (LayoutChannel.scene_id == target.scene_id) &
            (LayoutChannel.user_username == target.user_username)
        )
    )

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

# Singleton-like access
class DBSession:
    _session: Session = None

    @classmethod
    def get(cls) -> Session:
        if cls._session is None:
            cls._session = SessionLocal()
        return cls._session

    @classmethod
    def close(cls):
        if cls._session:
            cls._session.close()
            cls._session = None