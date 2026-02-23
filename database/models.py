"""Модели SQLAlchemy 2.0 для таблиц User, Event, EventRegistration."""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""
    pass


class User(Base):
    """Пользователь бота."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(unique=True, nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), default="user")  # admin | user
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # имя/псевдоним
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    driving_experience: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # стаж в годах
    motorcycle_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    engine_capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # см³
    category_a: Mapped[bool] = mapped_column(Boolean, default=False)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    registrations: Mapped[list["EventRegistration"]] = relationship(
        "EventRegistration", back_populates="user"
    )


class Event(Base):
    """Мероприятие (покатушка, мотопробег и т.д.)."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    route_link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # ссылка на маршрут
    min_experience: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # мин. стаж
    moto_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    min_engine_capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # мин. объём см³
    max_participants: Mapped[int] = mapped_column(Integer, default=0)  # 0 = без лимита
    price: Mapped[int] = mapped_column(Integer, default=0)

    registrations: Mapped[list["EventRegistration"]] = relationship(
        "EventRegistration", back_populates="event"
    )


class EventRegistration(Base):
    """Связь пользователя и мероприятия + статус оплаты."""

    __tablename__ = "event_registrations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False)
    payment_status: Mapped[str] = mapped_column(
        String(30), default="pending"
    )  # pending | paid | refunded

    user: Mapped["User"] = relationship("User", back_populates="registrations")
    event: Mapped["Event"] = relationship("Event", back_populates="registrations")


class SosSignal(Base):
    """SOS-сигнал для учёта и рассылки."""

    __tablename__ = "sos_signals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    problem_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class DoubleRequest(Base):
    """Заявка на двойку (поездка с пассажиром)."""

    __tablename__ = "double_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    date_route: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
