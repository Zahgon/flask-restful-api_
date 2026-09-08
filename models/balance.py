from sqlalchemy import Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from db import Base, session


class BalanceModel(Base):
    __tablename__ = "balance"

    id = Column(Integer, primary_key=True)
    balance = Column(Float(precision=2))

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("UserModel")

    def __init__(self, user_id, balance):
        self.user_id = user_id
        self.balance = balance

    @classmethod
    def find_by_name(cls, name):
        return session.query(cls).filter_by(name=name).first()

    @classmethod
    def find_by_id(cls, _id):
        return session.query(cls).filter_by(user_id=_id).first()

    def save_to_db(self):
        session.add(self)
        session.commit()

    def delete_from_db(self):
        session.delete(self)
        session.commit()
