"""Add indexes to ids in most tables

Revision ID: 28f42edd9fb0
Revises: 8d2149a11367
Create Date: 2025-01-29 13:06:06.378899

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "28f42edd9fb0"
down_revision: Union[str, None] = "8d2149a11367"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.get_context().autocommit_block():
        op.create_index(op.f("ix_bme688_data_id"), "bme688_data", ["id"], unique=False, postgresql_concurrently=True)
        op.create_index(op.f("ix_ens160_data_id"), "ens160_data", ["id"], unique=False, postgresql_concurrently=True)
        op.create_index(op.f("ix_scd41_data_id"), "scd41_data", ["id"], unique=False, postgresql_concurrently=True)
        op.create_index(op.f("ix_station_data_id"), "station_data", ["id"], unique=False, postgresql_concurrently=True)
        op.create_index(op.f("ix_svm41_data_id"), "svm41_data", ["id"], unique=False, postgresql_concurrently=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_svm41_data_id"), table_name="svm41_data")
    op.drop_index(op.f("ix_station_data_id"), table_name="station_data")
    op.drop_index(op.f("ix_scd41_data_id"), table_name="scd41_data")
    op.drop_index(op.f("ix_ens160_data_id"), table_name="ens160_data")
    op.drop_index(op.f("ix_bme688_data_id"), table_name="bme688_data")
    # ### end Alembic commands ###
