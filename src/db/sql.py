from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import create_engine
import datetime
from sqlalchemy import Column, Integer, String, Enum, DateTime, Text
from sqlalchemy.orm import declarative_base
from datamodel import AgentStatus

Base = declarative_base()

class Agent(Base):
    __tablename__ = 'agents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    status = Column(Enum(AgentStatus))
    started_at = Column(DateTime)
    completed_at = Column(DateTime, nullable=True)
    steps = Column(Text, nullable=True)  # can store as a JSON string or plain text

# Tweets Table
class TweetDB(Base):
    __tablename__ = "tweets"
    
    tweet_id = Column(String(50), primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False)
    full_text = Column(Text, nullable=False)
    language = Column(String(20), default="unknown")
    favorite_count = Column(Integer, default=0)
    retweet_count = Column(Integer, default=0)
    bookmark_count = Column(Integer, default=0)
    quote_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    screen_name = Column(String(50), nullable=False)
    user_name = Column(String(100), nullable=False)
    profile_image_url = Column(Text, nullable=False)
    is_retweet = Column(Boolean, default=False)
    is_quote = Column(Boolean, default=False)
    possibly_sensitive = Column(Boolean, default=False)

# URLs Table
class UrlDB(Base):
    __tablename__ = "urls"
    
    id = Column(Integer, primary_key=True)
    tweet_id = Column(String(50), ForeignKey("tweets.tweet_id"))
    index = Column(Integer)
    original_url = Column(Text, nullable=False)
    downloaded_path = Column(Text, nullable=True)
    type = Column(String(20), nullable=True)
    domain = Column(String(100), nullable=True)
    content_type = Column(String(20), nullable=True)
    file_category = Column(String(20), nullable=True)
    downloaded_at = Column(TIMESTAMP, nullable=True)

    tweet = relationship("TweetDB", back_populates="urls")

TweetDB.urls = relationship("UrlDB", back_populates="tweet")

# Media Table
class MediaDB(Base):
    __tablename__ = "media"
    
    id = Column(Integer, primary_key=True)
    tweet_id = Column(String(50), ForeignKey("tweets.tweet_id"))
    type = Column(String(20), nullable=False)
    original_url = Column(Text, nullable=False)
    final_url = Column(Text, nullable=True)
    downloaded_path = Column(Text, nullable=True)
    content_type = Column(String(20), nullable=True)
    thumbnail = Column(Text, nullable=True)
    downloaded_at = Column(TIMESTAMP, nullable=True)

    tweet = relationship("TweetDB", back_populates="media")

TweetDB.media = relationship("MediaDB", back_populates="tweet")

# Agent Tracking Table
class AgentTracking(Base):
    __tablename__ = "agent_tracking"
    
    id = Column(Integer, primary_key=True)
    tweet_id = Column(String(50), ForeignKey("tweets.tweet_id"))
    current_status = Column(
        String(50), 
        nullable=False, 
        default="TweetExtracted", 
        checkin_=('TweetExtracted', 'TweetClassified', 'TagsGenerated', 'BlogCreationStarted', 
                  'BlogCreationInProgress', 'SystemBlogGenerated', 'HumanReviewStarted', 
                  'HumanReviewInProgress', 'HumanReviewApproved', 'BlogScheduled', 
                  'BlogPublished', 'BlogArchived')
    )  # Fixed set of statuses for agent workflow
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


# Blog Details
class Blog(Base):
    __tablename__ = "blogs"
    
    id = Column(Integer, primary_key=True)
    tweet_id = Column(String(50), ForeignKey("tweets.tweet_id"))
    content = Column(Text, nullable=False)
    status = Column(
        String(50), 
        nullable=False, 
        default="Draft", 
        checkin_=('Draft', 'InReview', 'Approved', 'Scheduled', 'Published', 'Archived')
    )  # Fixed set of statuses for blog lifecycle
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


# Create Engine and Database Tables
def create_tables():
    engine = create_engine("postgresql+psycopg2://user:password@localhost/post_bot")
    Base.metadata.create_all(engine)

if __name__=="__main__":
    create_tables()
