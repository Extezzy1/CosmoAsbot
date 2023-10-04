"""add atlas

Revision ID: 2a035f093ef4
Revises: 6455bb3c305c
Create Date: 2023-10-04 19:57:16.647699

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a035f093ef4'
down_revision: Union[str, None] = '6455bb3c305c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('atlas',
    sa.Column('atlas_entry_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('atlas_entry_text', sa.VARCHAR(length=255), nullable=False),
    sa.PrimaryKeyConstraint('atlas_entry_id'),
    sa.UniqueConstraint('atlas_entry_id')
    )
    op.create_table('atlas_photos',
    sa.Column('altas_entry_id', sa.Integer(), nullable=True),
    sa.Column('atlas_photo_id', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['altas_entry_id'], ['atlas.atlas_entry_id'], ),
    sa.PrimaryKeyConstraint('atlas_photo_id'),
    sa.UniqueConstraint('atlas_photo_id')
    )
    op.create_unique_constraint(None, 'sub_procedures', ['sub_procedure_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'sub_procedures', type_='unique')
    op.drop_table('atlas_photos')
    op.drop_table('atlas')
    # ### end Alembic commands ###