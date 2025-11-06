"""
Database layer for storing articles, picks, and consensus data.
Uses SQLite with SQLAlchemy ORM.
"""

from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Text, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from typing import List, Optional
from core.models import Article, BettingPick, ConsensusPick, PickType, ConfidenceLevel
from core.logger import logger
from config.settings import settings

Base = declarative_base()


# Association table for many-to-many relationship between picks and sources
pick_sources = Table(
    'pick_sources',
    Base.metadata,
    Column('pick_id', Integer, ForeignKey('consensus_picks.id')),
    Column('source', String(100))
)


class ArticleModel(Base):
    """SQLAlchemy model for Article."""
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), unique=True, nullable=False)
    source = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    published_at = Column(DateTime, nullable=True)
    fetched_at = Column(DateTime, default=datetime.now)
    
    picks = relationship('BettingPickModel', back_populates='article')


class BettingPickModel(Base):
    """SQLAlchemy model for BettingPick."""
    __tablename__ = 'betting_picks'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('articles.id'), nullable=False)
    team_or_player = Column(String(200), nullable=False)
    pick_type = Column(String(50), nullable=False)
    confidence = Column(String(50), nullable=False)
    odds = Column(String(100), nullable=True)
    reasoning = Column(Text, nullable=True)
    source = Column(String(100), nullable=False)
    extracted_at = Column(DateTime, default=datetime.now)
    
    article = relationship('ArticleModel', back_populates='picks')


class ConsensusPickModel(Base):
    """SQLAlchemy model for ConsensusPick."""
    __tablename__ = 'consensus_picks'
    
    id = Column(Integer, primary_key=True)
    team_or_player = Column(String(200), nullable=False)
    pick_type = Column(String(50), nullable=False)
    frequency = Column(Integer, nullable=False)
    average_confidence = Column(Float, nullable=False)
    consensus_score = Column(Float, nullable=False)
    reasoning_samples = Column(Text, nullable=True)  # JSON string
    calculated_at = Column(DateTime, default=datetime.now)


class Database:
    """Database manager for the application."""
    
    def __init__(self, database_url: str = settings.database_url):
        """
        Initialize database connection.
        
        Args:
            database_url: Database connection URL
        """
        self.database_url = database_url
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(self.engine)
        logger.info(f"Database initialized: {database_url}")
    
    def save_article(self, article: Article) -> Optional[int]:
        """
        Save an article to the database.
        
        Args:
            article: Article object to save
            
        Returns:
            Article ID or None if failed
        """
        session = self.SessionLocal()
        try:
            # Check if article already exists
            existing = session.query(ArticleModel).filter_by(url=article.url).first()
            if existing:
                logger.debug(f"Article already exists: {article.url}")
                return existing.id
            
            # Create new article
            db_article = ArticleModel(
                title=article.title,
                url=article.url,
                source=article.source,
                content=article.content,
                published_at=article.published_at,
                fetched_at=article.fetched_at,
            )
            
            session.add(db_article)
            session.commit()
            
            logger.debug(f"Saved article: {article.title}")
            return db_article.id
        
        except Exception as e:
            logger.error(f"Error saving article: {e}")
            session.rollback()
            return None
        finally:
            session.close()
    
    def save_picks(self, picks: List[BettingPick]) -> int:
        """
        Save betting picks to the database.
        
        Args:
            picks: List of BettingPick objects
            
        Returns:
            Number of picks saved
        """
        session = self.SessionLocal()
        saved_count = 0
        
        try:
            for pick in picks:
                db_pick = BettingPickModel(
                    article_id=pick.article_id,
                    team_or_player=pick.team_or_player,
                    pick_type=pick.pick_type.value,
                    confidence=pick.confidence.value,
                    odds=pick.odds,
                    reasoning=pick.reasoning,
                    source=pick.source,
                    extracted_at=pick.extracted_at,
                )
                session.add(db_pick)
                saved_count += 1
            
            session.commit()
            logger.debug(f"Saved {saved_count} picks to database")
            return saved_count
        
        except Exception as e:
            logger.error(f"Error saving picks: {e}")
            session.rollback()
            return 0
        finally:
            session.close()
    
    def save_consensus_picks(self, consensus_picks: List[ConsensusPick]) -> int:
        """
        Save consensus picks to the database.
        
        Args:
            consensus_picks: List of ConsensusPick objects
            
        Returns:
            Number of consensus picks saved
        """
        session = self.SessionLocal()
        saved_count = 0
        
        try:
            for consensus in consensus_picks:
                db_consensus = ConsensusPickModel(
                    team_or_player=consensus.team_or_player,
                    pick_type=consensus.pick_type.value,
                    frequency=consensus.frequency,
                    average_confidence=consensus.average_confidence,
                    consensus_score=consensus.consensus_score,
                    reasoning_samples=str(consensus.reasoning_samples),
                    calculated_at=consensus.calculated_at,
                )
                session.add(db_consensus)
                saved_count += 1
            
            session.commit()
            logger.debug(f"Saved {saved_count} consensus picks to database")
            return saved_count
        
        except Exception as e:
            logger.error(f"Error saving consensus picks: {e}")
            session.rollback()
            return 0
        finally:
            session.close()
    
    def get_recent_consensus_picks(self, limit: int = 50) -> List[ConsensusPick]:
        """
        Get recent consensus picks from database.
        
        Args:
            limit: Maximum number of picks to return
            
        Returns:
            List of ConsensusPick objects
        """
        session = self.SessionLocal()
        try:
            db_picks = session.query(ConsensusPickModel).order_by(
                ConsensusPickModel.calculated_at.desc()
            ).limit(limit).all()
            
            picks = []
            for db_pick in db_picks:
                pick = ConsensusPick(
                    team_or_player=db_pick.team_or_player,
                    pick_type=PickType(db_pick.pick_type),
                    frequency=db_pick.frequency,
                    average_confidence=db_pick.average_confidence,
                    consensus_score=db_pick.consensus_score,
                    calculated_at=db_pick.calculated_at,
                )
                picks.append(pick)
            
            return picks
        
        except Exception as e:
            logger.error(f"Error retrieving consensus picks: {e}")
            return []
        finally:
            session.close()
    
    def close(self):
        """Close database connection."""
        self.engine.dispose()
        logger.debug("Database connection closed")

