-- Enable UUID extension (required for UUID primary keys)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- SourceTypes Table (Lookup Table for Source Types)
CREATE TABLE IF NOT EXISTS source_types (
    source_type_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT UNIQUE NOT NULL,  -- e.g., 'twitter', 'web_url', 'linkedin', 'github'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Profiles Table
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT,
    avatar_url TEXT,
    role TEXT DEFAULT 'free',
    subscription_status TEXT DEFAULT 'none',
    subscription_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    preferences JSONB DEFAULT '{"theme": "light", "defaultView": "blog", "emailNotifications": true}'::JSONB
);

-- ContentTypes Table
CREATE TABLE IF NOT EXISTS content_types (
    content_type_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Content Table
CREATE TABLE IF NOT EXISTS content (
    content_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    content_type_id UUID REFERENCES content_types(content_type_id) ON DELETE CASCADE,
    title TEXT,
    body TEXT,
    status TEXT CHECK (status IN ('Draft', 'Published', 'Archived','Scheduled','Archived')) DEFAULT 'Draft',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    published_at TIMESTAMPTZ,
    thread_id UUID
);

-- Sources Table
CREATE TABLE IF NOT EXISTS sources (
    source_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    batch_id UUID,
    source_type_id UUID REFERENCES source_types(source_type_id) ON DELETE CASCADE,  -- Reference to source_types
    source_identifier TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ContentSources Table
CREATE TABLE IF NOT EXISTS content_sources (
    content_source_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES content(content_id) ON DELETE CASCADE,
    source_id UUID REFERENCES sources(source_id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- URLReferences Table
CREATE TABLE IF NOT EXISTS url_references (
    url_reference_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES sources(source_id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    type TEXT,
    domain TEXT,
    content_type TEXT,
    file_category TEXT,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Media Table
CREATE TABLE IF NOT EXISTS media (
    media_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES sources(source_id) ON DELETE CASCADE,
    media_url TEXT NOT NULL,
    media_type TEXT CHECK (media_type IN ('image', 'video', 'audio', 'document')) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tags Table
CREATE TABLE IF NOT EXISTS tags (
    tag_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ContentTags Table
CREATE TABLE IF NOT EXISTS content_tags (
    content_tag_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES content(content_id) ON DELETE CASCADE,
    tag_id UUID REFERENCES tags(tag_id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Metadata Table
CREATE TABLE IF NOT EXISTS source_metadata (
    metadata_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES sources(source_id) ON DELETE CASCADE,
    key TEXT NOT NULL,
    value TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- CustomFields Table
CREATE TABLE IF NOT EXISTS custom_fields (
    custom_field_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_type_id UUID REFERENCES source_types(source_type_id) ON DELETE CASCADE,  -- Reference to source_types
    field_name TEXT NOT NULL,
    field_type TEXT CHECK (field_type IN ('string', 'number', 'boolean', 'date')) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- CustomFieldValues Table
CREATE TABLE IF NOT EXISTS custom_field_values (
    custom_field_value_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES sources(source_id) ON DELETE CASCADE,
    custom_field_id UUID REFERENCES custom_fields(custom_field_id) ON DELETE CASCADE,
    value TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ContentAnalytics Table
CREATE TABLE IF NOT EXISTS content_analytics (
    analytics_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES content(content_id) ON DELETE CASCADE,
    views INT DEFAULT 0,
    likes INT DEFAULT 0,
    shares INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- UserActivity Table
CREATE TABLE IF NOT EXISTS user_activity (
    activity_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    activity_type TEXT CHECK (activity_type IN ('login', 'blog_created', 'blog_published')) NOT NULL,
    activity_details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Plans Table
CREATE TABLE IF NOT EXISTS plans (
    plan_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    features JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Subscriptions Table
CREATE TABLE IF NOT EXISTS subscriptions (
    subscription_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES plans(plan_id) ON DELETE CASCADE,
    start_date TIMESTAMPTZ NOT NULL,
    end_date TIMESTAMPTZ,
    status TEXT CHECK (status IN ('active', 'canceled', 'expired')) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Payments Table
CREATE TABLE IF NOT EXISTS payments (
    payment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subscription_id UUID REFERENCES subscriptions(subscription_id) ON DELETE CASCADE,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method TEXT CHECK (payment_method IN ('credit_card', 'paypal', 'stripe')) NOT NULL,
    status TEXT CHECK (status IN ('success', 'failed', 'pending')) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- UserSelectedSources Table
CREATE TABLE IF NOT EXISTS user_selected_sources (
    selection_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    source_id UUID REFERENCES sources(source_id) ON DELETE CASCADE,
    selected_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default source types
INSERT INTO source_types (name) VALUES
('twitter'),
('web_url'),
('linkedin'),
('github');

-- Insert default content types
INSERT INTO content_types (name) VALUES
('blog'),
('short_post'),
('twitter_post'),
('linkedin_post');

CREATE OR REPLACE FUNCTION filter_content_by_domain(domain_text TEXT)
RETURNS TABLE (
    content_id UUID,
    title TEXT,
    body TEXT,
    status TEXT,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    published_at TIMESTAMPTZ,
    thread_id UUID,
    content_type_id UUID,
    content_type_name TEXT,
    tag_id UUID,
    tag_name TEXT,
    content_source_id UUID,
    source_id UUID,
    source_identifier TEXT,
    source_type_name TEXT,
    url_references JSONB,
    media JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.content_id,
        c.title,
        c.body,
        c.status,
        c.created_at,
        c.updated_at,
        c.published_at,
        c.thread_id,
        ct.content_type_id,
        ct.name AS content_type_name,
        t.tag_id,
        t.name AS tag_name,
        cs.content_source_id,
        s.source_id,
        s.source_identifier,
        st.name AS source_type_name,
        s.url_references,
        s.media
    FROM
        content c
        LEFT JOIN content_types ct ON c.content_type_id = ct.content_type_id
        LEFT JOIN content_tags ctg ON c.content_id = ctg.content_id
        LEFT JOIN tags t ON ctg.tag_id = t.tag_id
        LEFT JOIN content_sources cs ON c.content_id = cs.content_id
        LEFT JOIN sources s ON cs.source_id = s.source_id
        LEFT JOIN source_types st ON s.source_type_id = st.source_type_id
    WHERE
        s.url_references @> jsonb_build_object('domain', domain_text);
END;
$$ LANGUAGE plpgsql;