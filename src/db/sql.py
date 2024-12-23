from sqlalchemy import create_engine,inspect, Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import create_engine
import datetime
from sqlalchemy import Column, Integer, String, Enum, DateTime, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import declarative_base
# from db.enums import AgentStatus  # Import from enums.py
from sqlalchemy.orm import sessionmaker, scoped_session
import uuid  # Import the uuid module
import uuid
from psycopg_pool import ConnectionPool
from sqlalchemy.orm.exc import NoResultFound
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.schema import MetaData, Table
from sqlalchemy.sql import text
from enum import Enum, auto
Base = declarative_base()

#------------DB Models------------

class AgentStatus(Enum):
    STARTED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED =  auto()
    PENDING = auto()

class BlogStatus(str, Enum):
    ALL= 'All'
    DRAFT = 'Draft'
    PUBLISHED = 'Published'
    SCHEDULED = 'Scheduled'
    ARCHIVED = 'Archived'
    REJECTED = 'Rejected'
    DELETED = 'Deleted'

class BlogStyleTypes(str, Enum):
    Academic = 'Academic'
    Developer = 'Developer'
    Technical = 'Technical'
    Innovative = 'Innovative'
    Pragmatic = 'Pragmatic'
    Research = 'Research'
    StartupInnovator = 'StartupInnovator'
    Statistical = 'Statistical'
    TechReviewer = 'TechReviewer'
    Visionary = 'Visionary'  

class Agent(Base):
    __tablename__ = 'agents'

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))  # Use UUID as default
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255))
    status = status = Column(
        String(50), 
        nullable=False, 
        default=AgentStatus.PENDING,
    )
    started_at = Column(DateTime)
    completed_at = Column(DateTime, nullable=True)
    steps = Column(Text, nullable=True)  # can store as a JSON string or plain text

    @classmethod
    def create(cls, session, name, status, started_at):
        """Create a new Agent."""
        agent = cls(name=name, status=status, started_at=started_at)
        session.add(agent)
        session.commit()
        return agent
    
    @classmethod
    def update(cls, session, id, status=None, completed_at=None, steps=None):
        """Update an Agent."""
        agent = session.query(cls).filter(cls.id == id).first()
        if agent:
            if status:
                agent.status = status
            if completed_at:
                agent.completed_at = completed_at
            if steps:
                agent.steps = steps
            session.commit()
        return agent

class Tweets(Base):
    __tablename__ = "tweets"
    
    tweet_id = Column(String(50), primary_key=True,default=lambda: str(uuid.uuid4()))
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

    @classmethod
    def get_all(cls, session):
        """Retrieve all tweets from the database."""
        return session.query(cls).all()
    
    @classmethod
    def read(cls, session, tweet_id=None):
        query = session.query(cls)        
        query = query.filter(cls.tweet_id == tweet_id)
        return query.all()

# URLs Table
class Urls(Base):
    __tablename__ = "urls"
    
    id = Column(String(50), primary_key=True,default=lambda: str(uuid.uuid4()))
    tweet_id = Column(String(50), ForeignKey("tweets.tweet_id"))
    index = Column(Integer)
    original_url = Column(Text, nullable=False)
    downloaded_path = Column(Text, nullable=True)
    downloaded_path_md = Column(Text, nullable=True)
    type = Column(String(20), nullable=True)
    domain = Column(String(100), nullable=True)
    content_type = Column(String(20), nullable=True)
    file_category = Column(String(20), nullable=True)
    downloaded_at = Column(TIMESTAMP, nullable=True)

    tweet = relationship("Tweets", back_populates="urls")
Tweets.urls = relationship("Urls", back_populates="tweet")

# Media Table
class Medias(Base):
    __tablename__ = "media"
    
    id = Column(String(50), primary_key=True,default=lambda: str(uuid.uuid4()))
    tweet_id = Column(String(50), ForeignKey("tweets.tweet_id"))
    type = Column(String(20), nullable=False)
    original_url = Column(Text, nullable=False)
    final_url = Column(Text, nullable=True)
    downloaded_path = Column(Text, nullable=True)
    content_type = Column(String(20), nullable=True)
    thumbnail = Column(Text, nullable=True)
    downloaded_at = Column(TIMESTAMP, nullable=True)

    tweet = relationship("Tweets", back_populates="media")
