import logging
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

Base = declarative_base()


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    articles = relationship("Article", back_populates="category")


class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    url = Column(String, nullable=False)
    title = Column(String)
    content = Column(String)
    summary = Column(String)
    image_url = Column(String)
    category = relationship("Category", back_populates="articles")


# Create engine and bind it
try:
    engine = create_engine("sqlite:///db.sqlite", echo=False)
    logger.info("Database engine created successfully")
    Base.metadata.create_all(engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    raise

# Create session factory
Session = sessionmaker(bind=engine)
logger.info("Session factory created")
