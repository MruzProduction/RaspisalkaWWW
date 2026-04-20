from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from business.reminder.business_service import ReminderBusinessService, BusinessException
from datetime import datetime, timedelta

from bot.keyboards import main_keyboard, repeat_keyboard, confirm_delete_keyboard

router = Router()
business = ReminderBusinessService()

# ====================== СОСТОЯНИЯ ======================
class AddReminder(StatesGroup):
    title = State()
    description = State()
    datetime = State()
    repeat = State()

class EditReminder(StatesGroup):
    waiting_id = State()
    title = State()
    description = State()
    datetime_str = State()

class DeleteReminder(StatesGroup):
    waiting_id = State()
    confirm = State()

# ====================== START ======================
@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("👋 Привет! Я Raspisalka — твой личный бот-напоминалка.\nНажимай кнопки ниже 👇", reply_markup=main_keyboard)

# ====================== ДОБАВЛЕНИЕ ======================
@router.message(F.text == "➕ Добавить напоминание")
async def add_reminder_start(message: Message, state: FSMContext):
    await state.set_state(AddReminder.title)
    await message.answer("Напиши название напоминания:")

@router.message(AddReminder.title)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(AddReminder.description)
    await message.answer("Описание (можно пропустить, отправь '-'):")

@router.message(AddReminder.description)
async def process_description(message: Message, state: FSMContext):
    desc = None if message.text == "-" else message.text
    await state.update_data(description=desc)
    await state.set_state(AddReminder.datetime)
    await message.answer("Когда напомнить? (формат: 12.04.2026 15:30)")

@router.message(AddReminder.datetime)
async def process_datetime(message: Message, state: FSMContext):
    try:
        dt = datetime.strptime(message.text, "%d.%m.%Y %H:%M")
        await state.update_data(datetime=dt)
        await state.set_state(AddReminder.repeat)
        await message.answer("Повторять это напоминание?", reply_markup=repeat_keyboard)
    except ValueError:
        await message.answer("❌ Неверный формат даты!\nИспользуй: дд.мм.гггг чч:мм")

@router.message(AddReminder.repeat, F.text.in_({"Не повторять", "Каждый день", "Каждую неделю", "Отмена"}))
async def process_repeat(message: Message, state: FSMContext):
    text = message.text
    if text == "Отмена":
        await message.answer("❌ Добавление отменено.", reply_markup=main_keyboard)
        await state.clear()
        return

    repeat_type = "none" if text == "Не повторять" else "daily" if text == "Каждый день" else "weekly"

    data = await state.get_data()
    dt = data["datetime"]

    reminder = business.add_reminder(
        message.from_user.id, message.from_user.username,
        data["title"], data["description"], dt, repeat_type
    )

    repeat_str = "не повторяется" if repeat_type == "none" else repeat_type.capitalize()
    await message.answer(
        f"✅ Напоминание создано!\nID: {reminder.id}\nВремя: {dt.strftime('%d.%m.%Y %H:%M')}\nПовтор: {repeat_str}",
        reply_markup=main_keyboard
    )
    await state.clear()

# ====================== СПИСОК ======================
@router.message(F.text == "📋 Мои напоминания")
async def list_reminders(message: Message):
    reminders = business.get_reminders(message.from_user.id)
    if not reminders:
        await message.answer("У тебя пока нет напоминаний.", reply_markup=main_keyboard)
        return
    text = "📋 Твои напоминания:\n\n"
    for r in reminders:
        repeat = " (ежедневно)" if getattr(r, 'repeat_type', 'none') == "daily" else " (еженедельно)" if getattr(r, 'repeat_type', 'none') == "weekly" else ""
        text += f"🆔 {r.id} | {r.title} — {r.reminder_datetime.strftime('%d.%m.%Y %H:%M')}{repeat}\n"
    await message.answer(text, reply_markup=main_keyboard)

# ====================== РЕДАКТИРОВАНИЕ ======================
@router.message(F.text == "✏️ Редактировать напоминание")
async def start_edit(message: Message, state: FSMContext):
    reminders = business.get_reminders(message.from_user.id)
    if not reminders:
        await message.answer("У тебя нет напоминаний для редактирования.", reply_markup=main_keyboard)
        return
    text = "📋 Твои напоминания:\n\n"
    for r in reminders:
        text += f"🆔 {r.id} | {r.title} — {r.reminder_datetime.strftime('%d.%m.%Y %H:%M')}\n"
    text += "\nОтправь ID напоминания, которое хочешь отредактировать:"
    await message.answer(text)
    await state.set_state(EditReminder.waiting_id)

