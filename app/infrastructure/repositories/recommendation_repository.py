"""PostgreSQL recommendation repository."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.recommendation import Recommendation, RecommendationHistory
from app.domain.repositories import IRecommendationRepository
from app.infrastructure.postgres.mappers import map_recommendation
from app.infrastructure.postgres.models import (
    PhoneModel,
    RecommendationHistoryModel,
    RecommendationModel,
)


class RecommendationRepository(IRecommendationRepository):
    """PostgreSQL implementation of IRecommendationRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, recommendation: Recommendation) -> Recommendation:
        model = RecommendationModel(
            user_id=recommendation.user_id,
            preference_id=recommendation.preference_id,
        )
        self._session.add(model)
        await self._session.flush()
        return map_recommendation(model)

    async def save_history(
        self, history: list[RecommendationHistory]
    ) -> list[RecommendationHistory]:
        models = [
            RecommendationHistoryModel(
                recommendation_id=h.recommendation_id,
                phone_id=h.phone_id,
                score=h.score,
                rank=h.rank,
                reason=h.reason,
            )
            for h in history
        ]
        self._session.add_all(models)
        await self._session.flush()
        return history

    async def count(self) -> int:
        result = await self._session.execute(select(func.count()).select_from(RecommendationModel))
        return result.scalar_one()

    async def get_user_history(self, user_id: int, limit: int = 10) -> list[Recommendation]:
        result = await self._session.execute(
            select(RecommendationModel)
            .options(
                selectinload(RecommendationModel.history)
                .selectinload(RecommendationHistoryModel.phone)
                .selectinload(PhoneModel.brand)
            )
            .where(RecommendationModel.user_id == user_id)
            .order_by(RecommendationModel.created_at.desc())
            .limit(limit)
        )
        return [map_recommendation(m) for m in result.scalars().all()]

    async def get_popular_phones(self, limit: int = 10) -> list[tuple[int, str, int]]:
        result = await self._session.execute(
            select(
                PhoneModel.id,
                PhoneModel.name,
                PhoneModel.recommendation_count,
            )
            .where(PhoneModel.is_active.is_(True))
            .order_by(PhoneModel.recommendation_count.desc())
            .limit(limit)
        )
        return [(row[0], row[1], row[2]) for row in result.all()]
