"""empty message

Revision ID: 2a6af45fa4c5
Revises: e56742b7ec38
Create Date: 2020-02-08 10:08:05.387760

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2a6af45fa4c5'
down_revision = 'e56742b7ec38'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Observations', sa.Column('user_id', sa.String(length=120), nullable=False))
    op.drop_column('Observations', 'name')
    op.add_column('Plant', sa.Column('user_id', sa.String(length=120), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Plant', 'user_id')
    op.add_column('Observations', sa.Column('name', sa.VARCHAR(length=120), autoincrement=False, nullable=False))
    op.drop_column('Observations', 'user_id')
    # ### end Alembic commands ###