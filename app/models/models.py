from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import sqlalchemy.dialects.postgresql as pgsql_types

from enum import Enum

from core.db import Base


class RoleEnum(str, Enum):
    USER = "Пользователь"
    ADMIN = "Админ"
    MANAGER = "Mенеджер"


class QuestionEnum(str, Enum):
    GENERAL_QUESTIONS = "Общие вопросы"
    PROBLEMS_WITH_PRODUCTS = "Проблемы с продуктами"


class User(Base):
    """БД модель пользователя."""

    tg_id: Mapped[int] = mapped_column(
        pgsql_types.BIGINT, nullable=False, unique=True
    )

    role: Mapped[RoleEnum] = mapped_column(
        pgsql_types.ENUM(RoleEnum, name="role_enum", create_type=False),
        default=RoleEnum.USER,
    )

    join_date: Mapped[datetime] = mapped_column(
        pgsql_types.TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class ProductCategory(Base):
    """БД модель продуктов и услуг."""

    name: Mapped[str] = mapped_column(pgsql_types.VARCHAR(150))

    description: Mapped[str] = mapped_column(pgsql_types.TEXT)

    categories = relationship(
        "CategoryType",
        cascade="all, delete",
        back_populates="product_category",
    )


class CategoryType(Base):
    """БД модель типов категорий."""

    name: Mapped[str] = mapped_column(pgsql_types.VARCHAR(150), nullable=False)

    product_id: Mapped[int] = mapped_column(
        ForeignKey("productcategory.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    url: Mapped[str] = mapped_column(pgsql_types.VARCHAR(128), nullable=True)

    media: Mapped[str] = mapped_column(pgsql_types.VARCHAR(128), nullable=True)

    description: Mapped[str] = mapped_column(pgsql_types.TEXT, nullable=True)

    product_category = relationship(
        "ProductCategory", back_populates="categories"
    )


class InformationAboutCompany(Base):
    """Бд модель информации о компании."""

    name: Mapped[str] = mapped_column(pgsql_types.VARCHAR(48), nullable=False)

    url: Mapped[str] = mapped_column(pgsql_types.VARCHAR(128))


class CheckCompanyPortfolio(Base):
    """Бд модель информации о проектах."""

    name: Mapped[str] = mapped_column(pgsql_types.VARCHAR(48), nullable=False)

    url: Mapped[str] = mapped_column(pgsql_types.VARCHAR(128))


class Info(Base):
    """Бд модель F.A.Q."""

    question_type: Mapped[QuestionEnum] = mapped_column(
        pgsql_types.ENUM(
            QuestionEnum, name="question_enum", create_type=False
        ),
        nullable=False,
    )

    question: Mapped[str] = mapped_column(pgsql_types.TEXT, unique=True)

    answer: Mapped[str] = mapped_column(pgsql_types.TEXT, nullable=False)


class ContactManager(Base):
    """Бд модель заявки к менеджеру."""

    first_name: Mapped[str] = mapped_column(
        pgsql_types.VARCHAR(32), nullable=False
    )

    phone_number: Mapped[str] = mapped_column(
        pgsql_types.VARCHAR(25), nullable=False
    )

    need_support: Mapped[bool] = mapped_column(
        pgsql_types.BOOLEAN, default=False, nullable=False
    )

    need_contact_with_manager: Mapped[bool] = mapped_column(
        pgsql_types.BOOLEAN, default=False, nullable=False
    )

    shipping_date: Mapped[datetime] = mapped_column(
        pgsql_types.TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    shipping_date_close: Mapped[datetime] = mapped_column(
        pgsql_types.TIMESTAMP(timezone=True), nullable=True
    )


class Feedback(Base):
    """БД модель для отзывов."""

    user: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    feedback_text: Mapped[str] = mapped_column(
        pgsql_types.TEXT, nullable=False
    )
    feedback_date: Mapped[datetime] = mapped_column(
        pgsql_types.TIMESTAMP, default=datetime.now
    )
    rating: Mapped[int] = mapped_column(pgsql_types.INTEGER, nullable=False)
