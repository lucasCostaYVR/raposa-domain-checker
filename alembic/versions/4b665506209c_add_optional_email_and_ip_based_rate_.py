"""Add optional email and IP-based rate limiting for anonymous users

Revision ID: 4b665506209c
Revises: 6b897e8e0f54
Create Date: 2025-07-18 20:18:38.378073

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b665506209c'
down_revision: Union[str, Sequence[str], None] = '6b897e8e0f54'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('anonymous_usage',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('client_ip', sa.String(), nullable=False),
    sa.Column('domain', sa.String(), nullable=False),
    sa.Column('check_count', sa.Integer(), nullable=True),
    sa.Column('last_check', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('month_year', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_anonymous_usage_client_ip'), 'anonymous_usage', ['client_ip'], unique=False)
    op.create_index(op.f('ix_anonymous_usage_domain'), 'anonymous_usage', ['domain'], unique=False)
    op.create_index(op.f('ix_anonymous_usage_id'), 'anonymous_usage', ['id'], unique=False)
    op.create_index(op.f('ix_anonymous_usage_month_year'), 'anonymous_usage', ['month_year'], unique=False)
    op.add_column('domain_checks', sa.Column('client_ip', sa.String(), nullable=True))
    op.alter_column('domain_checks', 'email',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.create_index(op.f('ix_domain_checks_client_ip'), 'domain_checks', ['client_ip'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_domain_checks_client_ip'), table_name='domain_checks')
    op.alter_column('domain_checks', 'email',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_column('domain_checks', 'client_ip')
    op.drop_index(op.f('ix_anonymous_usage_month_year'), table_name='anonymous_usage')
    op.drop_index(op.f('ix_anonymous_usage_id'), table_name='anonymous_usage')
    op.drop_index(op.f('ix_anonymous_usage_domain'), table_name='anonymous_usage')
    op.drop_index(op.f('ix_anonymous_usage_client_ip'), table_name='anonymous_usage')
    op.drop_table('anonymous_usage')
    # ### end Alembic commands ###
