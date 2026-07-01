from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.postgres.models import (
    BrandModel,
    PhoneModel,
    RecommendationHistoryModel,
    RecommendationModel,
    UserModel,
)


@dataclass
class DashboardStats:
    users_total: int
    users_today: int
    users_this_month: int
    phones_total: int
    recommendations_total: int
    avg_recommendation_score: float
    most_viewed: list[tuple[int, str, int]]
    most_recommended: list[tuple[int, str, int]]
    top_brands: list[tuple[str, int]]
    trending_phones: list[tuple[int, str, float]]


class AnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_dashboard_stats(self) -> DashboardStats:
        now = datetime.now(UTC)
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        users_total = await self._count(select(func.count()).select_from(UserModel))
        users_today = await self._count(
            select(func.count()).select_from(UserModel).where(UserModel.created_at >= today)
        )
        users_month = await self._count(
            select(func.count()).select_from(UserModel).where(UserModel.created_at >= month)
        )
        phones_total = await self._count(
            select(func.count()).select_from(PhoneModel).where(PhoneModel.is_active.is_(True))
        )
        recs_total = await self._count(select(func.count()).select_from(RecommendationModel))
        avg_score = await self._count(select(func.avg(RecommendationHistoryModel.score))) or 0.0

        viewed = await self._session.execute(
            select(PhoneModel.id, PhoneModel.name, PhoneModel.view_count)
            .where(PhoneModel.is_active.is_(True))
            .order_by(PhoneModel.view_count.desc())
            .limit(5)
        )
        recommended = await self._session.execute(
            select(PhoneModel.id, PhoneModel.name, PhoneModel.recommendation_count)
            .where(PhoneModel.is_active.is_(True))
            .order_by(PhoneModel.recommendation_count.desc())
            .limit(5)
        )
        brands = await self._session.execute(
            select(BrandModel.name, func.count(PhoneModel.id))
            .join(PhoneModel, PhoneModel.brand_id == BrandModel.id)
            .where(PhoneModel.is_active.is_(True))
            .group_by(BrandModel.name)
            .order_by(func.count(PhoneModel.id).desc())
            .limit(5)
        )
        trending = await self._session.execute(
            select(
                PhoneModel.id,
                PhoneModel.name,
                (PhoneModel.view_count + PhoneModel.recommendation_count * 2).label("score"),
            )
            .where(PhoneModel.is_active.is_(True))
            .order_by(func.desc("score"))
            .limit(5)
        )

        return DashboardStats(
            users_total=users_total,
            users_today=users_today,
            users_this_month=users_month,
            phones_total=phones_total,
            recommendations_total=recs_total,
            avg_recommendation_score=round(float(avg_score), 4),
            most_viewed=[(r[0], r[1], r[2]) for r in viewed.all()],
            most_recommended=[(r[0], r[1], r[2]) for r in recommended.all()],
            top_brands=[(r[0], r[1]) for r in brands.all()],
            trending_phones=[(r[0], r[1], float(r[2])) for r in trending.all()],
        )

    async def _count(self, stmt) -> int | float:
        result = await self._session.execute(stmt)
        val = result.scalar_one()
        return val if val is not None else 0
