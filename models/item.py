from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db import Base, session


class ItemModel(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    name = Column(String(80))
    price = Column(Float(precision=2))
    image = Column(String(80))
    description = Column(String(240))

    store_id = Column(Integer, ForeignKey("stores.id"))
    store = relationship("StoreModel")

    def __init__(self, name, price, store_id, description, image):
        self.name = name
        self.price = price
        self.store_id = store_id
        self.description = description
        self.image = image

    def json(self, uuid):
        return {
            "name": self.name,
            "price": self.price,
            "itemID": uuid,
            "description": self.description,
            "image": self.image,
        }

    @classmethod
    def find_by_name(cls, name):
        return session.query(cls).filter_by(name=name).first()

    @classmethod
    def find_by_id(cls, _id):
        return session.query(cls).filter_by(id=_id).first()

    def save_to_db(self):
        session.add(self)
        session.commit()

    def delete_from_db(self):
        session.delete(self)
        session.commit()
