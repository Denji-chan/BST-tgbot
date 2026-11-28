from aiogram import Router

from . import error_handler

router = Router(name="errors")
router.include_router(error_handler.router)
