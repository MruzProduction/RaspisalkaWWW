from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Главная клавиатура
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить напоминание")],
        [KeyboardButton(text="📋 Мои напоминания")],
        [KeyboardButton(text="✏️ Редактировать напоминание")],
        [KeyboardButton(text="❌ Удалить напоминание")],
        [KeyboardButton(text="❌ Отмена")]
    ],
    resize_keyboard=True
)

# Клавиатура для выбора повторения
repeat_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Не повторять")],
        [KeyboardButton(text="Каждый день")],
        [KeyboardButton(text="Каждую неделю")],
        [KeyboardButton(text="Отмена")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Клавиатура подтверждения удаления
confirm_delete_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Да, удалить")],
        [KeyboardButton(text="❌ Нет, отменить")]
    ],
    resize_keyboard=True
)