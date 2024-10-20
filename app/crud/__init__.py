from .base_crud import CRUDBase
from .category_product import category_product_crud  # noqa
from .feedback_crud import feedback_crud  # noqa
from .info_crud import info_crud  # noqa
from .portfolio_projects_crud import portfolio_crud  # noqa
from .product_crud import products_crud  # noqa
from .user_crud import user_crud  # noqa
from models.models import InformationAboutCompany

company_info_crud = CRUDBase(InformationAboutCompany)
