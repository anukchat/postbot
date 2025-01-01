from sqlalchemy import Column, String, Text, Boolean, ForeignKey, ARRAY, TIMESTAMP, Integer, JSON, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
from supabase import create_client, Client


def supabase_client():
    # Initialize the Supabase client
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    return create_client(supabase_url, supabase_key)


# Base = declarative_base()

# # Profiles Table
# class Profiles(Base):
#     __tablename__ = "profiles"
    
#     id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
#     user_id = Column(String(50), ForeignKey("auth.users.id"), nullable=True)
#     full_name = Column(Text, nullable=True)
#     avatar_url = Column(Text, nullable=True)
#     role = Column(Text, default="free")
#     subscription_status = Column(Text, default="none")
#     subscription_end = Column(TIMESTAMP, nullable=True)
#     created_at = Column(TIMESTAMP, default=datetime.utcnow)
#     preferences = Column(JSON, default={"theme": "light", "defaultView": "blog", "emailNotifications": True})

#     # Relationships
#     content = relationship("Content", back_populates="profile")
#     subscriptions = relationship("Subscriptions", back_populates="profile")
#     user_activity = relationship("UserActivity", back_populates="profile")

# # ContentTypes Table
# class ContentTypes(Base):
#     __tablename__ = "content_types"
    
#     content_type_id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
#     name = Column(Text, unique=True, nullable=False)
#     created_at = Column(TIMESTAMP, default=datetime.utcnow)

#     # Relationships
#     content = relationship("Content", back_populates="content_type")

# # Content Table
# class Content(Base):
#     __tablename__ = "content"
    
#     content_id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
#     profile_id = Column(String(50), ForeignKey("profiles.id"), nullable=False)
#     content_type_id = Column(String(50), ForeignKey("content_types.content_type_id"), nullable=False)
#     title = Column(Text, nullable=True)
#     body = Column(Text, nullable=True)
#     status = Column(Text, default="draft")
#     created_at = Column(TIMESTAMP, default=datetime.utcnow)
#     updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
#     published_at = Column(TIMESTAMP, nullable=True)

#     # Relationships
#     profile = relationship("Profiles", back_populates="content")
#     content_type = relationship("ContentTypes", back_populates="content")
#     content_sources = relationship("ContentSources", back_populates="content")
#     content_tags = relationship("ContentTags", back_populates="content")
#     content_analytics = relationship("ContentAnalytics", back_populates="content")
    
# # Sources Table
# class Sources(Base):
#     __tablename__ = "sources"
    
#     source_id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
#     type = Column(Text, nullable=False)
#     source_identifier = Column(Text, nullable=False)
#     created_at = Column(TIMESTAMP, default=datetime.utcnow)
#     updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

#     # Relationships
#     content_sources = relationship("ContentSources", back_populates="source")
#     url_references = relationship("URLReferences", back_populates="source")
#     media = relationship("Media", back_populates="source")
#     metadata = relationship("Metadata", back_populates="source")
#     custom_field_values = relationship("CustomFieldValues", back_populates="source")
    
# # ContentSources Table
# class ContentSources(Base):
#     __tablename__ = "content_sources"
    
#     content_source_id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
#     content_id = Column(String(50), ForeignKey("content.content_id"), nullable=False)
#     source_id = Column(String(50), ForeignKey("sources.source_id"), nullable=False)
#     created_at = Column(TIMESTAMP, default=datetime.utcnow)

#     # Relationships
#     content = relationship("Content", back_populates="content_sources")
#     source = relationship("Sources", back_populates="content_sources")

# # URLReferences Table
# class URLReferences(Base):
#     __tablename__ = "url_references"
    
#     url_reference_id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
#     source_id = Column(String(50), ForeignKey("sources.source_id"), nullable=False)
#     url = Column(Text, nullable=False)
#     description = Column(Text, nullable=True)
#     created_at = Column(TIMESTAMP, default=datetime.utcnow)

#     # Relationships
#     source = relationship("Sources", back_populates="url_references")

# # Media Table
# class Media(Base):
#     __tablename__ = "media"
    
#     media_id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
#     source_id = Column(String(50), ForeignKey("sources.source_id"), nullable=False)
#     media_url = Column(Text, nullable=False)
#     media_type = Column(Text, nullable=False)
#     created_at = Column(TIMESTAMP, default=datetime.utcnow)

#     # Relationships
#     source = relationship("Sources", back_populates="media")

# # Tags Table
# class Tags(Base):
#     __tablename__ = "tags"
    
#     tag_id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
#     name = Column(Text, unique=True, nullable=False)
#     created_at = Column(TIMESTAMP, default=datetime.utcnow)

#     # Relationships
#     content_tags = relationship("ContentTags", back_populates="tag")

