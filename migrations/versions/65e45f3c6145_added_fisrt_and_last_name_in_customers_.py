"""added fisrt and last name in customers model and changed nullable value in all the fields

Revision ID: 65e45f3c6145
Revises: 1cdc3936cc5c
Create Date: 2025-01-20 15:55:34.137389

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '65e45f3c6145'
down_revision = '1cdc3936cc5c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('customers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('first_name', sa.String(length=100), nullable=False))
        batch_op.add_column(sa.Column('last_name', sa.String(length=100), nullable=False))
        batch_op.alter_column('email',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
        batch_op.alter_column('phone',
               existing_type=sa.VARCHAR(length=15),
               nullable=False)
        batch_op.alter_column('address',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
        batch_op.drop_column('name')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('customers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.VARCHAR(length=100), nullable=False))
        batch_op.alter_column('address',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
        batch_op.alter_column('phone',
               existing_type=sa.VARCHAR(length=15),
               nullable=True)
        batch_op.alter_column('email',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
        batch_op.drop_column('last_name')
        batch_op.drop_column('first_name')

    # ### end Alembic commands ###
