"""SQLAlchemy 2.0 declarative models."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""

    pass


class UserModel(Base):
    """Telegram user ORM model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language_code: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    preferences: Mapped[list["UserPreferenceModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    recommendations: Mapped[list["RecommendationModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    favorites: Mapped[list["FavoriteModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    reviews: Mapped[list["PhoneReviewModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class BrandModel(Base):
    """Brand ORM model."""

    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    phones: Mapped[list["PhoneModel"]] = relationship(back_populates="brand")


class CategoryModel(Base):
    """Category ORM model."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    phones: Mapped[list["PhoneModel"]] = relationship(back_populates="category")


class PhoneModel(Base):
    """Phone ORM model."""

    __tablename__ = "phones"
    __table_args__ = (
        Index("ix_phones_price", "price"),
        Index("ix_phones_ram_storage", "ram_gb", "storage_gb"),
        Index("ix_phones_active_price", "is_active", "price"),
        Index("ix_phones_model_year", "model_year"),
        Index("ix_phones_rating", "rating_avg"),
        Index("ix_phones_trending", "view_count", "recommendation_count"),
        UniqueConstraint("slug", name="uq_phones_slug"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    brand_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("brands.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    model_year: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    original_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    discount_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cpu: Mapped[str] = mapped_column(String(255), nullable=False)
    gpu: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ram_gb: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_gb: Mapped[int] = mapped_column(Integer, nullable=False)
    battery_mah: Mapped[int] = mapped_column(Integer, nullable=False)
    charging_watts: Mapped[int | None] = mapped_column(Integer, nullable=True)
    camera_main_mp: Mapped[float] = mapped_column(Float, nullable=False)
    camera_ultra_mp: Mapped[float | None] = mapped_column(Float, nullable=True)
    camera_tele_mp: Mapped[float | None] = mapped_column(Float, nullable=True)
    camera_front_mp: Mapped[float] = mapped_column(Float, nullable=False)
    performance_score: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    camera_score: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    battery_score: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    display_score: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    rating_avg: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    review_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    weight_grams: Mapped[float | None] = mapped_column(Float, nullable=True)
    dimensions: Mapped[str | None] = mapped_column(String(50), nullable=True)
    colors: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    release_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    advantages: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    disadvantages: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    recommendation_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    brand: Mapped["BrandModel"] = relationship(back_populates="phones")
    category: Mapped["CategoryModel"] = relationship(back_populates="phones")
    features: Mapped["PhoneFeatureModel | None"] = relationship(
        back_populates="phone", uselist=False, cascade="all, delete-orphan"
    )
    images: Mapped[list["PhoneImageModel"]] = relationship(
        back_populates="phone", cascade="all, delete-orphan"
    )
    reviews: Mapped[list["PhoneReviewModel"]] = relationship(
        back_populates="phone", cascade="all, delete-orphan"
    )
    price_history: Mapped[list["PhonePriceHistoryModel"]] = relationship(
        back_populates="phone", cascade="all, delete-orphan"
    )


class PhoneFeatureModel(Base):
    """Phone features ORM model."""

    __tablename__ = "phone_features"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phone_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("phones.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    has_5g: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_nfc: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_wireless_charging: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_esim: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_amoled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_high_refresh: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_fingerprint: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    refresh_rate_hz: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    display_type: Mapped[str] = mapped_column(String(50), default="AMOLED", nullable=False)
    display_size_inches: Mapped[float] = mapped_column(Float, nullable=False)
    display_resolution: Mapped[str] = mapped_column(String(50), nullable=False)
    ip_rating: Mapped[str | None] = mapped_column(String(20), nullable=True)
    os_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sim_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    bluetooth: Mapped[str | None] = mapped_column(String(50), nullable=True)
    wifi: Mapped[str | None] = mapped_column(String(50), nullable=True)
    usb_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    stereo_speakers: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    phone: Mapped["PhoneModel"] = relationship(back_populates="features")


class PhoneImageModel(Base):
    """Phone image ORM model."""

    __tablename__ = "phone_images"
    __table_args__ = (Index("ix_phone_images_phone_sort", "phone_id", "sort_order"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phone_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("phones.id", ondelete="CASCADE"), nullable=False, index=True
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    phone: Mapped["PhoneModel"] = relationship(back_populates="images")


class UserPreferenceModel(Base):
    """User preference ORM model."""

    __tablename__ = "user_preferences"
    __table_args__ = (Index("ix_user_preferences_user_created", "user_id", "created_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    budget_min: Mapped[float] = mapped_column(Float, nullable=False)
    budget_max: Mapped[float] = mapped_column(Float, nullable=False)
    use_case: Mapped[str] = mapped_column(String(50), nullable=False)
    preferred_brand: Mapped[str | None] = mapped_column(String(50), nullable=True)
    min_ram_gb: Mapped[int] = mapped_column(Integer, nullable=False)
    min_storage_gb: Mapped[int] = mapped_column(Integer, nullable=False)
    requires_5g: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_nfc: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_wireless_charging: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_esim: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_amoled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_high_refresh: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["UserModel"] = relationship(back_populates="preferences")
    recommendations: Mapped[list["RecommendationModel"]] = relationship(back_populates="preference")


class RecommendationModel(Base):
    """Recommendation session ORM model."""

    __tablename__ = "recommendations"
    __table_args__ = (Index("ix_recommendations_user_created", "user_id", "created_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    preference_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_preferences.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["UserModel"] = relationship(back_populates="recommendations")
    preference: Mapped["UserPreferenceModel"] = relationship(back_populates="recommendations")
    history: Mapped[list["RecommendationHistoryModel"]] = relationship(
        back_populates="recommendation", cascade="all, delete-orphan"
    )


class RecommendationHistoryModel(Base):
    """Individual recommendation result ORM model."""

    __tablename__ = "recommendation_history"
    __table_args__ = (
        Index("ix_rec_history_phone", "phone_id"),
        Index("ix_rec_history_rec_rank", "recommendation_id", "rank"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recommendation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("recommendations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    phone_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("phones.id", ondelete="CASCADE"), nullable=False
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    recommendation: Mapped["RecommendationModel"] = relationship(back_populates="history")
    phone: Mapped["PhoneModel"] = relationship()


class FavoriteModel(Base):
    """User favorite phone ORM model."""

    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("user_id", "phone_id", name="uq_favorites_user_phone"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    phone_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("phones.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["UserModel"] = relationship(back_populates="favorites")
    phone: Mapped["PhoneModel"] = relationship()


class PhoneReviewModel(Base):
    """User review and rating for a phone."""

    __tablename__ = "phone_reviews"
    __table_args__ = (
        UniqueConstraint("user_id", "phone_id", name="uq_reviews_user_phone"),
        Index("ix_reviews_phone_rating", "phone_id", "rating"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    phone_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("phones.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["UserModel"] = relationship(back_populates="reviews")
    phone: Mapped["PhoneModel"] = relationship(back_populates="reviews")


class PhonePriceHistoryModel(Base):
    """Historical price tracking for phones."""

    __tablename__ = "phone_price_history"
    __table_args__ = (Index("ix_price_history_phone_date", "phone_id", "recorded_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phone_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("phones.id", ondelete="CASCADE"), nullable=False, index=True
    )
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    original_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    discount_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    changed_by: Mapped[str | None] = mapped_column(String(100), nullable=True)

    phone: Mapped["PhoneModel"] = relationship(back_populates="price_history")
