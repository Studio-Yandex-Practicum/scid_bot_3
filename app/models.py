from datetime import datetime

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String,
                        Text)

from db.db_base import Base


class User(Base):
    tg_id = Column(Integer, nullable=False)
    username = Column(String(150))
    full_name = Column(String(150))
    phone = Column(Integer)
    join_date = Column(DateTime(default=datetime.now))


class CallRequest(Base):
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    question_type = Column(String(150))
    arrival_time = Column(DateTime(default=datetime.now))


class CompanyInfo(Base):
    info_type = Column(String(150), nullable=False)
    description = Column(Text)
    media = Column(String(150))


class FAQ(Base):
    question = Column(Text, nullable=False)
    answer = Column(Text)


class ProductProblems(Base):
    question = Column(Text, nullable=False)
    answer = Column(Text)


class ProjectsInfo(Base):
    project_name = Column(String(150), nullable=False)
    project_url = Column(String(250))
    media = Column(String(150))


class Websites(Base):
    website_type = Column(String(150), nullable=False)
    type_url = Column(String(250))
    description = Column(Text)
    media = Column(String(150))


class Portals(Base):
    portal_type = Column(String(150), nullable=False)
    type_url = Column(String(250))
    description = Column(Text)
    media = Column(String(150))


class MobileApps(Base):
    app_type = Column(String(150), nullable=False)
    type_url = Column(String(250))
    description = Column(Text)
    media = Column(String(150))


class LoyaltyPrograms(Base):
    loyalty_type = Column(String(150), nullable=False)
    is_active = Column(Boolean, default=True)
    description = Column(Text)


class Kiosk365(Base):
    info_type = Column(String(150), nullable=False)
    description = Column(Text)
    media = Column(String(150))


class NBPEJA(Base):
    info_type = Column(String(150), nullable=False)
    description = Column(Text)
    media = Column(String(150))


class Hosting(Base):
    info_type = Column(String(150), nullable=False)
    description = Column(Text)
