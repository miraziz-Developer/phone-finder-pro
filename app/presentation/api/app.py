from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel

from app.application.services.analytics import AnalyticsService
from app.core.config import Settings, get_settings
from app.core.database.unit_of_work import UnitOfWork

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


class Token(BaseModel):
    access_token: str
    token_type: str


class PhoneResponse(BaseModel):
    id: int
    name: str
    brand: str | None
    price_usd: str
    ram_gb: int
    storage_gb: int
    is_active: bool


class StatsResponse(BaseModel):
    users_total: int
    phones_total: int
    recommendations_total: int
    avg_recommendation_score: float


def create_api_app(settings: Settings | None = None) -> FastAPI:
    cfg = settings or get_settings()

    app = FastAPI(
        title=f"{cfg.app_name} Admin API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    def _create_token(username: str) -> str:
        expire = datetime.now(UTC) + timedelta(minutes=cfg.jwt_expire_minutes)
        return jwt.encode(
            {"sub": username, "exp": expire},
            cfg.jwt_secret_key,
            algorithm=cfg.jwt_algorithm,
        )

    async def _auth(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
        try:
            payload = jwt.decode(token, cfg.jwt_secret_key, algorithms=[cfg.jwt_algorithm])
            username = payload.get("sub")
            if not username:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            return str(username)
        except JWTError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from exc

    @app.post(f"{cfg.api_prefix}/auth/token", response_model=Token)
    async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
        if form.username != cfg.api_admin_username or form.password != cfg.api_admin_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )
        return Token(access_token=_create_token(form.username), token_type="bearer")

    @app.get(f"{cfg.api_prefix}/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get(f"{cfg.api_prefix}/phones", response_model=list[PhoneResponse])
    async def list_phones(
        _: Annotated[str, Depends(_auth)],
        offset: int = 0,
        limit: int = 20,
    ) -> list[PhoneResponse]:
        async with UnitOfWork() as uow:
            phones = await uow.phones.search(offset=offset, limit=limit)
            return [
                PhoneResponse(
                    id=p.id or 0,
                    name=p.name,
                    brand=p.brand_name,
                    price_usd=f"${p.price:,.0f}",
                    ram_gb=p.ram_gb,
                    storage_gb=p.storage_gb,
                    is_active=p.is_active,
                )
                for p in phones
            ]

    @app.get(f"{cfg.api_prefix}/stats", response_model=StatsResponse)
    async def get_stats(_: Annotated[str, Depends(_auth)]) -> StatsResponse:
        async with UnitOfWork() as uow:
            stats = await AnalyticsService(uow.session).get_dashboard_stats()
            return StatsResponse(
                users_total=stats.users_total,
                phones_total=stats.phones_total,
                recommendations_total=stats.recommendations_total,
                avg_recommendation_score=stats.avg_recommendation_score,
            )

    return app
