"""Merge two heads

Revision ID: e7ce82e7162b
Revises: a4dc72750b80, a91b476a53de
Create Date: 2025-02-11 15:42:39.273051

"""
from alembic import op
import models as models
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e7ce82e7162b'
down_revision = ('a4dc72750b80', 'a91b476a53de')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
