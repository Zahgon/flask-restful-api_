from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from db import Base, session


class StoreModel(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True)
    name = Column(String(80))

    items = relationship("ItemModel", lazy="dynamic")

    def __init__(self, name):
        self.name = name

    def json(self):
        return {
            "name": self.name,
            "items": [item.json() for item in self.items.all()],
            "uuid": self.find_by_name(self.name).id,
        }

    @classmethod
    def find_by_name(cls, name):
        return session.query(cls).filter_by(name=name).first()

    def save_to_db(self):
        session.add(self)
        session.commit()

    def delete_from_db(self):
        session.delete(self)
        session.commit()
