"""empty message

Revision ID: deb9c8c6cc16
Revises: 
Create Date: 2023-08-27 00:05:53.383290

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'deb9c8c6cc16'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cliente', schema=None) as batch_op:
        batch_op.add_column(sa.Column('price_per_day', sa.Float(), nullable=False))
        batch_op.alter_column('nif',
               existing_type=sa.VARCHAR(length=20),
               type_=sa.Integer(),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cliente', schema=None) as batch_op:
        batch_op.alter_column('nif',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(length=20),
               existing_nullable=False)
        batch_op.drop_column('price_per_day')

    # ### end Alembic commands ###