Tweets.media = relationship("Medias", back_populates="tweet")

# Blog Details
class Blogs(Base):
    __tablename__ = "blogs"
    
    id = Column(String(50), primary_key=True,default=lambda: str(uuid.uuid4()))
    tweet_id = Column(String(50), ForeignKey("tweets.tweet_id"))
    title=Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    status = Column(
        String(50), 
        nullable=False, 
        default=BlogStatus.DRAFT,
    )
    blog_category = Column(ARRAY(String), nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    style_id = Column(String(50),ForeignKey("blogstyles.id"))
    is_deleted = Column(Boolean, nullable=False)
    is_archived = Column(Boolean, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.now(datetime.UTC))
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.now(datetime.UTC), onupdate=datetime.datetime.now(datetime.UTC))

    @classmethod
    def get_all(cls, session):
        """Retrieve all blog styles from the database."""
        return session.query(cls).all()
    
    @classmethod
    def create(cls, session, tweet_id, content, blog_category, tags,status="Draft", style_id=None):
        blog = cls(tweet_id=tweet_id, content=content, tags=tags,blog_category=blog_category,status=status, style_id=style_id)
        session.add(blog)
        session.commit()
        return blog

    @classmethod
    def read(cls, session, id=None, tweet_id=None, status=None,is_deleted=False,is_archived=False):
        query = session.query(cls)
        query = query.filter(cls.is_deleted == is_deleted and cls.is_archived == is_archived)
        if id:
            query = query.filter(cls.id == id)
        if tweet_id:
            query = query.filter(cls.tweet_id == tweet_id)
        if status:
            query = query.filter(cls.status == status)
        return query.one_or_none()

    @classmethod
    def update(cls, session, id, content=None, status=None, style_id=None, blog_category=None, tags=None):
        blog = session.query(cls).filter(cls.id == id).first()
        if blog:
            if content:
                blog.content = content
            if status:
                blog.status = status
            if style_id:
                blog.style_id = style_id
            if blog_category:
                blog.blog_category = blog_category
            if tags:
                blog.tags = tags
            session.commit()
            return blog
        return None

    @classmethod
    def delete(cls, session, id):
        blog = session.query(cls).filter(cls.id == id).first()
        if blog:
            blog.is_deleted=True
            session.commit()
            return True
        return False
    
    @classmethod
    def archive(cls, session, id):
        blog = session.query(cls).filter(cls.id == id).first()
        if blog:
            blog.is_archived=True
            session.commit()
            return True
        return False

    @classmethod
    def get_blogs_with_references(cls, session, search_text=None, tags=None, status=None, created_before=None, created_after=None, url_type=None, domain=None, style_id=None,skip=0, limit=10):
        """
        Retrieve blog posts along with their associated tweets, URLs, and media data,
        with optional filters and pagination.

        :param session: The database session to use.
        :param blog_id: Optional ID of the blog post to retrieve.
        :param tags: Optional list of tags to filter by.
        :param status: Optional status to filter by.
        :param created_before: Optional date to filter blogs created before this date.
        :param created_after: Optional date to filter blogs created after this date.
        :param url_type: Optional URL type to filter URLs.
        :param domain: Optional domain to filter URLs.
        :param skip: Number of records to skip for pagination.
        :param limit: Maximum number of records to return for pagination.
        :return: A list of dictionaries containing the blog, tweet, URLs, and media data.
        """
        query = session.query(cls).filter(cls.is_deleted == False and cls.is_archived == False)

        # Apply optional filter for blog_id
        if search_text:
            query = query.filter(cls.title.ilike(f"%{search_text}%"))

        # Apply additional filters to the blog query if provided
        if tags:
            # Split tags if provided as a string
            if isinstance(tags, str):
                tags = [tag.strip() for tag in tags.split(',')]
            query = query.filter(cls.tags.overlap(tags))  # Use PostgreSQL's overlap operator

        if style_id:
            query = query.filter(cls.style_id == style_id)

        if status:
            if status=='All':
                query=query
            else:
                query = query.filter(cls.status == status)

        if created_before:
            query = query.filter(cls.created_at < created_before)

        if created_after:
            query = query.filter(cls.created_at > created_after)

        # Apply pagination
        query = query.offset(skip).limit(limit)

        # Retrieve all matching blogs
        blogs = query.all()
        if not blogs:
            return []  # Return an empty list if no blogs are found

        # Prepare the results
        results = []
        for blog in blogs:
            tweet = session.query(Tweets).filter(Tweets.tweet_id == blog.tweet_id).one_or_none()
            urls_query = session.query(Urls).filter(Urls.tweet_id == blog.tweet_id)

            # Apply optional filters to URLs
            if url_type:
                urls_query = urls_query.filter(Urls.type == url_type)
            if domain:
                urls_query = urls_query.filter(Urls.domain == domain)

            urls = urls_query.all()
            media = session.query(Medias).filter(Medias.tweet_id == blog.tweet_id).all()

            # Prepare blog data
            blog_data = {
                "blog": {
                    "id": blog.id,
                    "tweet_id": blog.tweet_id,
                    "title": blog.title,
                    "content": blog.content,
                    "status": blog.status,
                    "blog_category": blog.blog_category,
                    "tags": blog.tags,
                    "style_id": blog.style_id,
                    "created_at": blog.created_at,
                    "updated_at": blog.updated_at,
                },
                "tweet": {
                    "tweet_id": tweet.tweet_id,
                    "full_text": tweet.full_text,
                    "created_at": tweet.created_at,
                    "language": tweet.language,
                    "screen_name": tweet.screen_name,
                    "user_name": tweet.user_name,
                    "profile_image_url": tweet.profile_image_url,
                } if tweet else None,
                "urls": [
                    {
                        "id": url.id,
                        "original_url": url.original_url,
                        "downloaded_path": url.downloaded_path,
                        "type": url.type,
                        "domain": url.domain,
                    }
                    for url in urls
                ],
                "media": [
                    {
                        "id": media_item.id,
                        "original_url": media_item.original_url,
                        "final_url": media_item.final_url,
                        "type": media_item.type,
                        "thumbnail": media_item.thumbnail,
                    }
                    for media_item in media
                ],
            }
            results.append(blog_data)

        return results  # Return the list of blog data

