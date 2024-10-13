from abc import ABC

from aiogram.fsm.state import StatesGroup

from crud.base_crud import CRUDBase


class BaseAdminManager(ABC):
    """
    Базовый абстрактный класс для менеджеров администратора.

    Этот класс определяет общие атрибуты и методы для менеджеров,
    которые будут использоваться для взаимодействия с CRUD-операциями
    и клавиатурами администратора.

    Attributes:
        model_crud (CRUDBase): Объект для выполнения операций CRUD с моделью.
        back_option (str): Данные для возврата в меню.
    """

    def __init__(
        self, model_crud: CRUDBase, back_option: str, states_group: StatesGroup
    ) -> None:
        self.model_crud = model_crud
        self.back_option = back_option
        self.states_group = states_group
