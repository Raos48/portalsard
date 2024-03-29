"""empty message

Revision ID: d6d585237ffb
Revises: ed3578034221
Create Date: 2024-01-18 12:32:03.344427

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd6d585237ffb'
down_revision = 'ed3578034221'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('solicitacoes', schema=None) as batch_op:
        batch_op.drop_index('matricula')
        batch_op.drop_index('tipo')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('solicitacoes', schema=None) as batch_op:
        batch_op.create_index('tipo', ['tipo'], unique=False)
        batch_op.create_index('matricula', ['matricula'], unique=False)

    # ### end Alembic commands ###
