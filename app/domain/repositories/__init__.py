"""Repository interfaces (ports)."""

from abc import ABC, abstractmethod
from decimal import Decimal

from app.domain.entities.brand import Brand
from app.domain.entities.category import Category
from app.domain.entities.phone import Phone
from app.domain.entities.recommendation import Recommendation, RecommendationHistory
from app.domain.entities.user import User, UserPreference
from app.shared.enums import PhoneSortOrder


class IUserRepository(ABC):
    """User persistence port."""

    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> User | None: ...

    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    async def create(self, user: User) -> User: ...

    @abstractmethod
    async def update(self, user: User) -> User: ...

    @abstractmethod
    async def count(self) -> int: ...

    @abstractmethod
    async def save_preference(self, preference: UserPreference) -> UserPreference: ...


class IPhoneRepository(ABC):
    """Phone persistence port."""

    @abstractmethod
    async def get_by_id(self, phone_id: int) -> Phone | None: ...

    @abstractmethod
    async def get_all_active(self) -> list[Phone]: ...

    @abstractmethod
    async def search(
        self,
        *,
        brand_id: int | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        min_ram_gb: int | None = None,
        query: str | None = None,
        sort: PhoneSortOrder = PhoneSortOrder.SCORE,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Phone]: ...

    @abstractmethod
    async def create(self, phone: Phone) -> Phone: ...

    @abstractmethod
    async def update(self, phone: Phone) -> Phone: ...

    @abstractmethod
    async def delete(self, phone_id: int) -> None: ...

    @abstractmethod
    async def increment_view_count(self, phone_id: int) -> None: ...

    @abstractmethod
    async def get_popular(self, limit: int = 10) -> list[Phone]: ...

    @abstractmethod
    async def get_newest(self, limit: int = 10) -> list[Phone]: ...

    @abstractmethod
    async def count(self) -> int: ...


class IBrandRepository(ABC):
    """Brand persistence port."""

    @abstractmethod
    async def get_all(self) -> list[Brand]: ...

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Brand | None: ...

    @abstractmethod
    async def get_by_id(self, brand_id: int) -> Brand | None: ...


class ICategoryRepository(ABC):
    """Category persistence port."""

    @abstractmethod
    async def get_all(self) -> list[Category]: ...

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Category | None: ...


class IRecommendationRepository(ABC):
    """Recommendation persistence port."""

    @abstractmethod
    async def create(self, recommendation: Recommendation) -> Recommendation: ...

    @abstractmethod
    async def save_history(
        self, history: list[RecommendationHistory]
    ) -> list[RecommendationHistory]: ...

    @abstractmethod
    async def count(self) -> int: ...

    @abstractmethod
    async def get_user_history(self, user_id: int, limit: int = 10) -> list[Recommendation]: ...

    @abstractmethod
    async def get_popular_phones(self, limit: int = 10) -> list[tuple[int, str, int]]: ...


class IFavoriteRepository(ABC):
    """User favorites persistence port."""

    @abstractmethod
    async def add(self, user_id: int, phone_id: int) -> None: ...

    @abstractmethod
    async def remove(self, user_id: int, phone_id: int) -> None: ...

    @abstractmethod
    async def get_user_favorites(self, user_id: int) -> list[Phone]: ...

    @abstractmethod
    async def is_favorite(self, user_id: int, phone_id: int) -> bool: ...
