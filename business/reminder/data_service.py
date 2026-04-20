from __future__ import annotations
from data.session import SessionLocal
from models.reminder import Reminder
from models.user import User
from sqlalchemy import select, update, delete

class ReminderDataService:
    def __init__(self):
        self.session = SessionLocal()

    def get_or_create_user(self, telegram_id: int, username: str | None):
        user = self.session.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            user = User(telegram_id=telegram_id, username=username)
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
        return user

    def create_reminder(self, user_id: int, title: str, description: str | None, reminder_datetime, repeat_type='none'):
        reminder = Reminder(
            user_id=user_id,
            title=title,
            description=description,
            reminder_datetime=reminder_datetime,
            repeat_type=repeat_type
        )
        self.session.add(reminder)
        self.session.commit()
        self.session.refresh(reminder)
        return reminder

    def get_user_reminders(self, user_id: int):
        return self.session.query(Reminder).filter_by(user_id=user_id, is_active=True).all()

    def get_reminder_by_id(self, reminder_id: int, user_id: int):
        return self.session.query(Reminder).filter_by(id=reminder_id, user_id=user_id).first()

    def update_reminder(self, reminder_id: int, user_id: int, title: str, description: str | None, reminder_datetime, version: int):
        stmt = update(Reminder).where(
            Reminder.id == reminder_id,
            Reminder.user_id == user_id,
            Reminder.version == version
        ).values(
            title=title,
            description=description,
            reminder_datetime=reminder_datetime,
            version=Reminder.version + 1
        )
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount > 0

    def delete_reminder(self, reminder_id: int, user_id: int, version: int):
        stmt = delete(Reminder).where(
            Reminder.id == reminder_id,
            Reminder.user_id == user_id,
            Reminder.version == version
        )
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount > 0

    def mark_as_sent(self, reminder_id: int):
        self.session.query(Reminder).filter_by(id=reminder_id).update({"is_active": False})
        self.session.commit()