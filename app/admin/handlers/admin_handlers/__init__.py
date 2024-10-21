from aiogram import Router

from .admin import admin_menu_router
from .admin_info_handlers import info_router
from .admin_about_company_handlers import about_router
from .admin_portfolio_handlers import portfolio_router
from .admin_product_handlers import product_router
from .admin_category_handlers import category_router
from .admin_special_handlers import admin_special_router
from .superuser_handlers import superuser_router
from .admin_main_handlers import admin_main_router

admin_router = Router()
admin_router.include_router(admin_menu_router)
admin_router.include_router(info_router)
admin_router.include_router(about_router)
admin_router.include_router(portfolio_router)
admin_router.include_router(product_router)
admin_router.include_router(category_router)
admin_router.include_router(superuser_router)
admin_router.include_router(admin_special_router)
admin_router.include_router(admin_main_router)