@router.message(EditReminder.waiting_id)
async def process_edit_id(message: Message, state: FSMContext):
    try:
        rem_id = int(message.text.strip())
        reminder = business.get_reminder(message.from_user.id, rem_id)

        await state.update_data(
            reminder_id=rem_id,
            version=reminder.version,
            current_title=reminder.title,
            current_description=reminder.description,
            current_datetime=reminder.reminder_datetime
        )

        await message.answer(
            f"Текущее напоминание:\n"
            f"📌 Название: {reminder.title}\n"
            f"📝 Описание: {reminder.description or '—'}\n"
            f"🕒 Время: {reminder.reminder_datetime.strftime('%d.%m.%Y %H:%M')}\n\n"
            f"Новое название (или `-` чтобы оставить):",
            reply_markup=main_keyboard
        )
        await state.set_state(EditReminder.title)
    except ValueError:
        await message.answer("Пожалуйста, отправь числовой ID.")
    except BusinessException as e:
        await message.answer(f"❌ {e}")

@router.message(EditReminder.title)
async def process_edit_title(message: Message, state: FSMContext):
    data = await state.get_data()
    new_title = data["current_title"] if message.text.strip() == "-" else message.text.strip()
    if not new_title:
        await message.answer("Название не может быть пустым!")
        return
    await state.update_data(new_title=new_title)
    await message.answer("Новое описание (или `-` чтобы оставить):")
    await state.set_state(EditReminder.description)

@router.message(EditReminder.description)
async def process_edit_description(message: Message, state: FSMContext):
    data = await state.get_data()
    new_desc = None if message.text.strip() == "-" else message.text.strip()
    await state.update_data(new_description=new_desc)
    await message.answer("Новое время (формат: 12.04.2026 15:30) или `-` чтобы оставить:")
    await state.set_state(EditReminder.datetime_str)

@router.message(EditReminder.datetime_str)
async def process_edit_datetime(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text.strip() == "-":
        new_dt = data["current_datetime"]
    else:
        try:
            new_dt = datetime.strptime(message.text.strip(), "%d.%m.%Y %H:%M")
            if new_dt <= datetime.now() + timedelta(minutes=5):
                await message.answer("Новое время должно быть минимум через 5 минут!")
                return
        except ValueError:
            await message.answer("❌ Неверный формат! Используй дд.мм.гггг чч:мм или `-`")
            return

    try:
        business.update_reminder(
            message.from_user.id,
            data["reminder_id"],
            data["new_title"],
            data["new_description"],
            new_dt,
            data["version"]
        )
        await message.answer(f"✅ Напоминание #{data['reminder_id']} успешно обновлено!", reply_markup=main_keyboard)
        await state.clear()
    except BusinessException as e:
        await message.answer(f"❌ {e}")
        await state.clear()

# ====================== УДАЛЕНИЕ ======================
@router.message(F.text == "❌ Удалить напоминание")
async def start_delete(message: Message, state: FSMContext):
    reminders = business.get_reminders(message.from_user.id)
    if not reminders:
        await message.answer("У тебя нет напоминаний для удаления.", reply_markup=main_keyboard)
        return
    text = "📋 Твои напоминания:\n\n"
    for r in reminders:
        text += f"🆔 {r.id} | {r.title} — {r.reminder_datetime.strftime('%d.%m.%Y %H:%M')}\n"
    text += "\nОтправь ID напоминания, которое хочешь удалить:"
    await message.answer(text)
    await state.set_state(DeleteReminder.waiting_id)

@router.message(DeleteReminder.waiting_id)
async def process_delete_id(message: Message, state: FSMContext):
    try:
        rem_id = int(message.text.strip())
        reminder = business.get_reminder(message.from_user.id, rem_id)
        await state.update_data(reminder_id=rem_id, version=reminder.version)
        await message.answer(
            f"❗ Уверены, что хотите удалить это напоминание?\n\n"
            f"📌 {reminder.title}\n"
            f"🕒 {reminder.reminder_datetime.strftime('%d.%m.%Y %H:%M')}",
            reply_markup=confirm_delete_keyboard
        )
        await state.set_state(DeleteReminder.confirm)
    except ValueError:
        await message.answer("Пожалуйста, отправь числовой ID.")
    except BusinessException as e:
        await message.answer(f"❌ {e}")

@router.message(DeleteReminder.confirm)
async def process_delete_confirm(message: Message, state: FSMContext):
    if message.text == "✅ Да, удалить":
        data = await state.get_data()
        try:
            business.delete_reminder(message.from_user.id, data["reminder_id"], data["version"])
            await message.answer("✅ Напоминание успешно удалено!", reply_markup=main_keyboard)
        except BusinessException as e:
            await message.answer(f"❌ {e}")
    else:
        await message.answer("❌ Удаление отменено.", reply_markup=main_keyboard)
    await state.clear()

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("Просто используй кнопки!", reply_markup=main_keyboard)