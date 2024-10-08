"""Импорты класса Base и всех моделей для Alembic."""
from app.core.db import Base # noqa
from app.models.models import (  # noqa
    User,
    ProductCategory,
    CategoryType,
    InformationAboutCompany,
    CheckCompanyPortfolio,
    Info,
    ContactManager,
    Feedback
)
