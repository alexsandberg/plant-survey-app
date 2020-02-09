"""empty message

Revision ID: 7225f407d169
Revises: 1f52bdfdc1f9
Create Date: 2020-02-09 10:33:01.785192

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7225f407d169'
down_revision = '1f52bdfdc1f9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('username', sa.String(length=120), nullable=False),
    sa.Column('user_id', sa.String(length=120), nullable=False),
    sa.Column('date_added', sa.DateTime(), nullable=False),
    sa.Column('role', sa.String(length=120), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Plants',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('latin_name', sa.String(length=120), nullable=False),
    sa.Column('description', sa.String(length=2500), nullable=False),
    sa.Column('image_link', sa.String(length=500), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['Users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Observations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('plant_id', sa.Integer(), nullable=False),
    sa.Column('notes', sa.String(length=2500), nullable=True),
    sa.ForeignKeyConstraint(['plant_id'], ['Plants.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['Users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Observations')
    op.drop_table('Plants')
    op.drop_table('Users')
    # ### end Alembic commands ###
