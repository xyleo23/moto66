"""Роутеры обработчиков."""
from aiogram import Router

from handlers.start import router as start_router
from handlers.registration import router as registration_router
from handlers.main_menu import router as main_menu_router
from handlers.admin import router as admin_router
from handlers.events import router as events_router
from handlers.double import router as double_router
from handlers.sos import router as sos_router
from handlers.payment import router as payment_router

main_router = Router(name="main")
main_router.include_router(start_router, tags=["start"])
main_router.include_router(registration_router, tags=["registration"])
main_router.include_router(main_menu_router, tags=["main_menu"])
main_router.include_router(admin_router, tags=["admin"])
main_router.include_router(events_router, tags=["events"])
main_router.include_router(double_router, tags=["double"])
main_router.include_router(sos_router, tags=["sos"])
main_router.include_router(payment_router, tags=["payment"])
