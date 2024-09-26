from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
import sqlalchemy.dialects.postgresql as pgsql_types

from enum import Enum

from app.core.db import Base


class RoleEnum(str, Enum):
    USER = 'U'
    ADMIN = 'A'
    MANAGER = 'M'


class User(Base):
    """БД модель пользователя."""

    __tablename__ = 'users'

    tg_id: Mapped[int] = mapped_column(
        pgsql_types.INTEGER,
        nullable=False,
        unique=True
    )

    username: Mapped[str] = mapped_column(
        pgsql_types.VARCHAR(150)
    )

    full_name: Mapped[str] = mapped_column(
        pgsql_types.VARCHAR(150)
    )

    phone: Mapped[str] = mapped_column(
        pgsql_types.VARCHAR(25)
    )

    role: Mapped[RoleEnum] = mapped_column(
        pgsql_types.ENUM('U', 'A', 'M'),
        default=RoleEnum.USER
    )

    join_date: Mapped[datetime] = mapped_column(
        pgsql_types.TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )
