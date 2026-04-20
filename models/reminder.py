from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, Boolean
from data.base import Base

class Reminder(Base):
    __tablename__ = "reminders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    reminder_datetime = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=0, nullable=False)
    repeat_type = Column(String(20), default='none')  # 'none', 'daily', 'weekly'