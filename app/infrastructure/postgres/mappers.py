"""ORM to domain entity mappers."""

from app.domain.entities.brand import Brand
from app.domain.entities.category import Category
from app.domain.entities.phone import Phone, PhoneFeatures, PhoneImage
from app.domain.entities.recommendation import Recommendation, RecommendationHistory, ScoredPhone
from app.domain.entities.user import User, UserPreference
from app.infrastructure.postgres.models import (
    BrandModel,
    CategoryModel,
    PhoneFeatureModel,
    PhoneImageModel,
    PhoneModel,
    RecommendationHistoryModel,
    RecommendationModel,
    UserModel,
    UserPreferenceModel,
)


def map_user(model: UserModel) -> User:
    """Map UserModel to User entity."""
    return User(
        id=model.id,
        telegram_id=model.telegram_id,
        username=model.username,
        first_name=model.first_name,
        last_name=model.last_name,
        language_code=model.language_code,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def map_user_preference(model: UserPreferenceModel) -> UserPreference:
    """Map UserPreferenceModel to UserPreference entity."""
    return UserPreference(
        id=model.id,
        user_id=model.user_id,
        budget_min=model.budget_min,
        budget_max=model.budget_max,
        use_case=model.use_case,
        preferred_brand=model.preferred_brand,
        min_ram_gb=model.min_ram_gb,
        min_storage_gb=model.min_storage_gb,
        requires_5g=model.requires_5g,
        requires_nfc=model.requires_nfc,
        requires_wireless_charging=model.requires_wireless_charging,
        requires_esim=model.requires_esim,
        requires_amoled=model.requires_amoled,
        requires_high_refresh=model.requires_high_refresh,
        created_at=model.created_at,
    )


def map_brand(model: BrandModel) -> Brand:
    """Map BrandModel to Brand entity."""
    return Brand(
        id=model.id,
        name=model.name,
        slug=model.slug,
        logo_url=model.logo_url,
        is_active=model.is_active,
        created_at=model.created_at,
    )


def map_category(model: CategoryModel) -> Category:
    """Map CategoryModel to Category entity."""
    return Category(
        id=model.id,
        name=model.name,
        slug=model.slug,
        description=model.description,
        created_at=model.created_at,
    )


def map_phone_features(model: PhoneFeatureModel) -> PhoneFeatures:
    """Map PhoneFeatureModel to PhoneFeatures entity."""
    return PhoneFeatures(
        id=model.id,
        phone_id=model.phone_id,
        has_5g=model.has_5g,
        has_nfc=model.has_nfc,
        has_wireless_charging=model.has_wireless_charging,
        has_esim=model.has_esim,
        has_amoled=model.has_amoled,
        has_high_refresh=model.has_high_refresh,
        has_fingerprint=getattr(model, "has_fingerprint", True),
        refresh_rate_hz=model.refresh_rate_hz,
        display_type=getattr(model, "display_type", "AMOLED"),
        display_size_inches=model.display_size_inches,
        display_resolution=model.display_resolution,
        ip_rating=model.ip_rating,
        os_version=model.os_version,
        sim_type=getattr(model, "sim_type", None),
        bluetooth=getattr(model, "bluetooth", None),
        wifi=getattr(model, "wifi", None),
        usb_type=getattr(model, "usb_type", None),
        stereo_speakers=getattr(model, "stereo_speakers", False),
    )


def map_phone_image(model: PhoneImageModel) -> PhoneImage:
    """Map PhoneImageModel to PhoneImage entity."""
    return PhoneImage(
        id=model.id,
        phone_id=model.phone_id,
        url=model.url,
        is_primary=model.is_primary,
        sort_order=model.sort_order,
    )


def map_phone(model: PhoneModel, *, load_relations: bool = True) -> Phone:
    """Map PhoneModel to Phone entity with optional relations."""
    phone = Phone(
        id=model.id,
        brand_id=model.brand_id,
        category_id=model.category_id,
        name=model.name,
        slug=model.slug,
        model_year=model.model_year,
        price=model.price,
        currency=model.currency,
        cpu=model.cpu,
        gpu=model.gpu,
        ram_gb=model.ram_gb,
        storage_gb=model.storage_gb,
        battery_mah=model.battery_mah,
        camera_main_mp=model.camera_main_mp,
        camera_ultra_mp=model.camera_ultra_mp,
        camera_tele_mp=model.camera_tele_mp,
        camera_front_mp=model.camera_front_mp,
        performance_score=model.performance_score,
        camera_score=model.camera_score,
        battery_score=model.battery_score,
        display_score=model.display_score,
        original_price=model.original_price,
        discount_percent=model.discount_percent,
        description=model.description,
        charging_watts=model.charging_watts,
        rating_avg=model.rating_avg,
        review_count=model.review_count,
        weight_grams=model.weight_grams,
        dimensions=model.dimensions,
        colors=list(model.colors or []),
        advantages=list(model.advantages or []),
        disadvantages=list(model.disadvantages or []),
        is_active=model.is_active,
        view_count=model.view_count,
        recommendation_count=model.recommendation_count,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )

    if load_relations:
        if model.brand:
            phone.brand_name = model.brand.name
        if model.category:
            phone.category_name = model.category.name
        if model.features:
            phone.features = map_phone_features(model.features)
        if model.images:
            phone.images = [map_phone_image(img) for img in model.images]

    return phone


def map_recommendation(model: RecommendationModel, *, load_history: bool = True) -> Recommendation:
    results: list[ScoredPhone] = []
    if load_history:
        history = model.history
        if history:
            for h in history:
                results.append(
                    ScoredPhone(
                        phone_id=h.phone_id,
                        phone_name=h.phone.name if h.phone else "Unknown",
                        brand_name=h.phone.brand.name if h.phone and h.phone.brand else "Unknown",
                        price=h.phone.price if h.phone else 0,
                        score=h.score,
                        reason=h.reason,
                    )
                )

    return Recommendation(
        id=model.id,
        user_id=model.user_id,
        preference_id=model.preference_id,
        created_at=model.created_at,
        results=results,
    )


def map_recommendation_history(model: RecommendationHistoryModel) -> RecommendationHistory:
    """Map RecommendationHistoryModel to RecommendationHistory entity."""
    return RecommendationHistory(
        id=model.id,
        recommendation_id=model.recommendation_id,
        phone_id=model.phone_id,
        score=model.score,
        rank=model.rank,
        reason=model.reason,
        created_at=model.created_at,
    )
