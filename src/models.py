"""
SQLAlchemy ORM models for Diablo 4 Item Comparator
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import (
    Boolean, Column, Integer, String, Text, DECIMAL, TIMESTAMP,
    ForeignKey, ARRAY, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


# ============================================================================
# REFERENCE DATA TABLES
# ============================================================================

class ItemType(Base):
    """Item type classifications (Helm, Sword, Ring, etc.)"""
    __tablename__ = 'item_types'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    internal_id = Column(String(100), unique=True)
    slot = Column(String(50))  # Head, MainHand, Finger, etc.
    is_weapon = Column(Boolean, default=False)
    is_armor = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    item_instances = relationship('ItemInstance', back_populates='item_type')

    def __repr__(self):
        return f"<ItemType(name='{self.name}', slot='{self.slot}')>"


class Class(Base):
    """Character classes"""
    __tablename__ = 'classes'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    internal_id = Column(String(50), unique=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    builds = relationship('Build', back_populates='character_class')
    item_instances = relationship('ItemInstance', back_populates='class_restriction')

    def __repr__(self):
        return f"<Class(name='{self.name}')>"


class AffixCategory(Base):
    """Affix categories (Offensive, Defensive, Utility, etc.)"""
    __tablename__ = 'affix_categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    affixes = relationship('Affix', back_populates='category')

    def __repr__(self):
        return f"<AffixCategory(name='{self.name}')>"


class Affix(Base):
    """Affix definitions with ranges and restrictions"""
    __tablename__ = 'affixes'

    id = Column(Integer, primary_key=True)
    internal_id = Column(String(200), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey('affix_categories.id'))

    # Value ranges
    min_value = Column(DECIMAL(10, 2))
    max_value = Column(DECIMAL(10, 2))
    is_percentage = Column(Boolean, default=False)

    # Affix types
    is_implicit = Column(Boolean, default=False)
    is_tempering = Column(Boolean, default=False)
    magic_type = Column(Integer, default=0)  # 0=Affix, 1=Legendary, 2=Unique, 4=Mythic

    # Restrictions (PostgreSQL arrays)
    allowed_item_types = Column(ARRAY(Integer))
    allowed_classes = Column(ARRAY(Integer))

    # Metadata
    priority_tier = Column(Integer, default=5)  # 1=highest, 10=lowest
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    category = relationship('AffixCategory', back_populates='affixes')
    item_instance_affixes = relationship('ItemInstanceAffix', back_populates='affix')
    build_weights = relationship('BuildAffixWeight', back_populates='affix')

    # Indexes
    __table_args__ = (
        Index('idx_affixes_category', 'category_id'),
        Index('idx_affixes_internal_id', 'internal_id'),
        Index('idx_affixes_allowed_types', 'allowed_item_types', postgresql_using='gin'),
        Index('idx_affixes_allowed_classes', 'allowed_classes', postgresql_using='gin'),
    )

    def __repr__(self):
        return f"<Affix(name='{self.name}', range=[{self.min_value}-{self.max_value}])>"


class Aspect(Base):
    """Legendary and Unique aspects"""
    __tablename__ = 'aspects'

    id = Column(Integer, primary_key=True)
    internal_id = Column(String(200), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50))  # Offensive, Defensive, Utility, Mobility, Resource

    # Value ranges (if aspect has variable scaling)
    min_value = Column(DECIMAL(10, 2))
    max_value = Column(DECIMAL(10, 2))
    scaling_formula = Column(Text)

    # Restrictions
    allowed_classes = Column(ARRAY(Integer))
    allowed_item_types = Column(ARRAY(Integer))
    is_unique_power = Column(Boolean, default=False)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    item_instance_aspects = relationship('ItemInstanceAspect', back_populates='aspect')

    def __repr__(self):
        return f"<Aspect(name='{self.name}', category='{self.category}')>"


# ============================================================================
# ITEM INSTANCE TABLES (OCR'd Items)
# ============================================================================

class ItemInstance(Base):
    """Specific item instances from OCR or manual entry"""
    __tablename__ = 'item_instances'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    item_type_id = Column(Integer, ForeignKey('item_types.id'), nullable=False)
    class_restriction_id = Column(Integer, ForeignKey('classes.id'))

    # Item stats
    item_power = Column(Integer)
    quality = Column(Integer)  # 0-8 rarity scale
    quality_bonus = Column(Integer, default=0)  # Tempering bonus
    rarity_stars = Column(Integer)  # Visual display (1-4 stars)

    # Item flags
    is_ancestral = Column(Boolean, default=False)
    is_unique = Column(Boolean, default=False)
    is_mythic = Column(Boolean, default=False)
    is_sanctified = Column(Boolean, default=False)
    is_account_bound = Column(Boolean, default=True)
    is_modifiable = Column(Boolean, default=True)

    # Additional info
    level_requirement = Column(Integer)
    sell_value = Column(Integer)
    unique_power_text = Column(Text)
    flavor_text = Column(Text)

    # OCR metadata
    screenshot_path = Column(String(500))
    ocr_confidence = Column(DECIMAL(3, 2))  # 0.00-1.00
    source = Column(String(20), default='ocr')  # ocr, manual, import

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    item_type = relationship('ItemType', back_populates='item_instances')
    class_restriction = relationship('Class', back_populates='item_instances')
    affixes = relationship('ItemInstanceAffix', back_populates='item_instance', cascade='all, delete-orphan')
    aspects = relationship('ItemInstanceAspect', back_populates='item_instance', cascade='all, delete-orphan')
    sockets = relationship('ItemInstanceSocket', back_populates='item_instance', cascade='all, delete-orphan')
    comparisons_as_a = relationship('ItemComparison', foreign_keys='ItemComparison.item_a_id', back_populates='item_a')
    comparisons_as_b = relationship('ItemComparison', foreign_keys='ItemComparison.item_b_id', back_populates='item_b')

    # Indexes
    __table_args__ = (
        Index('idx_item_instances_type', 'item_type_id'),
        Index('idx_item_instances_quality', 'quality'),
        CheckConstraint('quality >= 0 AND quality <= 8', name='check_quality_range'),
        CheckConstraint('ocr_confidence >= 0 AND ocr_confidence <= 1', name='check_confidence_range'),
    )

    def __repr__(self):
        return f"<ItemInstance(name='{self.name}', power={self.item_power}, quality={self.quality})>"


class ItemInstanceAffix(Base):
    """Affixes on specific item instances with roll values"""
    __tablename__ = 'item_instance_affixes'

    id = Column(Integer, primary_key=True)
    item_instance_id = Column(Integer, ForeignKey('item_instances.id'), nullable=False)
    affix_id = Column(Integer, ForeignKey('affixes.id'), nullable=False)
    roll_value = Column(DECIMAL(10, 2), nullable=False)

    # Affix metadata
    is_greater_affix = Column(Boolean, default=False)
    is_tempered = Column(Boolean, default=False)
    is_implicit = Column(Boolean, default=False)
    affix_order = Column(Integer, default=0)  # Display order on tooltip

    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    item_instance = relationship('ItemInstance', back_populates='affixes')
    affix = relationship('Affix', back_populates='item_instance_affixes')

    # Indexes and constraints
    __table_args__ = (
        UniqueConstraint('item_instance_id', 'affix_id', 'affix_order', name='uq_item_affix_order'),
        Index('idx_item_instance_affixes_item', 'item_instance_id'),
        Index('idx_item_instance_affixes_affix', 'affix_id'),
    )

    def __repr__(self):
        return f"<ItemInstanceAffix(affix_id={self.affix_id}, roll={self.roll_value})>"


class ItemInstanceAspect(Base):
    """Aspects on specific item instances"""
    __tablename__ = 'item_instance_aspects'

    id = Column(Integer, primary_key=True)
    item_instance_id = Column(Integer, ForeignKey('item_instances.id'), nullable=False)
    aspect_id = Column(Integer, ForeignKey('aspects.id'), nullable=False)
    roll_value = Column(DECIMAL(10, 2))  # If aspect has variable scaling

    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    item_instance = relationship('ItemInstance', back_populates='aspects')
    aspect = relationship('Aspect', back_populates='item_instance_aspects')

    # Constraints
    __table_args__ = (
        UniqueConstraint('item_instance_id', 'aspect_id', name='uq_item_aspect'),
    )

    def __repr__(self):
        return f"<ItemInstanceAspect(aspect_id={self.aspect_id}, roll={self.roll_value})>"


class ItemInstanceSocket(Base):
    """Gem sockets on item instances"""
    __tablename__ = 'item_instance_sockets'

    id = Column(Integer, primary_key=True)
    item_instance_id = Column(Integer, ForeignKey('item_instances.id'), nullable=False)
    socket_index = Column(Integer, default=0)
    gem_type = Column(String(50))  # ruby, emerald, diamond, etc.
    is_empty = Column(Boolean, default=True)

    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    item_instance = relationship('ItemInstance', back_populates='sockets')

    def __repr__(self):
        return f"<ItemInstanceSocket(gem='{self.gem_type}', empty={self.is_empty})>"


# ============================================================================
# BUILD MANAGEMENT TABLES
# ============================================================================

class Build(Base):
    """User-defined character builds"""
    __tablename__ = 'builds'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    class_id = Column(Integer, ForeignKey('classes.id'), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    character_class = relationship('Class', back_populates='builds')
    affix_weights = relationship('BuildAffixWeight', back_populates='build', cascade='all, delete-orphan')
    comparisons = relationship('ItemComparison', back_populates='build')

    def __repr__(self):
        return f"<Build(name='{self.name}', class_id={self.class_id})>"


class BuildAffixWeight(Base):
    """Affix priority weights for builds"""
    __tablename__ = 'build_affix_weights'

    id = Column(Integer, primary_key=True)
    build_id = Column(Integer, ForeignKey('builds.id'), nullable=False)
    affix_id = Column(Integer, ForeignKey('affixes.id'), nullable=False)
    weight = Column(DECIMAL(5, 2), nullable=False)  # 0.00-100.00
    priority = Column(Integer, default=5)  # 1=highest priority
    is_required = Column(Boolean, default=False)
    notes = Column(Text)

    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    build = relationship('Build', back_populates='affix_weights')
    affix = relationship('Affix', back_populates='build_weights')

    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint('build_id', 'affix_id', name='uq_build_affix'),
        Index('idx_build_weights_build', 'build_id'),
        CheckConstraint('weight >= 0 AND weight <= 100', name='check_weight_range'),
    )

    def __repr__(self):
        return f"<BuildAffixWeight(build_id={self.build_id}, affix_id={self.affix_id}, weight={self.weight})>"


# ============================================================================
# COMPARISON HISTORY TABLES
# ============================================================================

class ItemComparison(Base):
    """History of item comparisons"""
    __tablename__ = 'item_comparisons'

    id = Column(Integer, primary_key=True)
    build_id = Column(Integer, ForeignKey('builds.id'), nullable=False)
    item_a_id = Column(Integer, ForeignKey('item_instances.id'), nullable=False)
    item_b_id = Column(Integer, ForeignKey('item_instances.id'), nullable=False)

    # Results
    winner = Column(String(10))  # 'item_a', 'item_b', 'tie'
    score_a = Column(DECIMAL(10, 2))
    score_b = Column(DECIMAL(10, 2))
    score_delta = Column(DECIMAL(10, 2))
    comparison_details = Column(JSONB)  # Detailed breakdown
    screenshot_path = Column(String(500))

    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    build = relationship('Build', back_populates='comparisons')
    item_a = relationship('ItemInstance', foreign_keys=[item_a_id], back_populates='comparisons_as_a')
    item_b = relationship('ItemInstance', foreign_keys=[item_b_id], back_populates='comparisons_as_b')

    # Indexes
    __table_args__ = (
        Index('idx_comparisons_build', 'build_id'),
        Index('idx_comparisons_created', 'created_at', postgresql_ops={'created_at': 'DESC'}),
        Index('idx_comparison_details', 'comparison_details', postgresql_using='gin'),
        CheckConstraint("winner IN ('item_a', 'item_b', 'tie')", name='check_winner_values'),
    )

    def __repr__(self):
        return f"<ItemComparison(winner='{self.winner}', delta={self.score_delta})>"


class OCRCache(Base):
    """Cache of OCR processing results"""
    __tablename__ = 'ocr_cache'

    id = Column(Integer, primary_key=True)
    image_hash = Column(String(64), unique=True, nullable=False)  # SHA256
    image_path = Column(String(500))
    extracted_data = Column(JSONB)
    confidence_score = Column(DECIMAL(3, 2))
    processing_time_ms = Column(Integer)
    ocr_engine_version = Column(String(50))

    created_at = Column(TIMESTAMP, server_default=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_ocr_cache_hash', 'image_hash'),
        Index('idx_ocr_extracted_data', 'extracted_data', postgresql_using='gin'),
    )

    def __repr__(self):
        return f"<OCRCache(hash='{self.image_hash[:8]}...', confidence={self.confidence_score})>"
