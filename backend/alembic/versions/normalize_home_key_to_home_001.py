"""Normalize home key/name to home-001

Revision ID: c0d1a2b3c4d7
Revises: c0d1a2b3c4d6
Create Date: 2026-04-21 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c0d1a2b3c4d7"
down_revision: Union[str, Sequence[str], None] = "c0d1a2b3c4d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Data migration:
    - Normalize any home key/name variants that represent "home 001" into "home-001".

    Rationale: MQTT topics send home_key like "home-001" but existing DB may contain
    inconsistent variants like "home 001", "home01", "home 1", etc.
    """
    # Normalize homes.name
    op.execute(
        """
        UPDATE homes
        SET name = 'home-001'
        WHERE regexp_replace(lower(name), '[^a-z0-9]+', '', 'g') IN ('home1','home01','home001');
        """
    )

    # Normalize device_identity_map.home_key
    op.execute(
        """
        UPDATE device_identity_map
        SET home_key = 'home-001'
        WHERE regexp_replace(lower(home_key), '[^a-z0-9]+', '', 'g') IN ('home1','home01','home001');
        """
    )

    # Normalize devices.metadata.mqtt_home_key if present
    # (column is named "metadata" in DB; JSONB operators are used)
    op.execute(
        """
        UPDATE devices
        SET metadata =
            CASE
                WHEN metadata ? 'mqtt_home_key'
                 AND regexp_replace(lower(metadata->>'mqtt_home_key'), '[^a-z0-9]+', '', 'g') IN ('home1','home01','home001')
                THEN jsonb_set(metadata, '{mqtt_home_key}', '"home-001"'::jsonb, true)
                ELSE metadata
            END
        WHERE metadata ? 'mqtt_home_key';
        """
    )


def downgrade() -> None:
    """
    Irreversible normalization (we don't know original variants).
    """
    pass

