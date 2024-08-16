"""merge heads

Revision ID: 07a4565e67b6
Revises: 8782057ff0dc, 2b2278ef199d
Create Date: 2024-08-16 08:25:05.119934

"""
from alembic import op
import models as models
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '07a4565e67b6'
down_revision = ('8782057ff0dc', '2b2278ef199d')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
