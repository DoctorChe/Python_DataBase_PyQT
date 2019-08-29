from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from server.utils.server_db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    # password = Column(String, nullable=False)
    messages = relationship("Message", back_populates="user")
    contacts = relationship("Contact", back_populates="user")
