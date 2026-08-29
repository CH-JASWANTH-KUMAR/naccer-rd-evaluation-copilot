"""add_document_type_classification_fields

Revision ID: 9b7a4210e302
Revises: 7c100a6b46b8
Create Date: 2026-08-29 10:05:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = '9b7a4210e302'
down_revision: str | None = '7c100a6b46b8'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('documents', sa.Column('document_type', sa.String(length=50), nullable=False, server_default='R&D_PROPOSAL'))
    op.add_column('documents', sa.Column('document_type_confidence', sa.String(length=20), nullable=True))
    op.add_column('documents', sa.Column('document_type_reasons', sa.JSON(), nullable=True))

    op.add_column('proposals', sa.Column('document_type', sa.String(length=50), nullable=True, server_default='R&D_PROPOSAL'))
    op.add_column('proposals', sa.Column('document_type_confidence', sa.String(length=20), nullable=True))
    op.add_column('proposals', sa.Column('document_type_reasons', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('proposals', 'document_type_reasons')
    op.drop_column('proposals', 'document_type_confidence')
    op.drop_column('proposals', 'document_type')

    op.drop_column('documents', 'document_type_reasons')
    op.drop_column('documents', 'document_type_confidence')
    op.drop_column('documents', 'document_type')
