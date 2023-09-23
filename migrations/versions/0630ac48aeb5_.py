"""empty message

Revision ID: 0630ac48aeb5
Revises: 
Create Date: 2023-09-23 12:12:24.433491

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0630ac48aeb5'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('errors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('step', sa.Enum('TRANSTALTION', 'TELEGRAM', name='stepnamechoice'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('step')
    )
    op.create_table('posts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('link', sa.Text(), nullable=False),
    sa.Column('title', sa.Text(), nullable=False),
    sa.Column('short_description', sa.Text(), nullable=False),
    sa.Column('error_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['error_id'], ['errors.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('posts')
    op.drop_table('errors')
    # ### end Alembic commands ###