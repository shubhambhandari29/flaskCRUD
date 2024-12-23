"""empty message

Revision ID: 97616a7a326c
Revises: 
Create Date: 2024-12-23 19:58:48.740847

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '97616a7a326c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password', sa.String(length=200), nullable=False),
    sa.Column('date_joined', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('gift',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('description', sa.String(length=500), nullable=True),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('image_url', sa.String(length=300), nullable=True),
    sa.Column('seller_id', sa.Integer(), nullable=False),
    sa.Column('date_listed', sa.DateTime(), nullable=True),
    sa.Column('sold', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['seller_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('gift')
    op.drop_table('user')
    # ### end Alembic commands ###