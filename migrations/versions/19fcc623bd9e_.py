"""empty message

Revision ID: 19fcc623bd9e
Revises: 71ce786b667f
Create Date: 2020-01-27 11:33:44.751558

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '19fcc623bd9e'
down_revision = '71ce786b667f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Observations', 'contributor_email',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('Plant', 'contributor_email',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Plant', 'contributor_email',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('Observations', 'contributor_email',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    # ### end Alembic commands ###
