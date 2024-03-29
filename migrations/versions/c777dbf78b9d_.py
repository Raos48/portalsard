"""empty message

Revision ID: c777dbf78b9d
Revises: 544e0e43274a
Create Date: 2024-02-21 15:39:52.275036

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'c777dbf78b9d'
down_revision = '544e0e43274a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('solicitacoes', schema=None) as batch_op:
        batch_op.alter_column('protocolo',
               existing_type=mysql.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('solicitacoes', schema=None) as batch_op:
        batch_op.alter_column('protocolo',
               existing_type=mysql.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###
