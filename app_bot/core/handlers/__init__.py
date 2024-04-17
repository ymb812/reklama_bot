from core.handlers.welcome import router as welcome_router
from core.handlers.basic import router as basic_router
from core.handlers.admin import router as admin_router
from core.handlers.buyer import router as buyer_router
from core.handlers.manager import router as manager_router
from core.handlers.free_sub import router as free_sub_router


routers = [welcome_router, basic_router, admin_router, buyer_router, manager_router, free_sub_router]
