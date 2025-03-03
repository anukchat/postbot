from typing import List, Optional
from datetime import datetime
from sqlalchemy import CheckConstraint, Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Table, Enum as SQLEnum, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

# Association tables for many-to-many relationships
content_tags = Table(
    'content_tags',
    Base.metadata,
    Column('content_tag_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column('content_id', UUID(as_uuid=True), ForeignKey('content.content_id')), 
    Column('tag_id', UUID(as_uuid=True), ForeignKey('tags.tag_id')),
    Column('created_at', DateTime(timezone=True), default=func.now()),
    Column('is_deleted', Boolean, default=False),
    Column('deleted_at', DateTime(timezone=True))
)

content_sources = Table(
    'content_sources',
    Base.metadata,
    Column('content_source_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column('content_id', UUID(as_uuid=True), ForeignKey('content.content_id')),
    Column('source_id', UUID(as_uuid=True), ForeignKey('sources.source_id')),
    Column('created_at', DateTime(timezone=True), default=func.now()),
    Column('is_deleted', Boolean, default=False),
    Column('deleted_at', DateTime(timezone=True))
)

template_parameters = Table(
    'template_parameters',
    Base.metadata,
    Column('template_param_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column('template_id', UUID(as_uuid=True), ForeignKey('templates.template_id')),
    Column('parameter_id', UUID(as_uuid=True), ForeignKey('parameters.parameter_id')),
    Column('value_id', UUID(as_uuid=True), ForeignKey('parameter_values.value_id')),
    Column('created_at', DateTime(timezone=True), default=func.now())
)

# Additional association tables from schema
user_selected_sources = Table(
    'user_selected_sources',
    Base.metadata,
    Column('selection_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column('profile_id', UUID(as_uuid=True), ForeignKey('profiles.id')),
    Column('source_id', UUID(as_uuid=True), ForeignKey('sources.source_id')),
    Column('selected_at', DateTime(timezone=True), default=func.now())
)

class Profile(Base):
    __tablename__ = 'profiles'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    full_name = Column(Text)
    avatar_url = Column(Text)
    role = Column(Text, default='free')
    subscription_status = Column(Text,
        CheckConstraint("subscription_status IN ('active', 'trialing', 'cancelled', 'none')"), default='none')
    subscription_end = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=func.now())
    preferences = Column(JSONB, default={'theme': 'light', 'defaultView': 'blog', 'emailNotifications': True})
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True))
    generations_used = Column(Integer, default=0)
    bio = Column(Text)
    website = Column(Text)
    company = Column(Text)
    updated_at = Column(DateTime(timezone=True), default=func.now())
    email = Column(Text)

    activities = relationship("UserActivity", back_populates="profile", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="profile")
    templates = relationship("Template", back_populates="profile")
    content = relationship("Content", back_populates="profile")

class Content(Base):
    __tablename__ = 'content'
    
    content_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'), nullable=False)
    content_type_id = Column(UUID(as_uuid=True), ForeignKey('content_types.content_type_id'))
    title = Column(Text)
    body = Column(Text)
    status = Column(Text, default='Draft')
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now())
    published_at = Column(DateTime(timezone=True))
    thread_id = Column(UUID(as_uuid=True))
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True))
    template_id = Column(UUID(as_uuid=True), ForeignKey('templates.template_id'))
    
    # Relationships
    profile = relationship("Profile")
    content_type = relationship("ContentType")
    template = relationship("Template")
    tags = relationship("Tag", secondary=content_tags)
    sources = relationship("Source", secondary=content_sources)

class ContentType(Base):
    __tablename__ = 'content_types'
    
    content_type_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), default=func.now())

class ContentAnalytics(Base):
    __tablename__ = 'content_analytics'
    
    analytics_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey('content.content_id'))
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now())

class Tag(Base):
    __tablename__ = 'tags'
    
    tag_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True))

class Source(Base):
    __tablename__ = 'sources'
    
    source_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_identifier = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now())
    batch_id = Column(UUID(as_uuid=True))
    source_type_id = Column(UUID(as_uuid=True), ForeignKey('source_types.source_type_id'), nullable=False)
    profile_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'), nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True))

    # Relationships
    source_type = relationship("SourceType")
    profile = relationship("Profile")
    url_references = relationship("URLReference", back_populates="source")
    media = relationship("Media", back_populates="source")


class SourceMetadata(Base):
    __tablename__ = 'source_metadata'
    
    metadata_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey('sources.source_id'))
    key = Column(Text, nullable=False)
    value = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Relationship

class SourceType(Base):
    __tablename__ = 'source_types'
    
    source_type_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), default=func.now())

class URLReference(Base):
    __tablename__ = 'url_references'
    
    url_reference_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey('sources.source_id'))
    url = Column(Text, nullable=False)
    description = Column(Text)
    type = Column(Text)
    domain = Column(Text)
    content_type = Column(Text)
    file_category = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.now())
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True))
    
    # Relationship
    source = relationship("Source", back_populates="url_references")

