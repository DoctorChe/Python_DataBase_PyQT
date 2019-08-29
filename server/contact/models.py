from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from server.utils.server_db import Base


class Contact(Base):
    __tablename__ = "contact"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    info = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="contacts")
