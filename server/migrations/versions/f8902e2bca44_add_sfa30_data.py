"""Add SFA30 Data

Revision ID: f8902e2bca44
Revises: 28f42edd9fb0
Create Date: 2025-02-18 17:56:16.905880

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f8902e2bca44"
down_revision: Union[str, None] = "28f42edd9fb0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "sfa30_data",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("temperature", sa.VARCHAR(length=20), nullable=False),
        sa.Column("humidity", sa.VARCHAR(length=20), nullable=False),
        sa.Column("hco", sa.VARCHAR(length=20), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_sfa30_data"),
    )
    op.add_column("station_data", sa.Column("sfa30_data_id", sa.INTEGER(), nullable=True))
    op.create_foreign_key(None, "station_data", "sfa30_data", ["sfa30_data_id"], ["id"])

    with op.get_context().autocommit_block():
        op.create_index(op.f("ix_sfa30_data_id"), "sfa30_data", ["id"], unique=False, postgresql_concurrently=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "station_data", type_="foreignkey")
    op.drop_column("station_data", "sfa30_data_id")
    op.drop_index(op.f("ix_sfa30_data_id"), table_name="sfa30_data")
    op.drop_table("sfa30_data")
    # ### end Alembic commands ###
