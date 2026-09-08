from sqlalchemy import Column, Integer, String

from db import Base, session


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(20))
    password = Column(String(10))

    def __init__(self, username, password):
        self.id = None
        self.username = username
        self.password = password

    def save_to_db(self):
        session.add(self)
        session.commit()

    def delete_from_db(self):
        session.delete(self)
        session.commit()

    @classmethod
    def find_by_username(cls, username):
        return session.query(cls).filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id):
        return session.query(cls).filter_by(id=_id).first()
