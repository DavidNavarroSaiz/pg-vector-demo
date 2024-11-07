# db/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Text
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.types import UserDefinedType

Base = declarative_base()

class Vector(UserDefinedType):
    """Custom type to represent pgvector's VECTOR data type."""

    def get_col_spec(self):
        return "VECTOR(1536)"  # Adjust dimension as needed (e.g., 1536 for OpenAI embeddings)


# Define the tables

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String, nullable=False)
    permissions = Column(String, nullable=False)

class Category(Base):
    __tablename__ = 'categories'
    category_id = Column(Integer, primary_key=True)
    category_name = Column(String, nullable=False)

class Section(Base):
    __tablename__ = 'sections'
    section_id = Column(Integer, primary_key=True)
    section_name = Column(String, nullable=False)

class SubSection(Base):
    __tablename__ = 'sub_section'
    subsection_id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey('sections.section_id'), nullable=False)
    section_name = Column(String, nullable=False)
    section = relationship("Section", back_populates="subsections")

Section.subsections = relationship("SubSection", order_by=SubSection.subsection_id, back_populates="section")

class LearningType(Base):
    __tablename__ = 'learning_type'
    learning_type_id = Column(Integer, primary_key=True)
    name_type = Column(String, nullable=False)

class Resource(Base):
    __tablename__ = 'resources'
    id = Column(Integer, primary_key=True)
    sub_section_id = Column(Integer, ForeignKey('sub_section.subsection_id'), nullable=False)
    learning_type_id = Column(Integer, ForeignKey('learning_type.learning_type_id'), nullable=False)
    permissions_allowed = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.category_id'), nullable=False)
    resource_name = Column(String, nullable=False)
    path = Column(String, nullable=False)

    # Define relationships
    sub_section = relationship("SubSection")
    learning_type = relationship("LearningType")
    category = relationship("Category")
    embeddings = relationship("Embeddings", back_populates="resource", cascade="all, delete-orphan")  # Relationship to Embeddings

class Embeddings(Base):
    __tablename__ = 'embeddings'
    id = Column(Integer, primary_key=True)
    resource_id = Column(Integer, ForeignKey('resources.id'), nullable=False)
    chunk_order = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    embedding = Column(Vector, nullable=False)
    content = Column(Text, nullable=False)

    resource = relationship("Resource", back_populates="embeddings")  # Relationship back to Resource