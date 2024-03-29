"""init

Revision ID: 65856ee0df0e
Revises: 
Create Date: 2024-01-21 20:26:42.730322

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '65856ee0df0e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sensor_data',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('co2', sa.VARCHAR(length=20), nullable=False),
    sa.Column('temperature', sa.VARCHAR(length=20), nullable=False),
    sa.Column('humidity', sa.VARCHAR(length=20), nullable=False),
    sa.Column('eco2', sa.Integer(), nullable=False),
    sa.Column('tvoc', sa.Integer(), nullable=False),
    sa.Column('aqi', sa.Integer(), nullable=False),
    sa.Column('sensor_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.VARCHAR(length=20), nullable=False),
    sa.Column('location_id', sa.VARCHAR(length=36), nullable=False),
    sa.PrimaryKeyConstraint('id', name='pk_sensor_data')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sensor_data')
    # ### end Alembic commands ###
