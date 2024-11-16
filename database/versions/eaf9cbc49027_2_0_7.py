"""2.0.7

Revision ID: eaf9cbc49027
Revises: a295e41830a6
Create Date: 2024-11-16 00:26:09.505188

"""
import contextlib

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'eaf9cbc49027'
down_revision = 'a295e41830a6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # 站点管理、订阅增加下载器选项
    with contextlib.suppress(Exception):
        op.add_column('site', sa.Column('downloader', sa.String(), nullable=True))
        op.add_column('subscribe', sa.Column('downloader', sa.String(), nullable=True))


# ### end Alembic commands ###

def downgrade() -> None:
    pass
