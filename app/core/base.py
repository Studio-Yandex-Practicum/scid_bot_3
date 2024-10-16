"""Импорты класса Base и всех моделей для Alembic."""

from core.db import Base  # noqa
from models.models import (  # noqa
    User,
    ProductCategory,
    CategoryType,
    InformationAboutCompany,
    CheckCompanyPortfolio,
    Info,
    ContactManager,
    Feedback,
)
