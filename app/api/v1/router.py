from fastapi import APIRouter
from app.modules.services.auth.auth_router import router as auth_router
from app.modules.services.credits.routes import router as credits_router
from app.modules.products.generator.routes import router as generator_router
from app.modules.services.payments.routes import router as payments_router
from app.modules.products.reports.routes import router as reports_router
from app.modules.products.shop.routes import router as shop_router
from app.api.v1.views import router as views
from app.api.v1.stripe import router as stripe_webhook_router
from app.api.v1.account import router as account_router
from app.api.v1.report import report_router


api_router = APIRouter()

api_router.include_router(stripe_webhook_router, prefix="/stripe", tags=["billing"])
api_router.include_router(account_router, prefix="/account", tags=["account"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(credits_router, prefix="/credits", tags=["credits"])
api_router.include_router(generator_router, prefix="/generate", tags=["generator"])
api_router.include_router(payments_router, prefix="/payments", tags=["payments"])
api_router.include_router(reports_router, prefix="/reports", tags=["reports"])
api_router.include_router(shop_router, prefix="/shop", tags=["shop"])
api_router.include_router(views, tags=["views"])
api_router.include_router(report_router, prefix="/report", tags=["report"])

