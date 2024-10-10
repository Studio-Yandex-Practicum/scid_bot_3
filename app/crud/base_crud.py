from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDBase:
    def __init__(self, model) -> None:
        self.model = model

    async def create(
        self,
        obj_in: dict,
        session: AsyncSession,
    ):
        db_obj = self.model(**obj_in)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(self, db_obj, obj_in, session: AsyncSession):
        """Внести изменения в объект модели в БД."""
        obj_fields = db_obj.__dict__
        for field in obj_fields:
            if field in obj_in:
                setattr(db_obj, field, obj_in[field])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get(
        self,
        obj_id: int,
        session: AsyncSession,
    ):
        """Получить объект модели по ее id."""
        db_obj = await session.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        return db_obj.scalars().first()

    async def get_multi(self, session: AsyncSession):
        """Получить список всех объектов модели из БД."""
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    async def remove(self, db_obj, session: AsyncSession):
        """Удалить объект модели из БД."""
        await session.delete(db_obj)
        await session.commit()
        return db_obj

    async def get_by_string(self, string: str, session: AsyncSession):
        """Получить объект модели из БД по его названию."""
        db_obj = await session.execute(
            select(self.model).where(self.model.name == string)
        )
        return db_obj.scalars().first()
