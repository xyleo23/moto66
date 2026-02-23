"""FSM регистрации и анкеты участника."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import SUPERADMIN_ID
from database.engine import async_session_maker
from database.models import User
from keyboards.main_menu import get_main_keyboard
from states.registration import RegistrationStates
from keyboards.registration import (
    get_contact_keyboard,
    get_moto_type_keyboard,
    get_category_a_keyboard,
)
from keyboards.fsm import get_cancel_keyboard, get_back_cancel_keyboard

router = Router(name="registration")


async def start_registration(message: Message, state: FSMContext) -> None:
    """Запуск анкеты."""
    await state.set_state(RegistrationStates.name)
    await message.answer(
        "Как вас зовут? (имя или псевдоним)",
        reply_markup=get_cancel_keyboard(),
    )


@router.message(RegistrationStates.name, F.text)
async def process_name(message: Message, state: FSMContext) -> None:
    """Имя."""
    await state.update_data(name=message.text.strip()[:100])
    await state.set_state(RegistrationStates.phone)
    await message.answer(
        "Отправьте номер телефона:",
        reply_markup=get_contact_keyboard(has_back=True),
    )


@router.message(RegistrationStates.phone, F.text == "⬅️ Назад")
async def reg_back_phone(message: Message, state: FSMContext) -> None:
    """Назад: телефон -> имя."""
    await state.set_state(RegistrationStates.name)
    await message.answer("Как вас зовут? (имя или псевдоним)", reply_markup=get_cancel_keyboard())


@router.message(RegistrationStates.phone)
async def process_phone(message: Message, state: FSMContext) -> None:
    """Телефон — только через Share Contact."""
    if message.contact:
        if message.contact.user_id != message.from_user.id:
            await message.answer("Пожалуйста, нажмите «Поделиться контактом» от своего имени.")
            return
        phone = message.contact.phone_number or ""
        await state.update_data(phone=phone)
        await state.set_state(RegistrationStates.driving_experience)
        await message.answer("Ваш стаж вождения в годах? (число)", reply_markup=get_back_cancel_keyboard())
        return
    await message.answer("Нажмите кнопку «Поделиться контактом»:", reply_markup=get_contact_keyboard(has_back=True))


@router.message(RegistrationStates.driving_experience, F.text == "⬅️ Назад")
async def reg_back_experience(message: Message, state: FSMContext) -> None:
    """Назад: стаж -> телефон."""
    await state.set_state(RegistrationStates.phone)
    await message.answer("Отправьте номер телефона:", reply_markup=get_contact_keyboard(has_back=True))


@router.message(RegistrationStates.driving_experience, F.text.regexp(r"^\d+$"))
async def process_experience(message: Message, state: FSMContext) -> None:
    """Стаж вождения."""
    exp = int(message.text)
    if exp > 50:
        await message.answer("Укажите корректный стаж (до 50 лет).")
        return
    await state.update_data(driving_experience=exp)
    await state.set_state(RegistrationStates.motorcycle_type)
    await message.answer("Выберите тип мотоцикла:", reply_markup=get_moto_type_keyboard())


@router.callback_query(RegistrationStates.motorcycle_type, F.data.startswith("moto:"))
async def process_moto_type(callback: CallbackQuery, state: FSMContext) -> None:
    """Тип мотоцикла."""
    moto_type = callback.data.split(":", 1)[1]
    await state.update_data(motorcycle_type=moto_type)
    await state.set_state(RegistrationStates.engine_capacity)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Объём двигателя в кубах? (число, например 600)", reply_markup=get_back_cancel_keyboard())


@router.message(RegistrationStates.engine_capacity, F.text == "⬅️ Назад")
async def reg_back_engine(message: Message, state: FSMContext) -> None:
    """Назад: объём -> тип мото."""
    await state.set_state(RegistrationStates.motorcycle_type)
    await message.answer("Выберите тип мотоцикла:", reply_markup=get_moto_type_keyboard())


@router.message(RegistrationStates.engine_capacity, F.text.regexp(r"^\d+$"))
async def process_engine(message: Message, state: FSMContext) -> None:
    """Объём двигателя."""
    cap = int(message.text)
    if cap < 50 or cap > 3000:
        await message.answer("Укажите объём от 50 до 3000 см³.")
        return
    await state.update_data(engine_capacity=cap)
    await state.set_state(RegistrationStates.category_a)
    await message.answer("Есть права категории А?", reply_markup=get_category_a_keyboard())


@router.callback_query(RegistrationStates.category_a, F.data.startswith("cat_a:"))
async def process_category_a(callback: CallbackQuery, state: FSMContext) -> None:
    """Категория А."""
    category_a = callback.data == "cat_a:yes"
    await state.update_data(category_a=category_a)
    await state.set_state(RegistrationStates.city)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Ваш город?", reply_markup=get_back_cancel_keyboard())


@router.message(RegistrationStates.city, F.text == "⬅️ Назад")
async def reg_back_city(message: Message, state: FSMContext) -> None:
    """Назад: город -> категория А."""
    await state.set_state(RegistrationStates.category_a)
    await message.answer("Есть права категории А?", reply_markup=get_category_a_keyboard())


@router.message(RegistrationStates.city, F.text)
async def process_city(message: Message, state: FSMContext) -> None:
    """Город и завершение регистрации."""
    await state.update_data(city=message.text.strip()[:100])

    data = await state.get_data()
    role = "admin" if message.from_user.id == SUPERADMIN_ID else "user"

    async with async_session_maker() as session:
        user = User(
            telegram_id=message.from_user.id,
            role=role,
            name=data.get("name"),
            phone=data.get("phone"),
            driving_experience=data.get("driving_experience"),
            motorcycle_type=data.get("motorcycle_type"),
            engine_capacity=data.get("engine_capacity"),
            category_a=data.get("category_a", False),
            city=data.get("city"),
        )
        session.add(user)
        await session.commit()

    show_admin = message.from_user.id == SUPERADMIN_ID
    await state.clear()
    await message.answer(
        "Регистрация завершена.\n\nВыберите действие:",
        reply_markup=get_main_keyboard(show_admin=show_admin),
    )
