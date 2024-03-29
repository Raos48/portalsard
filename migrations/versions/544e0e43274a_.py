"""empty message

Revision ID: 544e0e43274a
Revises: b0edeef9833a
Create Date: 2024-02-12 19:31:34.170007

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '544e0e43274a'
down_revision = 'b0edeef9833a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('status_api', schema=None) as batch_op:
        batch_op.alter_column('data',
               existing_type=mysql.VARCHAR(length=45),
               type_=sa.DateTime(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('status_api', schema=None) as batch_op:
        batch_op.alter_column('data',
               existing_type=sa.DateTime(),
               type_=mysql.VARCHAR(length=45),
               existing_nullable=True)

    # ### end Alembic commands ###
