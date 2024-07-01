"""1_0_12

Revision ID: d71e624f0208
Revises: 06abf3e7090b
Create Date: 2023-12-12 13:26:34.039497

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd71e624f0208'
down_revision = '06abf3e7090b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    try:
        with op.batch_alter_table("subscribe") as batch_op:
            batch_op.add_column(sa.Column('save_path', sa.String, nullable=True))
    except Exception as e:
        pass
    # ### end Alembic commands ###


def downgrade() -> None:
    pass
