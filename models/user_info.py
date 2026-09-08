from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db import Base, session


class UserInfoModel(Base):
    __tablename__ = "users_info"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("UserModel")

    street = Column(String(20))
    city = Column(String(20))
    home_number = Column(Integer)
    phone = Column(String(20))
    email = Column(String(20))

    def __init__(self, user_id, address, phone, email):
        self.user_id = user_id
        self.street = address.get("street")
        self.city = address.get("city")
        self.home_number = address.get("home_number")
        self.phone = phone
        self.email = email

    def json(self, uuid):
        return {
            "city": self.city,
            "street": self.street,
            "userID": uuid,
            "phone": self.phone,
            "email": self.email,
        }

    @classmethod
    def find_by_id(cls, _id):
        return session.query(cls).filter_by(user_id=_id).first()

    def save_to_db(self):
        session.add(self)
        session.commit()

    def delete_from_db(self):
        session.delete(self)
        session.commit()
