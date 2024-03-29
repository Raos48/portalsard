"""empty message

Revision ID: b0edeef9833a
Revises: 705908f3e0c5
Create Date: 2024-01-18 18:42:30.523790

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b0edeef9833a'
down_revision = '705908f3e0c5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('solicitacoes', schema=None) as batch_op:
        batch_op.alter_column('protocolo',
               existing_type=mysql.VARCHAR(length=50),
               type_=sa.Integer(),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('solicitacoes', schema=None) as batch_op:
        batch_op.alter_column('protocolo',
               existing_type=sa.Integer(),
               type_=mysql.VARCHAR(length=50),
               existing_nullable=False)

    # ### end Alembic commands ###
