"""Migration: expanded phone fields, reviews, price history.

Revision ID: 002_marketplace
Revises: 001_initial
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002_marketplace"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add marketplace fields and new tables."""
    op.add_column("phones", sa.Column("original_price", sa.Numeric(10, 2), nullable=True))
    op.add_column("phones", sa.Column("discount_percent", sa.Float(), nullable=True))
    op.add_column("phones", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("phones", sa.Column("charging_watts", sa.Integer(), nullable=True))
    op.add_column("phones", sa.Column("rating_avg", sa.Float(), server_default="0", nullable=False))
    op.add_column("phones", sa.Column("review_count", sa.Integer(), server_default="0", nullable=False))
    op.add_column("phones", sa.Column("weight_grams", sa.Float(), nullable=True))
    op.add_column("phones", sa.Column("dimensions", sa.String(50), nullable=True))
    op.add_column(
        "phones",
        sa.Column("colors", sa.JSON(), server_default="[]", nullable=False),
    )
    op.add_column("phones", sa.Column("release_date", sa.Date(), nullable=True))
    op.create_index("ix_phones_model_year", "phones", ["model_year"])
    op.create_index("ix_phones_rating", "phones", ["rating_avg"])
    op.create_index("ix_phones_trending", "phones", ["view_count", "recommendation_count"])

    op.add_column(
        "phone_features",
        sa.Column("has_fingerprint", sa.Boolean(), server_default="true", nullable=False),
    )
    op.add_column(
        "phone_features",
        sa.Column("display_type", sa.String(50), server_default="AMOLED", nullable=False),
    )
    op.add_column("phone_features", sa.Column("sim_type", sa.String(50), nullable=True))
    op.add_column("phone_features", sa.Column("bluetooth", sa.String(50), nullable=True))
    op.add_column("phone_features", sa.Column("wifi", sa.String(50), nullable=True))
    op.add_column("phone_features", sa.Column("usb_type", sa.String(50), nullable=True))
    op.add_column(
        "phone_features",
        sa.Column("stereo_speakers", sa.Boolean(), server_default="false", nullable=False),
    )

    op.create_table(
        "phone_reviews",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("phone_id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["phone_id"], ["phones.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "phone_id", name="uq_reviews_user_phone"),
    )
    op.create_index("ix_reviews_phone_rating", "phone_reviews", ["phone_id", "rating"])
    op.create_index("ix_phone_reviews_user_id", "phone_reviews", ["user_id"])
    op.create_index("ix_phone_reviews_phone_id", "phone_reviews", ["phone_id"])

    op.create_table(
        "phone_price_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("phone_id", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("original_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("discount_percent", sa.Float(), nullable=True),
        sa.Column("currency", sa.String(3), server_default="USD", nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("changed_by", sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(["phone_id"], ["phones.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_price_history_phone_date", "phone_price_history", ["phone_id", "recorded_at"])
    op.create_index("ix_phone_price_history_phone_id", "phone_price_history", ["phone_id"])


def downgrade() -> None:
    """Revert marketplace expansion."""
    op.drop_table("phone_price_history")
    op.drop_table("phone_reviews")
    for col in ("stereo_speakers", "usb_type", "wifi", "bluetooth", "sim_type", "display_type", "has_fingerprint"):
        op.drop_column("phone_features", col)
    op.drop_index("ix_phones_trending", "phones")
    op.drop_index("ix_phones_rating", "phones")
    op.drop_index("ix_phones_model_year", "phones")
    for col in ("release_date", "colors", "dimensions", "weight_grams", "review_count", "rating_avg",
                "charging_watts", "description", "discount_percent", "original_price"):
        op.drop_column("phones", col)
