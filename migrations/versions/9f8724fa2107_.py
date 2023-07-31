"""empty message

Revision ID: 9f8724fa2107
Revises: 68e16828c9de
Create Date: 2023-07-31 14:49:13.130153

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f8724fa2107'
down_revision = '68e16828c9de'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vehicle', schema=None) as batch_op:
        batch_op.add_column(sa.Column('last_legalization_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('next_legalization_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('legalization_history', sa.String(length=1000), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vehicle', schema=None) as batch_op:
        batch_op.drop_column('legalization_history')
        batch_op.drop_column('next_legalization_date')
        batch_op.drop_column('last_legalization_date')

    # ### end Alembic commands ###
