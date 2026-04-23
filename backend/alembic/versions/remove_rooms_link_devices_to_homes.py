"""Remove rooms, link devices directly to homes

Revision ID: c0d1a2b3c4d5
Revises: b30149459cec
Create Date: 2026-04-20 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c0d1a2b3c4d5'
down_revision: Union[str, Sequence[str], None] = 'b30149459cec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - remove rooms table and link devices to homes."""
    # Add home_id and location columns to devices
    op.add_column('devices', sa.Column('home_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('devices', sa.Column('location', sa.String(), nullable=True))
    op.add_column('devices', sa.Column('updated_at', sa.DateTime(), nullable=True))

    # Copy data from rooms to devices
    op.execute("""
        UPDATE devices d 
        SET home_id = r.home_id 
        FROM rooms r 
        WHERE d.room_id = r.id
    """)

    # Set updated_at to created_at for existing records
    op.execute("""
        UPDATE devices 
        SET updated_at = created_at 
        WHERE updated_at IS NULL
    """)

    # Make home_id and updated_at NOT NULL
    op.alter_column('devices', 'home_id', nullable=False)
    op.alter_column('devices', 'updated_at', nullable=False)

    # Add foreign key constraint for home_id
    op.create_foreign_key(
        'devices_home_id_fkey',
        'devices', 'homes',
        ['home_id'], ['id'],
        ondelete='CASCADE'
    )

    # Add indices
    op.create_index('idx_devices_home_id', 'devices', ['home_id'])
    op.create_index('idx_devices_online_status', 'devices', ['online_status'])
    op.create_index('idx_devices_location', 'devices', ['location'])

    # Drop the old room_id foreign key
    op.drop_constraint('devices_room_id_fkey', 'devices', type_='foreignkey')
    
    # Drop the old room_id column
    op.drop_column('devices', 'room_id')

    # Drop the rooms table
    op.drop_table('rooms')


def downgrade() -> None:
    """Downgrade schema - restore rooms table and revert devices."""
    # Recreate rooms table
    op.create_table('rooms',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('home_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('icon', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['home_id'], ['homes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Add room_id back to devices
    op.add_column('devices', sa.Column('room_id', postgresql.UUID(as_uuid=True), nullable=True))

    # Recreate rooms from location data (just assign to first room of home)
    op.execute("""
        INSERT INTO rooms (id, home_id, name, created_at)
        SELECT 
            gen_random_uuid(),
            d.home_id,
            COALESCE(d.location, 'Default Room'),
            NOW()
        FROM (
            SELECT DISTINCT home_id, location
            FROM devices
        ) d
    """)

    # Map devices back to rooms
    op.execute("""
        UPDATE devices d
        SET room_id = (
            SELECT id FROM rooms r
            WHERE r.home_id = d.home_id
            LIMIT 1
        )
    """)

    # Make room_id NOT NULL and add foreign key
    op.alter_column('devices', 'room_id', nullable=False)
    op.create_foreign_key(
        'devices_room_id_fkey',
        'devices', 'rooms',
        ['room_id'], ['id'],
        ondelete='CASCADE'
    )

    # Drop new columns and indices
    op.drop_index('idx_devices_location')
    op.drop_index('idx_devices_online_status')
    op.drop_index('idx_devices_home_id')
    op.drop_constraint('devices_home_id_fkey', 'devices', type_='foreignkey')
    op.drop_column('devices', 'updated_at')
    op.drop_column('devices', 'location')
    op.drop_column('devices', 'home_id')
