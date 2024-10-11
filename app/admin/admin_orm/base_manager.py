from abc import ABC

from aiogram.fsm.state import State, StatesGroup

from app.admin.keyboards.keyboards import InlineKeyboardManager
from app.crud.base_crud import CRUDBase


class CreateUpdateState(StatesGroup):
    """
    Базовый класс для машинных состояний при
    добавлении или обновлении данных в БД.
    """

    select = State()
    name = State()
    url = State()
    text = State()
    media = State()


class BaseAdminManager(ABC):
    """
    Базовый абстрактный класс для менеджеров администратора.

    Этот класс определяет общие атрибуты и методы для менеджеров,
    которые будут использоваться для взаимодействия с CRUD-операциями
    и клавиатурами администратора.

    Attributes:
        model_crud (CRUDBase): Объект для выполнения операций CRUD с моделью.
        keyboard (InlineKeyboardManager): Менеджер для создания интерактивных клавиатур.
    """

    def __init__(
        self, model_crud: CRUDBase, keyboard: InlineKeyboardManager
    ) -> None:
        self.model_crud = model_crud
        self.keyboard = keyboard
