from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import Enum as AlchemyEnum
from sqlalchemy.orm import relationship

from db.db_base import Base
from settings import DEFAULT_STR_LEN, PHONE_NUMBER_LEN


class RoleEnum(str, Enum):
    USER = "U"
    ADMIN = "A"
    MANAGER = "M"


class QuestionEnum(str, Enum):
    FAQ = "Общие вопросы"
    TROUBLESHOOTING = "Проблемы с продуктами"


class User(Base):
    telegram_id = Column(Integer)
    name = Column(String(DEFAULT_STR_LEN), default="Аноним")
    phone = Column(String(PHONE_NUMBER_LEN))
    role = Column(AlchemyEnum(RoleEnum), default=RoleEnum.USER)
    join_date = Column(DateTime, default=datetime.now)
    callback_request = Column(Boolean, default=False)
    callback_request_date = Column(DateTime)
    case_closed_date = Column(DateTime)
    feedbacks = relationship(
        "Feedback", back_populates="author", cascade="all, delete"
    )


class ProductCategory(Base):
    title = Column(String(DEFAULT_STR_LEN), nullable=False)
    response = Column(Text, nullable=False)
    categories = relationship(
        "CategoryType", cascade="all, delete", backref="product_category"
    )


class CategoryType(Base):
    name = Column(String(DEFAULT_STR_LEN), nullable=False)
    product_id = Column(
        Integer,
        ForeignKey("productcategory.id", ondelete="CASCADE"),
        nullable=False,
    )
    url = Column(String(DEFAULT_STR_LEN))
    media = Column(String(DEFAULT_STR_LEN))
    description = Column(Text)


class InformationAboutCompany(Base):
    name = Column(String(DEFAULT_STR_LEN), nullable=False)
    url = Column(String(DEFAULT_STR_LEN), nullable=False)


class CheckCompanyPortfolio(Base):
    project_name = Column(String(DEFAULT_STR_LEN), nullable=False)
    url = Column(String(DEFAULT_STR_LEN), nullable=False)


class Info(Base):
    question_type = Column(AlchemyEnum(QuestionEnum))
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)


class Feedback(Base):
    user = Column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    feedback_text = Column(Text, nullable=False)
    feedback_date = Column(DateTime, default=datetime.now)
    unread = Column(Boolean, default=True)
    author = relationship("User", back_populates="feedbacks")
