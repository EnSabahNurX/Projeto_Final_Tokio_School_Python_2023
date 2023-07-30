"""database update

Revision ID: 9a4c303852c3
Revises: bc47e0924781
Create Date: 2023-07-31 00:05:13.861911

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9a4c303852c3'
down_revision = 'bc47e0924781'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vehicle', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.Boolean(), nullable=True))
        batch_op.drop_column('is_available')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vehicle', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_available', sa.BOOLEAN(), nullable=True))
        batch_op.drop_column('status')

    # ### end Alembic commands ###
