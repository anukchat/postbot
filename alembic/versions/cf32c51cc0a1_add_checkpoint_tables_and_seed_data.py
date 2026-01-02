"""seed_reference_data

Revision ID: cf32c51cc0a1
Revises: e2746ef4e845
Create Date: 2026-01-01 10:35:43.366448

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf32c51cc0a1'
down_revision: Union[str, None] = 'e2746ef4e845'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Seed generation_limits (idempotent)
    op.execute("""
        INSERT INTO generation_limits (tier, max_generations) VALUES
        ('free', 5),
        ('basic', 20),
        ('premium', 1000)
        ON CONFLICT (tier) DO UPDATE
        SET max_generations = EXCLUDED.max_generations
    """)

    # Seed source_types
    op.execute("""
        INSERT INTO source_types (source_type_id, name, created_at) VALUES
        (gen_random_uuid(), 'twitter', NOW()),
        (gen_random_uuid(), 'web_url', NOW()),
        (gen_random_uuid(), 'topic', NOW()),
        (gen_random_uuid(), 'reddit', NOW())
        ON CONFLICT (name) DO NOTHING
    """)

    # Seed content_types
    op.execute("""
        INSERT INTO content_types (content_type_id, name, created_at) VALUES
        (gen_random_uuid(), 'blog', NOW()),
        (gen_random_uuid(), 'social_post', NOW()),
        (gen_random_uuid(), 'article', NOW()),
        (gen_random_uuid(), 'newsletter', NOW())
        ON CONFLICT (name) DO NOTHING
    """)

    # Seed parameters
    op.execute("""
        INSERT INTO parameters (parameter_id, name, display_name, description, is_required, created_at) VALUES
        (gen_random_uuid(), 'persona', 'Persona', 'The persona/role for content generation', true, NOW()),
        (gen_random_uuid(), 'content_type', 'Content Type', 'The type of content to generate', true, NOW()),
        (gen_random_uuid(), 'age_group', 'Age Group', 'Target age group for the content', true, NOW()),
        (gen_random_uuid(), 'tone', 'Tone', 'Writing tone', false, NOW()),
        (gen_random_uuid(), 'length', 'Length', 'Expected content length', false, NOW())
        ON CONFLICT (name) DO NOTHING
    """)


def downgrade() -> None:
    # Remove seed data
    op.execute("DELETE FROM parameters WHERE name IN ('persona', 'content_type', 'age_group', 'tone', 'length')")
    op.execute("DELETE FROM content_types WHERE name IN ('blog', 'social_post', 'article', 'newsletter')")
    op.execute("DELETE FROM source_types WHERE name IN ('twitter', 'web_url', 'topic', 'reddit')")
    op.execute("DELETE FROM generation_limits WHERE tier IN ('free', 'basic', 'premium')")