class Media(Base):
    __tablename__ = 'media'
    
    media_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey('sources.source_id'))
    media_url = Column(Text, nullable=False)
    media_type = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True))
    
    # Relationship
    source = relationship("Source", back_populates="media")

class Template(Base):
    __tablename__ = 'templates'
    
    template_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    description = Column(Text)
    template_type = Column(Text, default='default')
    profile_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    template_image_url = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now())
    is_deleted = Column(Boolean, default=False)

    # Relationships
    profile = relationship("Profile")
    parameters = relationship("Parameter", secondary=template_parameters, back_populates="templates")

class Parameter(Base):
    __tablename__ = 'parameters'
    
    parameter_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False, unique=True)
    display_name = Column(Text, nullable=False)
    description = Column(Text)
    is_required = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Relationships
    values = relationship("ParameterValue", back_populates="parameter", cascade="all, delete-orphan")
    templates = relationship("Template", secondary=template_parameters, back_populates="parameters")


class ParameterValue(Base):
    __tablename__ = 'parameter_values'
    
    value_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parameter_id = Column(UUID(as_uuid=True), ForeignKey('parameters.parameter_id'))
    value = Column(Text, nullable=False)
    display_order = Column(Integer)
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Relationships
    parameter = relationship("Parameter", back_populates="values")

class RateLimit(Base):
    __tablename__ = 'rate_limits'
    
    rate_limit_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    action_type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())

class Quota(Base):
    __tablename__ = 'quotas'
    
    quota_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    quota_type = Column(String, nullable=False)
    limit = Column(Integer, nullable=False)
    period = Column(String)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

class QuotaUsage(Base):
    __tablename__ = 'quota_usage'
    
    usage_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    quota_type = Column(String, nullable=False)
    amount = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), default=func.now())

class Checkpoint(Base):
    __tablename__ = 'checkpoints'
    
    thread_id = Column(Text, primary_key=True)
    checkpoint_ns = Column(Text, primary_key=True, default='')
    checkpoint_id = Column(Text, primary_key=True)
    parent_checkpoint_id = Column(Text)
    type = Column(Text)
    checkpoint = Column(JSONB, nullable=False)
    checkpoint_metadata = Column('metadata',JSONB, nullable=False, default={})

class CheckpointWrite(Base):
    __tablename__ = 'checkpoint_writes'
    
    thread_id = Column(Text, primary_key=True)
    checkpoint_ns = Column(Text, primary_key=True, default='')
    checkpoint_id = Column(Text, primary_key=True)
    task_id = Column(Text, primary_key=True)
    idx = Column(Integer, primary_key=True)
    channel = Column(Text, nullable=False)
    type = Column(Text)
    blob = Column(Text, nullable=False)
    task_path = Column(Text, nullable=False, default='')

class CheckpointBlob(Base):
    __tablename__ = 'checkpoint_blobs'
    
    thread_id = Column(Text, primary_key=True)
    checkpoint_ns = Column(Text, primary_key=True, default='')
    channel = Column(Text, primary_key=True)
    version = Column(Text, primary_key=True)
    type = Column(Text, nullable=False)
    blob = Column(Text)

class UserActivity(Base):
    __tablename__ = 'user_activity'
    
    activity_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    activity_type = Column(Text, nullable=False)
    activity_details = Column(JSONB)
    created_at = Column(DateTime(timezone=True), default=func.now())

    profile = relationship("Profile", back_populates="activities")    

class Plan(Base):
    __tablename__ = 'plans'
    
    plan_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    features = Column(JSONB)
    created_at = Column(DateTime(timezone=True), default=func.now())

class Subscription(Base):
    __tablename__ = 'subscriptions'
    
    subscription_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    plan_id = Column(UUID(as_uuid=True), ForeignKey('plans.plan_id'))
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True))
    status = Column(Text, default='active')
    created_at = Column(DateTime(timezone=True), default=func.now())

class Payment(Base):
    __tablename__ = 'payments'
    
    payment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey('subscriptions.subscription_id'))
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(Text, nullable=False)
    status = Column(Text, default='pending')
    created_at = Column(DateTime(timezone=True), default=func.now())

class GenerationLimits(Base):
    __tablename__ = 'generation_limits'
    
    tier = Column(Text, primary_key=True)
    max_generations = Column(Integer, nullable=False)

class UserGeneration(Base):
    __tablename__ = 'user_generations'
    
    user_thread_generation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    generations_used = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=func.now())  
    updated_at = Column(DateTime(timezone=True), default=func.now())

    # Relationship
    profile = relationship("Profile")

class CheckpointMigrations(Base):
    __tablename__ = 'checkpoint_migrations'
    
    v = Column(Integer, primary_key=True)