class BlogStyles(Base):
    __tablename__="blogstyles"

    id = Column(String(50), primary_key=True,default=lambda: str(uuid.uuid4()))
    style = Column(Text, nullable=False, default=BlogStyleTypes.Academic)
    filename = Column(Text, nullable=True)
    style_prompt = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.now(datetime.UTC))
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.now(datetime.UTC), onupdate=datetime.datetime.now(datetime.UTC))

    @classmethod
    def get_all(cls, session):
        """Retrieve all blog styles from the database."""
        return session.query(cls).all()
    
    @classmethod
    def create(cls, session, style="Academic", filename=None, style_prompt=None):
        blog_style = cls(style=style, filename=filename, style_prompt=style_prompt)
        session.add(blog_style)
        session.commit()
        return blog_style

    @classmethod
    def read(cls, session, id):
        query = session.query(cls).filter(cls.id == id)
        
        return query.one_or_none()

    @classmethod
    def update(cls, session, id, style=None, filename=None, style_prompt=None):
        blog_style = session.query(cls).filter(cls.id == id).first()
        if blog_style:
            if style:
                blog_style.style = style
            if filename:
                blog_style.filename = filename
            if style_prompt:
                blog_style.style_prompt = style_prompt
            session.commit()
            return blog_style
        return None

    @classmethod
    def delete(cls, session, id):
        blog_style = session.query(cls).filter(cls.id == id).first()
        if blog_style:
            session.delete(blog_style)
            session.commit()
            return True
        return False

