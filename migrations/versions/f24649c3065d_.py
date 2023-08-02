"""empty message

Revision ID: f24649c3065d
Revises: 93da99989fc0
Create Date: 2023-08-02 22:29:34.799905

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f24649c3065d'
down_revision = '93da99989fc0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vehicle', schema=None) as batch_op:
        batch_op.add_column(sa.Column('imagens', sa.String(length=1000), nullable=True))
        batch_op.drop_column('image_filenames')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vehicle', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_filenames', sa.BLOB(), nullable=True))
        batch_op.drop_column('imagens')

    # ### end Alembic commands ###
