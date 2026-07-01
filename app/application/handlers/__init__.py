"""Application command and query handlers."""

from decimal import Decimal

from app.application.commands import (
    CreateRecommendationCommand,
    RegisterUserCommand,
    ToggleFavoriteCommand,
)
from app.application.dto import RecommendationResultDTO
from app.application.queries import (
    GetPhoneByIdQuery,
    GetRecommendationHistoryQuery,
    GetUserFavoritesQuery,
    SearchPhonesQuery,
)
from app.core.database.unit_of_work import UnitOfWork
from app.core.logging import get_logger
from app.domain.entities.recommendation import Recommendation, RecommendationHistory
from app.domain.entities.user import User, UserPreference
from app.domain.services.recommendation_engine import RecommendationEngine
from app.domain.value_objects import BudgetRange, UserPreferencesInput
from app.shared.enums import BrandName, UseCase
from app.shared.exceptions import NotFoundError, RecommendationError

logger = get_logger(__name__)


class RegisterUserHandler:
    """Handle user registration or profile update."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: RegisterUserCommand) -> User:
        """Register a new user or update existing profile."""
        existing = await self._uow.users.get_by_telegram_id(command.telegram_id)
        if existing:
            existing.username = command.username
            existing.first_name = command.first_name
            existing.last_name = command.last_name
            existing.language_code = command.language_code
            return await self._uow.users.update(existing)

        user = User(
            id=None,
            telegram_id=command.telegram_id,
            username=command.username,
            first_name=command.first_name,
            last_name=command.last_name,
            language_code=command.language_code,
            is_active=True,
        )
        return await self._uow.users.create(user)


class CreateRecommendationHandler:
    """Handle recommendation generation workflow."""

    def __init__(
        self,
        uow: UnitOfWork,
        engine: RecommendationEngine | None = None,
    ) -> None:
        self._uow = uow
        self._engine = engine or RecommendationEngine()

    async def handle(self, command: CreateRecommendationCommand) -> RecommendationResultDTO:
        """Generate recommendations based on user preferences."""
        req = command.request

        user = await self._uow.users.get_by_telegram_id(req.telegram_id)
        if user is None or user.id is None:
            raise NotFoundError("User", req.telegram_id)

        preference = UserPreference(
            id=None,
            user_id=user.id,
            budget_min=req.budget_min,
            budget_max=req.budget_max,
            use_case=req.use_case,
            preferred_brand=req.preferred_brand,
            min_ram_gb=req.min_ram_gb,
            min_storage_gb=req.min_storage_gb,
            requires_5g=req.requires_5g,
            requires_nfc=req.requires_nfc,
            requires_wireless_charging=req.requires_wireless_charging,
            requires_esim=req.requires_esim,
            requires_amoled=req.requires_amoled,
            requires_high_refresh=req.requires_high_refresh,
        )
        saved_pref = await self._uow.users.save_preference(preference)

        prefs_input = UserPreferencesInput(
            budget=BudgetRange(
                min_amount=Decimal(str(req.budget_min)),
                max_amount=Decimal(str(req.budget_max)),
            ),
            use_case=UseCase(req.use_case),
            preferred_brand=BrandName(req.preferred_brand),
            min_ram_gb=req.min_ram_gb,
            min_storage_gb=req.min_storage_gb,
            requires_5g=req.requires_5g,
            requires_nfc=req.requires_nfc,
            requires_wireless_charging=req.requires_wireless_charging,
            requires_esim=req.requires_esim,
            requires_amoled=req.requires_amoled,
            requires_high_refresh=req.requires_high_refresh,
        )

        phones = await self._uow.phones.get_all_active()
        if not phones:
            raise RecommendationError("No phones available in catalog")

        scored = self._engine.score_phones(phones, prefs_input)
        if not scored:
            raise RecommendationError("No phones match your criteria. Try adjusting preferences.")

        recommendation = Recommendation(
            id=None,
            user_id=user.id,
            preference_id=saved_pref.id or 0,
        )
        saved_rec = await self._uow.recommendations.create(recommendation)

        history = [
            RecommendationHistory(
                id=None,
                recommendation_id=saved_rec.id or 0,
                phone_id=s.phone_id,
                score=s.score,
                rank=idx + 1,
                reason=s.reason,
            )
            for idx, s in enumerate(scored)
        ]
        await self._uow.recommendations.save_history(history)

        phone_details = []
        for s in scored:
            phone = await self._uow.phones.get_by_id(s.phone_id)
            if phone:
                phone_details.append(phone)

        logger.info(
            "recommendation_created",
            user_id=user.id,
            recommendation_id=saved_rec.id,
            results_count=len(scored),
        )

        return RecommendationResultDTO(
            recommendation_id=saved_rec.id or 0,
            phones=scored,
            phone_details=phone_details,
        )


class ToggleFavoriteHandler:
    """Handle adding/removing favorites."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: ToggleFavoriteCommand) -> bool:
        """Toggle favorite status. Returns True if now favorited."""
        is_fav = await self._uow.favorites.is_favorite(command.user_id, command.phone_id)
        if is_fav:
            await self._uow.favorites.remove(command.user_id, command.phone_id)
            return False
        await self._uow.favorites.add(command.user_id, command.phone_id)
        return True


class GetPhoneByIdHandler:
    """Handle phone detail query."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self, query: GetPhoneByIdQuery):
        phone = await self._uow.phones.get_by_id(query.phone_id)
        if phone is None:
            raise NotFoundError("Phone", query.phone_id)
        await self._uow.phones.increment_view_count(query.phone_id)
        return phone


class SearchPhonesHandler:
    """Handle phone search query."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self, query: SearchPhonesQuery):
        return await self._uow.phones.search(
            brand_id=query.brand_id,
            min_price=Decimal(str(query.min_price)) if query.min_price else None,
            max_price=Decimal(str(query.max_price)) if query.max_price else None,
            query=query.query,
            sort=query.sort,
            offset=query.offset,
            limit=query.limit,
        )


class GetUserFavoritesHandler:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self, query: GetUserFavoritesQuery):
        return await self._uow.favorites.get_user_favorites(query.user_id)


class GetRecommendationHistoryHandler:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self, query: GetRecommendationHistoryQuery):
        return await self._uow.recommendations.get_user_history(query.user_id, query.limit)
