from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, Text,Date
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy.types import UserDefinedType

from sqlalchemy.exc import IntegrityError
import os

from dotenv import load_dotenv
import os

load_dotenv()


connection = (f"postgresql+psycopg://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}"
            f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")
# Initialize SQLAlchemy base and database connection
Base = declarative_base()
engine = create_engine(connection)
Session = sessionmaker(bind=engine)
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
class Embeddings(Base):
    __tablename__ = 'embeddings'

    id = Column(Integer, primary_key=True)
    resource_id = Column(Integer, ForeignKey('resources.id'), nullable=False)
    chunk_order = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    
    # Store embedding as a vector type (adjust dimensions based on embedding size)
    embedding = Column(Vector(1536), nullable=False)  # Adjust the dimension as needed (e.g., 1536 for OpenAI embeddings)
    
    content = Column(Text, nullable=False)
    resource = relationship("Resource", back_populates="embeddings")
# Create tables
Base.metadata.create_all(engine)

# Methods to populate tables

def populate_users(session):
    users = [
        User(user_name=f"User{i+1}", permissions="read_write") for i in range(5)
    ]
    session.add_all(users)
    session.commit()

def populate_categories(session):
    categories = [
        Category(category_name=f"Category{i+1}") for i in range(5)
    ]
    session.add_all(categories)
    session.commit()

def populate_sections(session):
    sections = [
        Section(section_name=f"Section{i+1}") for i in range(5)
    ]
    session.add_all(sections)
    session.commit()

def populate_subsections(session):
    subsections = [
        SubSection(section_id=section_id, section_name=f"SubSection{section_id}_{j+1}")
        for section_id in range(1, 6) for j in range(3)
    ]
    session.add_all(subsections)
    session.commit()

def populate_learning_types(session):
    learning_types = [
        LearningType(name_type=f"Type{i+1}") for i in range(3)
    ]
    session.add_all(learning_types)
    session.commit()

def add_resource(session, sub_section_id, learning_type_id, category_id, resource_name, path):
    resource = Resource(
        sub_section_id=sub_section_id,
        learning_type_id=learning_type_id,
        permissions_allowed="read",
        category_id=category_id,
        resource_name=resource_name,
        path=path,
    )
    session.add(resource)
    session.commit()

# Fill tables with initial data
session = Session()

try:
    # populate_users(session)
    # populate_categories(session)
    # populate_sections(session)
    # populate_subsections(session)
    # populate_learning_types(session)
    # print("Tables populated successfully.")

    # Example of adding a resource
    add_resource(
        session,
        sub_section_id=1,
        learning_type_id=1,
        category_id=1,
        resource_name="Sample Document",
        path="/chw_test.doc",
    )
    print("Sample resource added.")

except IntegrityError:
    session.rollback()
    print("Data already exists in one of the tables.")
finally:
    session.close()
