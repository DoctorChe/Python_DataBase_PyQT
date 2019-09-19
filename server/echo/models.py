from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship

from server.utils.server_db import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    data = Column(String, nullable=True)
    created = Column(DateTime, default=datetime.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="messages")

    @property
    def is_anonymous(self):
        return self.user is None