# # ContentTags Table
# class ContentTags(Base):
#     __tablename__ = "content_tags"
    
#     content_tag_id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
#     content_id = Column(String(50), ForeignKey("content.content_id"), nullable=False)
#     tag_id = Column(String(50), ForeignKey("tags.tag_id"), nullable=False)
#     created_at = Column(TIMESTAMP, default=datetime.utcnow)

#     # Relationships
#     content = relationship("Content", back_populates="content_tags")
#     tag = relationship("Tags", back_populates="content_tags")

# # Metadata Table
# class Metadata(Base):
#     __tablename__ = "metadata"
    
#     metadata_id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
#     source_id = Column(String(50), ForeignKey("sources.source_id"), nullable=False)
#     key = Column(Text, nullable=False)
#     value = Column(Text, nullable=True)
#     created_at = Column(TIMESTAMP, default=datetime.utcnow)

#     # Relationships
#     source = relationship("Sources", back_populates="metadata")

# # CustomFields Table
# class CustomFields(Base):
#     __tablename__ = "custom_fields"
    
#     custom_field_id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
#     source_type = Column(Text, nullable=False)
#     field_name = Column(Text, nullable=False)
#     field_type = Column(Text, nullable=False)
#     created_at = Column(TIMESTAMP, default=datetime.utcnow)

#     # Relationships
#     custom_field_values = relationship("CustomFieldValues", back_populates="custom_field")

# # CustomFieldValues Table
# class CustomFieldValues(Base):
#     __tablename__ = "custom_field_values"
    
#     custom_field_value_id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
#     source_id = Column(String(50), ForeignKey("sources.source_id"), nullable=False)
#     custom_field_id = Column(String(50), ForeignKey("custom_fields.custom_field_id"), nullable=False)
#     value = Column(Text, nullable=True)
#     created_at = Column(TIMESTAMP, default=datetime.utcnow)

#     # Relationships
#     source = relationship("Sources", back_populates="custom_field_values")
#     custom_field = relationship("CustomFields", back_populates="custom_field_values")

# # ContentAnalytics Table
# class ContentAnalytics(Base):
#     __tablename__ = "content_analytics"
    
#     analytics_id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
#     content_id = Column(String(50), ForeignKey("content.content_id"), nullable=False)
#     views = Column(Integer, default=0)
#     likes = Column(Integer, default=0)
#     shares = Column(Integer, default=0)
#     created_at = Column(TIMESTAMP, default=datetime.utcnow)
#     updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

#     # Relationships
#     content = relationship("Content", back_populates="content_analytics")

# # UserActivity Table
# class UserActivity(Base):
#     __tablename__ = "user_activity"
    
#     activity_id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
#     profile_id = Column(String(50), ForeignKey("profiles.id"), nullable=False)
#     activity_type = Column(Text, nullable=False)
#     activity_details = Column(JSON, nullable=True)
#     created_at = Column(TIMESTAMP, default=datetime.utcnow)

#     # Relationships
#     profile = relationship("Profiles", back_populates="user_activity")

# # Plans Table
# class Plans(Base):
#     __tablename__ = "plans"
    
#     plan_id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
#     name = Column(Text, nullable=False)
#     price = Column(DECIMAL(10, 2), nullable=False)
#     features = Column(JSON, nullable=True)
#     created_at = Column(TIMESTAMP, default=datetime.utcnow)

#     # Relationships
#     subscriptions = relationship("Subscriptions", back_populates="plan")

# # Subscriptions Table
# class Subscriptions(Base):
#     __tablename__ = "subscriptions"
    
#     subscription_id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
#     profile_id = Column(String(50), ForeignKey("profiles.id"), nullable=False)
#     plan_id = Column(String(50), ForeignKey("plans.plan_id"), nullable=False)
#     start_date = Column(TIMESTAMP, nullable=False)
#     end_date = Column(TIMESTAMP, nullable=True)
#     status = Column(Text, default="active")
#     created_at = Column(TIMESTAMP, default=datetime.utcnow)

#     # Relationships
#     profile = relationship("Profiles", back_populates="subscriptions")
#     plan = relationship("Plans", back_populates="subscriptions")
#     payments = relationship("Payments", back_populates="subscription")

# # Payments Table
# class Payments(Base):
#     __tablename__ = "payments"
    
#     payment_id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
#     subscription_id = Column(String(50), ForeignKey("subscriptions.subscription_id"), nullable=False)
#     amount = Column(DECIMAL(10, 2), nullable=False)
#     payment_method = Column(Text, nullable=False)
#     status = Column(Text, default="pending")
#     created_at = Column(TIMESTAMP, default=datetime.utcnow)

#     # Relationships
#     subscription = relationship("Subscriptions", back_populates="payments")