#------------------------------------
def store_tweet_data(tweet_data):
    """
    Store tweet JSON data into the database.
    """
    db_gen = get_db()  # Get the generator object
    session = next(db_gen)  # Extract the session
    try:
        for tweet_json in tweet_data:
            # Extract tweet-level data
            if not Tweets.read(session,tweet_id=tweet_json["tweet_id"]):
                tweet = Tweets(
                    tweet_id=tweet_json["tweet_id"],
                    created_at=datetime.datetime.fromisoformat(tweet_json["created_at"]),
                    full_text=tweet_json["full_text"],
                    language=tweet_json.get("language", "unknown"),
                    favorite_count=tweet_json.get("favorite_count", 0),
                    retweet_count=tweet_json.get("retweet_count", 0),
                    bookmark_count=tweet_json.get("bookmark_count", 0),
                    quote_count=tweet_json.get("quote_count", 0),
                    reply_count=tweet_json.get("reply_count", 0),
                    views_count=tweet_json.get("views_count", 0),
                    screen_name=tweet_json["screen_name"],
                    user_name=tweet_json["user_name"],
                    profile_image_url=tweet_json["profile_image_url"],
                    is_retweet=tweet_json.get("is_retweet", False),
                    is_quote=tweet_json.get("is_quote", False),
                    possibly_sensitive=tweet_json.get("possibly_sensitive", False),
                )
                session.add(tweet)

                # Add URLs
                for url_data in tweet_json.get("urls", []):
                    url = Urls(
                        id=str(uuid.uuid4()),
                        tweet_id=tweet_json["tweet_id"],
                        index=url_data["index"],
                        original_url=url_data["original_url"],
                        downloaded_path=url_data.get("downloaded_path"),
                        downloaded_path_md=url_data.get("downloaded_path_md"),
                        type=url_data.get("type"),
                        domain=url_data.get("domain"),
                        content_type=url_data.get("content_type"),
                        file_category=url_data.get("file_category"),
                        downloaded_at=datetime.datetime.fromisoformat(url_data["downloaded_at"]) if url_data.get("downloaded_at") else None,
                    )
                    session.add(url)

                # Add Media
                for media_data in tweet_json.get("media", []):
                    media = Medias(
                        id=str(uuid.uuid4()),
                        tweet_id=tweet_json["tweet_id"],
                        type=media_data["type"],
                        original_url=media_data["original_url"],
                        final_url=media_data.get("final_url"),
                        downloaded_path=media_data.get("downloaded_path"),
                        content_type=media_data.get("content_type"),
                        thumbnail=media_data.get("thumbnail"),
                        downloaded_at=datetime.datetime.fromisoformat(media_data["downloaded_at"]) if media_data.get("downloaded_at") else None,
                    )
                    session.add(media)

        session.commit()  # Commit all transactions at once
    except Exception as e:
        session.rollback()  # Rollback in case of any error
        raise e  # Re-raise the exception for further handling
    finally:
        db_gen.close()  # Ensure the generator is closed

