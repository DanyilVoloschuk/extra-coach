from fastapi import FastAPI, Request, Depends, Response, status
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv
from sqladmin import Admin, ModelView

from application.services.telegram_message_service import TelegramMessageService
from infrastructure.config.environment import initialize_environment
from infrastructure.config.settings import get_settings
from infrastructure.database import models
from infrastructure.database.session import get_db
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession

load_dotenv()

settings = get_settings()
initialize_environment()

app = FastAPI()

# Create the async engine
engine = create_async_engine(settings.DATABASE_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        valid_username = settings.ADMIN_USERNAME
        valid_password = settings.ADMIN_PASSWORD

        if username == valid_username and password == valid_password:
            request.session.update({"token": "..."})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return False
        return True


# Initialize authentication
authentication_backend = AdminAuth(secret_key="my-super-duper-12313seada")

# Update the Admin initialization to include authentication
admin = Admin(
    app,
    engine,
    authentication_backend=authentication_backend
)


class UserAdmin(ModelView, model=models.User):
    column_list = [models.User.id, models.User.name, models.User.is_active]


class ChatAdmin(ModelView, model=models.UserChat):
    column_list = [
        models.UserChat.id,
        models.UserChat.telegram_chat_id,
        models.UserChat.stage,
        models.UserChat.user,
    ]


class NutritionalDataAdmin(ModelView, model=models.NutritionalData):
    column_list = [
        models.NutritionalData.id,
        models.NutritionalData.name,
        models.NutritionalData.user,
        models.NutritionalData.type,
        models.NutritionalData.day_counter,
    ]

    column_searchable_list = [
        models.NutritionalData.name,
        models.NutritionalData.type,
        models.NutritionalData.day_counter,
    ]

    column_sortable_list = [
        models.NutritionalData.name,
        models.NutritionalData.type,
        models.NutritionalData.day_counter,
    ]


admin.add_view(UserAdmin)
admin.add_view(ChatAdmin)
admin.add_view(NutritionalDataAdmin)


@app.post("/webhook")
async def webhook_handler(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    async with async_session() as session:
        data = await request.json()
        telegram_service = TelegramMessageService(db=session)
        await telegram_service.handle_webhook_message(
            message=data
        )
        response.status_code = status.HTTP_200_OK
        return {"status": "ok"}


@app.get("/")
async def root():
    from infrastructure.database.session import init_db
    await init_db()
    return {"message": "Telegram Bot is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8447, reload=True)