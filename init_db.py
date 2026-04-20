from data.session import engine, SessionLocal
from data.base import Base
from models.user import User
from models.reminder import Reminder
from datetime import datetime, timedelta

def init_database():
    print("🚀 Создаём SQLite базу...")
    Base.metadata.create_all(bind=engine)
    
    # Добавляем индексы для быстрой работы с большим количеством данных
    with engine.connect() as conn:
        conn.execute("CREATE INDEX IF NOT EXISTS idx_reminder_datetime ON reminders (reminder_datetime)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON reminders (user_id)")
        conn.commit()
    
    print("✅ Индексы созданы — база готова к большому объёму данных!")

    # Тестовые данные (как раньше)
    # ... (оставляем твой старый код заполнения)

if __name__ == "__main__":
    init_database()