def get_tweet_by_id(tweet_id):
    """
    Retrieve a tweet record from the database by its tweet_id.
    
    :param tweet_id: The unique ID of the tweet to retrieve.
    :return: A dictionary representing the tweet and its related data (URLs and media).
    :raises: Exception if the tweet is not found or any database error occurs.
    """
    db_gen = get_db()  # Get the database session generator
    session = next(db_gen)  # Extract a session from the generator

    try:
        # Query the TweetDB table for the given tweet_id
        tweet = session.query(Tweets).filter_by(tweet_id=tweet_id).one()
        
        # Convert the tweet and related data into a dictionary
        tweet_data = {
            "tweet_id": tweet.tweet_id,
            "created_at": tweet.created_at,
            "full_text": tweet.full_text,
            "language": tweet.language,
            "favorite_count": tweet.favorite_count,
            "retweet_count": tweet.retweet_count,
            "bookmark_count": tweet.bookmark_count,
            "quote_count": tweet.quote_count,
            "reply_count": tweet.reply_count,
            "views_count": tweet.views_count,
            "screen_name": tweet.screen_name,
            "user_name": tweet.user_name,
            "profile_image_url": tweet.profile_image_url,
            "is_retweet": tweet.is_retweet,
            "is_quote": tweet.is_quote,
            "possibly_sensitive": tweet.possibly_sensitive,
            "urls": [
                {
                    "id": url.id,
                    "index": url.index,
                    "original_url": url.original_url,
                    "downloaded_path": url.downloaded_path,
                    "downloaded_path_md": url.downloaded_path_md,
                    "type": url.type,
                    "domain": url.domain,
                    "content_type": url.content_type,
                    "file_category": url.file_category,
                    "downloaded_at": url.downloaded_at,
                }
                for url in tweet.urls
            ],
            "media": [
                {
                    "id": media.id,
                    "type": media.type,
                    "original_url": media.original_url,
                    "final_url": media.final_url,
                    "downloaded_path": media.downloaded_path,
                    "content_type": media.content_type,
                    "thumbnail": media.thumbnail,
                    "downloaded_at": media.downloaded_at,
                }
                for media in tweet.media
            ],
        }
        return tweet_data
    except NoResultFound:
        raise Exception(f"No tweet found with tweet_id {tweet_id}.")
    except Exception as e:
        raise e  # Reraise any other exceptions
    finally:
        db_gen.close()  # Ensure the generator is closed

#------------DB Operations------------

def safe_add_column(engine, table_name, column_name, column_type):
    """Safely add a column if it doesn't exist"""
    inspector = inspect(engine)
    has_column = False
    for col in inspector.get_columns(table_name):
        if col['name'] == column_name:
            has_column = True
    if not has_column:
        with engine.begin() as connection:
            connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column_name} {column_type}"))

def create_version_table(engine):
    """Create version tracking table if it doesn't exist"""
    metadata = MetaData()
    version_table = Table(
        'schema_version',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('version', String(50)),
        Column('updated_at', TIMESTAMP, default=datetime.datetime.now(datetime.UTC))
    )
    if not inspect(engine).has_table('schema_version'):
        version_table.create(engine)
    return version_table

def apply_schema_updates(engine):
    """Apply schema updates preserving data"""
    # Create version table
    version_table = create_version_table(engine)
    
    try:
        # Add new columns safely
        safe_add_column(engine, 'blogs', 'title', 'TEXT')
        safe_add_column(engine, 'blogs', 'is_deleted', 'BOOLEAN DEFAULT FALSE')
        safe_add_column(engine, 'blogs', 'is_archived', 'BOOLEAN DEFAULT FALSE')
        
        # Update schema version
        with engine.begin() as connection:
            connection.execute(
                version_table.insert().values(
                    version='1.1',
                    updated_at=datetime.datetime.now(datetime.UTC)
                )
            )
        
        return True
    except Exception as e:
        print(f"Error updating schema: {e}")
        return False

def create_tables():
    """Create or update tables"""
    engine = create_engine("postgresql+psycopg2://postbot:postbot12345@localhost/post_bot")
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if not tables:
        Base.metadata.create_all(engine)
        print("Created new database schema")
    else:
        if apply_schema_updates(engine):
            print("Schema updates applied successfully")
        else:
            print("Schema update failed")

# Create a new SQLAlchemy engine
engine = create_engine("postgresql+psycopg2://postbot:postbot12345@localhost/post_bot")

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a scoped session
db_session = scoped_session(SessionLocal)

def get_db():
    """
    Provides a database session for use in a context manager.
    Yields a session and ensures it is closed after use.
    """
    db = db_session()  # Create a new session
    try:
        yield db          # Yield the session for use
    finally:
        db.close()       # Close the session after use

if __name__=="__main__":
    create_tables()
