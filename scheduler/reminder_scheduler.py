from apscheduler.schedulers.asyncio import AsyncIOScheduler
from business.reminder.business_service import ReminderBusinessService
from data.session import SessionLocal
from models.reminder import Reminder
from models.user import User
from datetime import datetime, timedelta
import asyncio

scheduler = AsyncIOScheduler()
business = ReminderBusinessService()

async def check_reminders(bot):
    """Проверяет и отправляет напоминания (3 сообщения + повтор)"""
    session = SessionLocal()
    try:
        now = datetime.now()
        reminders = session.query(Reminder).filter(
            Reminder.reminder_datetime <= now,
            Reminder.is_active == True
        ).all()

        for r in reminders:
            try:
                # Загружаем пользователя по user_id
                user = session.query(User).get(r.user_id)
                if not user:
                    continue

                text = f"🔔 НАПОМИНАНИЕ!\n\n📌 {r.title}\n{r.description or ''}\n\nВремя: {r.reminder_datetime.strftime('%d.%m.%Y %H:%M')}"

                # Отправляем 3 сообщения с интервалом 2 минуты
                for i in range(3):
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=text + f"\n\nСообщение {i+1}/3"
                    )
                    if i < 2:
                        await asyncio.sleep(120)

                # Повторение
                if r.repeat_type == 'daily':
                    next_dt = r.reminder_datetime + timedelta(days=1)
                elif r.repeat_type == 'weekly':
                    next_dt = r.reminder_datetime + timedelta(days=7)
                else:
                    next_dt = None

                if next_dt:
                    business.data.create_reminder(r.user_id, r.title, r.description, next_dt, r.repeat_type)
                else:
                    business.data.mark_as_sent(r.id)

            except Exception as e:
                print(f"Ошибка отправки ID {r.id}: {e}")

    finally:
        session.close()

def start_scheduler(bot):
    scheduler.add_job(check_reminders, 'interval', seconds=30, args=(bot,))
    scheduler.start()
    print("✅ Планировщик напоминаний запущен")