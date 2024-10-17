from datetime import datetime
from enum import Enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import sqlalchemy.dialects.postgresql as pgsql_types

from core.db import Base
import models.models_const as mc


class RoleEnum(str, Enum):
    USER = "Пользователь"
    ADMIN = "Администратор"
    MANAGER = "Mенеджер"

    def __str__(self) -> str:
        return self.value


class QuestionEnum(str, Enum):
    GENERAL_QUESTIONS = "Общие вопросы"
    PROBLEMS_WITH_PRODUCTS = "Проблемы с продуктами"


class User(Base):
    """БД модель пользователя."""

    tg_id: Mapped[int] = mapped_column(
        pgsql_types.BIGINT, nullable=False, unique=True
    )

    name: Mapped[str] = mapped_column(
        pgsql_types.VARCHAR(mc.NAME_LENGTH), default="Аноним"
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
    closed_requests: Mapped[list["ContactManager"]] = relationship(
        "ContactManager", back_populates="manager"
    )


class ProductCategory(Base):
    """БД модель продуктов и услуг."""

    name: Mapped[str] = mapped_column(pgsql_types.VARCHAR(mc.NAME_LENGTH))

    description: Mapped[str] = mapped_column(pgsql_types.TEXT)

    categories = relationship(
        "CategoryType",
        cascade="all, delete",
        back_populates="product_category",
    )


class CategoryType(Base):
    """БД модель типов категорий."""

    name: Mapped[str] = mapped_column(
        pgsql_types.VARCHAR(mc.NAME_LENGTH), nullable=False
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("productcategory.id", ondelete="CASCADE"),
        ForeignKey("productcategory.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    url: Mapped[str] = mapped_column(
        pgsql_types.VARCHAR(mc.URL_LENGTH), nullable=True
    )

    media: Mapped[str] = mapped_column(
        pgsql_types.VARCHAR(mc.MEDIA_URL), nullable=True
    )

    description: Mapped[str] = mapped_column(pgsql_types.TEXT, nullable=True)

    product_category = relationship(
        "ProductCategory", back_populates="categories"
    )


class InformationAboutCompany(Base):
    """Бд модель информации о компании."""

    name: Mapped[str] = mapped_column(
        pgsql_types.VARCHAR(mc.NAME_LENGTH), nullable=False
    )

    url: Mapped[str] = mapped_column(pgsql_types.VARCHAR(mc.URL_LENGTH))


class CheckCompanyPortfolio(Base):
    """Бд модель информации о проектах."""

    name: Mapped[str] = mapped_column(
        pgsql_types.VARCHAR(mc.NAME_LENGTH), nullable=False
    )

    url: Mapped[str] = mapped_column(pgsql_types.VARCHAR(mc.URL_LENGTH))


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
        pgsql_types.VARCHAR(mc.FIRST_NAME_LENGHT), nullable=False
    )

    phone_number: Mapped[str] = mapped_column(
        pgsql_types.VARCHAR(mc.PHONE_NUMBER_LENGHT), nullable=False
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

    manager_id: Mapped[int] = mapped_column(
        pgsql_types.BIGINT, ForeignKey('user.tg_id'), nullable=True
    )

    manager: Mapped[User] = relationship(
        "User", back_populates="closed_requests"
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
