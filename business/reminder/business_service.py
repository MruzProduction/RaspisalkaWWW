from __future__ import annotations
from datetime import datetime, timedelta
from business.reminder.data_service import ReminderDataService
from models.reminder import Reminder

class BusinessException(Exception):
    pass

class ReminderBusinessService:
    def __init__(self):
        self.data = ReminderDataService()

    def add_reminder(self, telegram_id: int, username: str | None, title: str, description: str | None, reminder_datetime: datetime, repeat_type='none'):
        if not title or len(title.strip()) == 0:
            raise BusinessException("Название напоминания обязательно!")
        if reminder_datetime <= datetime.now() + timedelta(minutes=5):
            raise BusinessException("Напоминание должно быть минимум через 5 минут!")

        user = self.data.get_or_create_user(telegram_id, username)
        return self.data.create_reminder(user.id, title.strip(), description, reminder_datetime, repeat_type)

    def get_reminders(self, telegram_id: int):
        user = self.data.get_or_create_user(telegram_id, None)
        return self.data.get_user_reminders(user.id)

    def get_reminder(self, telegram_id: int, reminder_id: int):
        user = self.data.get_or_create_user(telegram_id, None)
        reminder = self.data.get_reminder_by_id(reminder_id, user.id)
        if not reminder:
            raise BusinessException("Напоминание не найдено или принадлежит другому пользователю!")
        return reminder

    def update_reminder(self, telegram_id: int, reminder_id: int, title: str, description: str | None, reminder_datetime: datetime, version: int):
        if not title or len(title.strip()) == 0:
            raise BusinessException("Название обязательно!")
        if reminder_datetime <= datetime.now() + timedelta(minutes=5):
            raise BusinessException("Новое время должно быть в будущем!")

        user = self.data.get_or_create_user(telegram_id, None)
        success = self.data.update_reminder(reminder_id, user.id, title.strip(), description, reminder_datetime, version)
        if not success:
            raise BusinessException("Напоминание было изменено другим пользователем или уже удалено. Обновите список!")
        return True

    def delete_reminder(self, telegram_id: int, reminder_id: int, version: int):
        user = self.data.get_or_create_user(telegram_id, None)
        success = self.data.delete_reminder(reminder_id, user.id, version)
        if not success:
            raise BusinessException("Напоминание уже удалено или изменено другим пользователем!")
        return True