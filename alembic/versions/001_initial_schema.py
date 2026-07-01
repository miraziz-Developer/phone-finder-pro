"""Initial schema migration.

Revision ID: 001_initial
Revises:
Create Date: 2026-07-01
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all application tables."""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("first_name", sa.String(length=255), nullable=True),
        sa.Column("last_name", sa.String(length=255), nullable=True),
        sa.Column("language_code", sa.String(length=10), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("telegram_id"),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"])

    op.create_table(
        "brands",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("logo_url", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_brands_slug", "brands", ["slug"])

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_categories_slug", "categories", ["slug"])

    op.create_table(
        "phones",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("brand_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("model_year", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("cpu", sa.String(length=255), nullable=False),
        sa.Column("gpu", sa.String(length=255), nullable=True),
        sa.Column("ram_gb", sa.Integer(), nullable=False),
        sa.Column("storage_gb", sa.Integer(), nullable=False),
        sa.Column("battery_mah", sa.Integer(), nullable=False),
        sa.Column("camera_main_mp", sa.Float(), nullable=False),
        sa.Column("camera_ultra_mp", sa.Float(), nullable=True),
        sa.Column("camera_tele_mp", sa.Float(), nullable=True),
        sa.Column("camera_front_mp", sa.Float(), nullable=False),
        sa.Column("performance_score", sa.Float(), nullable=False),
        sa.Column("camera_score", sa.Float(), nullable=False),
        sa.Column("battery_score", sa.Float(), nullable=False),
        sa.Column("display_score", sa.Float(), nullable=False),
        sa.Column("advantages", sa.JSON(), server_default="[]", nullable=False),
        sa.Column("disadvantages", sa.JSON(), server_default="[]", nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("view_count", sa.Integer(), nullable=False),
        sa.Column("recommendation_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["brand_id"], ["brands.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_phones_slug"),
    )
    op.create_index("ix_phones_brand_id", "phones", ["brand_id"])
    op.create_index("ix_phones_category_id", "phones", ["category_id"])
    op.create_index("ix_phones_price", "phones", ["price"])
    op.create_index("ix_phones_ram_storage", "phones", ["ram_gb", "storage_gb"])
    op.create_index("ix_phones_active_price", "phones", ["is_active", "price"])
    op.create_index("ix_phones_is_active", "phones", ["is_active"])

    op.create_table(
        "phone_features",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("phone_id", sa.Integer(), nullable=False),
        sa.Column("has_5g", sa.Boolean(), nullable=False),
        sa.Column("has_nfc", sa.Boolean(), nullable=False),
        sa.Column("has_wireless_charging", sa.Boolean(), nullable=False),
        sa.Column("has_esim", sa.Boolean(), nullable=False),
        sa.Column("has_amoled", sa.Boolean(), nullable=False),
        sa.Column("has_high_refresh", sa.Boolean(), nullable=False),
        sa.Column("refresh_rate_hz", sa.Integer(), nullable=False),
        sa.Column("display_size_inches", sa.Float(), nullable=False),
        sa.Column("display_resolution", sa.String(length=50), nullable=False),
        sa.Column("ip_rating", sa.String(length=20), nullable=True),
        sa.Column("os_version", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(["phone_id"], ["phones.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("phone_id"),
    )
    op.create_index("ix_phone_features_phone_id", "phone_features", ["phone_id"])

    op.create_table(
        "phone_images",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("phone_id", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["phone_id"], ["phones.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_phone_images_phone_id", "phone_images", ["phone_id"])
    op.create_index("ix_phone_images_phone_sort", "phone_images", ["phone_id", "sort_order"])

    op.create_table(
        "user_preferences",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("budget_min", sa.Float(), nullable=False),
        sa.Column("budget_max", sa.Float(), nullable=False),
        sa.Column("use_case", sa.String(length=50), nullable=False),
        sa.Column("preferred_brand", sa.String(length=50), nullable=True),
        sa.Column("min_ram_gb", sa.Integer(), nullable=False),
        sa.Column("min_storage_gb", sa.Integer(), nullable=False),
        sa.Column("requires_5g", sa.Boolean(), nullable=False),
        sa.Column("requires_nfc", sa.Boolean(), nullable=False),
        sa.Column("requires_wireless_charging", sa.Boolean(), nullable=False),
        sa.Column("requires_esim", sa.Boolean(), nullable=False),
        sa.Column("requires_amoled", sa.Boolean(), nullable=False),
        sa.Column("requires_high_refresh", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_preferences_user_id", "user_preferences", ["user_id"])
    op.create_index("ix_user_preferences_user_created", "user_preferences", ["user_id", "created_at"])

    op.create_table(
        "recommendations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("preference_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["preference_id"], ["user_preferences.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_recommendations_user_id", "recommendations", ["user_id"])
    op.create_index("ix_recommendations_preference_id", "recommendations", ["preference_id"])
    op.create_index("ix_recommendations_user_created", "recommendations", ["user_id", "created_at"])

    op.create_table(
        "recommendation_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("recommendation_id", sa.Integer(), nullable=False),
        sa.Column("phone_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["phone_id"], ["phones.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recommendation_id"], ["recommendations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_rec_history_recommendation_id", "recommendation_history", ["recommendation_id"])
    op.create_index("ix_rec_history_phone", "recommendation_history", ["phone_id"])
    op.create_index("ix_rec_history_rec_rank", "recommendation_history", ["recommendation_id", "rank"])

    op.create_table(
        "favorites",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("phone_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["phone_id"], ["phones.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "phone_id", name="uq_favorites_user_phone"),
    )
    op.create_index("ix_favorites_user_id", "favorites", ["user_id"])
    op.create_index("ix_favorites_phone_id", "favorites", ["phone_id"])


def downgrade() -> None:
    """Drop all application tables."""
    op.drop_table("favorites")
    op.drop_table("recommendation_history")
    op.drop_table("recommendations")
    op.drop_table("user_preferences")
    op.drop_table("phone_images")
    op.drop_table("phone_features")
    op.drop_table("phones")
    op.drop_table("categories")
    op.drop_table("brands")
    op.drop_table("users")
