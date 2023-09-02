"""empty message

Revision ID: a95d7fbd62be
Revises: 129c7bbb84bb
Create Date: 2023-09-02 15:36:28.507222

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a95d7fbd62be'
down_revision = '129c7bbb84bb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('categoria', schema=None) as batch_op:
        batch_op.alter_column('nome',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.String(length=255),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('categoria', schema=None) as batch_op:
        batch_op.alter_column('nome',
               existing_type=sa.String(length=255),
               type_=sa.VARCHAR(length=50),
               existing_nullable=False)

    # ### end Alembic commands ###
