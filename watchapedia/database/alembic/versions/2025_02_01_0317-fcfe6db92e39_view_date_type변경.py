"""view_date type변경

Revision ID: fcfe6db92e39
Revises: c93e49e3c18e
Create Date: 2025-02-01 03:17:36.679043

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'fcfe6db92e39'
down_revision: Union[str, None] = 'c93e49e3c18e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('review', 'view_date',
               existing_type=mysql.JSON(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('review', 'view_date',
               existing_type=mysql.JSON(),
               nullable=False)
    # ### end Alembic commands ###
