"""empty message

Revision ID: 71ce786b667f
Revises: 5366394e4835
Create Date: 2020-01-27 11:22:21.625774

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '71ce786b667f'
down_revision = '5366394e4835'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Observations', sa.Column(
        'contributor_email', sa.String(length=120), nullable=True))
    op.add_column('Plant', sa.Column('contributor_email',
                                     sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Plant', 'contributor_email')
    op.drop_column('Observations', 'contributor_email')
    # ### end Alembic commands ###
