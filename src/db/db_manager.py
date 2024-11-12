# db/crud.py

from src.db.models import User, Category, Section, SubSection, LearningType, Resource, Embeddings,Base
from src.db.config import engine,Session as SessionFactory  
from sqlalchemy import MetaData,inspect,text
from datetime import date


class DatabaseManager:
    def __init__(self):
        self.session = SessionFactory()
        self.create_missing_tables()

    def close(self):
        """Close the session."""
        self.session.close()
    def create_missing_tables(self):
        """Create tables only if they are missing in the database."""
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        # Reflect metadata to check existing tables
        metadata = MetaData()
        metadata.reflect(bind=engine)

        # Check for missing tables and create them
        missing_tables = [table for table in Base.metadata.tables.keys() if table not in existing_tables]
        if missing_tables:
            Base.metadata.create_all(engine, tables=[Base.metadata.tables[table] for table in missing_tables])
            print(f"Created missing tables: {missing_tables}")
        else:
            # print("All tables already exist.")
            pass
    # Population Methods

    def populate_users(self):
        """Populate users with realistic names and varied permissions."""
        users = [
            User(user_name="David", permissions="free"),
            User(user_name="Carlos", permissions="paid"),
            User(user_name="Andres", permissions="agency"),
            User(user_name="Laura", permissions="free"),
            User(user_name="Sara", permissions="paid")
        ]
        self.session.add_all(users)
        self.session.commit()
        print("Users populated with varied permissions.")

    def populate_categories(self):
        """Populate categories with more descriptive names."""
        categories = [
            Category(category_name="Reflection"),
            Category(category_name="Activity Sheet"),
            Category(category_name="Slideshow"),
            Category(category_name="Interactive Map")
        ]
        self.session.add_all(categories)
        self.session.commit()
        print("Categories populated.")

    def populate_sections(self):
        """Populate sections with realistic names."""
        sections = [
            Section(section_name="CHW"),
            Section(section_name="Education"),
            Section(section_name="Supervisors"),
            Section(section_name="Healthcare")
        ]
        self.session.add_all(sections)
        self.session.commit()
        print("Sections populated.")

    def populate_subsections(self):
        """Populate subsections with realistic names."""
        subsections = [
            SubSection(section_id=1, section_name="Popular Education"),
            SubSection(section_id=2, section_name="Professional Skills Development"),
            SubSection(section_id=1, section_name="Interpersonal Awareness"),
            SubSection(section_id=3, section_name="Roles and Competences"),
            SubSection(section_id=4, section_name="Introduction to CHWs")
        ]
        self.session.add_all(subsections)
        self.session.commit()
        print("Subsections populated.")

    def populate_learning_types(self):
        """Populate learning types with more descriptive names."""
        learning_types = [
            LearningType(name_type="Analizador"),
            LearningType(name_type="Visual"),
            LearningType(name_type="Auditory"),
            LearningType(name_type="Logical"),
            LearningType(name_type="Reading"),
            LearningType(name_type="Writing")
        ]
        self.session.add_all(learning_types)
        self.session.commit()
        print("Learning types populated.")
        
    def drop_all_tables(self):
        """Drops all tables in the database. Use with caution, as this removes all data and structure."""
        metadata = MetaData()
        metadata.reflect(bind=engine)
        metadata.drop_all(bind=engine)
        print("All tables dropped.")

    def delete_all_records(self):
        """Deletes all records from each table without dropping the table structure."""
        self.session.query(Embeddings).delete()
        self.session.query(Resource).delete()
        self.session.query(SubSection).delete()
        self.session.query(Section).delete()
        self.session.query(LearningType).delete()
        self.session.query(Category).delete()
        self.session.query(User).delete()
        self.session.commit()
        print("All records deleted from all tables.")
        
    def delete_resources_embeddings(self):
        """Deletes all records from Embedding and Resources table deleted without dropping the table structure."""
        self.session.query(Embeddings).delete()
        self.session.query(Resource).delete()
        self.session.commit()
        print("All records from Embedding and Resources deleted")
        
        
    # CRUD Operations

    def delete_resource(self, resource_id: int):
        """Deletes a resource and its associated embeddings (chunks)."""
        resource = self.session.query(Resource).filter_by(id=resource_id).first()
        if resource:
            self.session.delete(resource)
            self.session.commit()
            print(f"Resource {resource_id} and associated chunks deleted.")
        else:
            print(f"Resource {resource_id} not found.")

    def update_resource(self, resource_id: int, **kwargs):
        """Updates a resource's details with provided keyword arguments."""
        resource = self.session.query(Resource).filter_by(id=resource_id).first()
        if resource:
            for key, value in kwargs.items():
                setattr(resource, key, value)
            self.session.commit()
            print(f"Resource {resource_id} updated with {kwargs}.")
        else:
            print(f"Resource {resource_id} not found.")

    def update_chunk(self, chunk_id: int, **kwargs):
        """Updates a chunk's details with provided keyword arguments."""
        chunk = self.session.query(Embeddings).filter_by(id=chunk_id).first()
        if chunk:
            for key, value in kwargs.items():
                setattr(chunk, key, value)
            self.session.commit()
            print(f"Chunk {chunk_id} updated with {kwargs}.")
        else:
            print(f"Chunk {chunk_id} not found.")
    def add_resource(self, sub_section_id, learning_type_id, category_id, resource_name, path, permissions_allowed="free"):
        """Add a new resource to the database."""
        resource = Resource(
            sub_section_id=sub_section_id,
            learning_type_id=learning_type_id,
            permissions_allowed=permissions_allowed,
            category_id=category_id,
            resource_name=resource_name,
            path=path
        )
        self.session.add(resource)
        self.session.commit()
        print(f"Resource '{resource_name}' added with ID {resource.id}.")
        return resource.id  # Return the ID of the newly created resource

    def add_chunk(self, resource_id, chunk_order, embedding, content,summary,cmetadata):
        """Add a new chunk (embedding) associated with a specific resource."""
        chunk = Embeddings(
            resource_id=resource_id,
            chunk_order=chunk_order,
            date=date.today(),
            embedding=embedding,
            content=content,
            summary=summary,
            cmetadata= cmetadata
        )
        self.session.add(chunk)
        self.session.commit()
        print(f"Chunk {chunk_order} added to resource ID {resource_id}.")
    def get_all_resource_paths(self):
        """Retrieve all unique document paths in the resources table."""
        paths = self.session.query(Resource.path).distinct().all()
        return [path[0] for path in paths]
    
    def get_sections(self):
        """Get a dictionary of section names and IDs."""
        return {section.section_name: section.section_id for section in self.session.query(Section).all()}

    def get_subsections(self):
        """Get a dictionary of subsection names and IDs."""
        return {subsection.section_name: subsection.subsection_id for subsection in self.session.query(SubSection).all()}

    def get_categories(self):
        """Get a dictionary of category names and IDs."""
        return {category.category_name: category.category_id for category in self.session.query(Category).all()}

    def get_learning_types(self):
        """Get a dictionary of learning type names and IDs."""
        return {learning_type.name_type: learning_type.learning_type_id for learning_type in self.session.query(LearningType).all()}

    def get_permissions(self):
        """Return a list of permission options."""
        return ["free", "paid", "agency"]
    
        
    def search_documents(self, query_embedding, limit=5, resource_id=None, permissions_allowed=None, category_id=None, sub_section_id=None, learning_type_id=None):
        # Convert the query to an embedding and format it as an array for PostgreSQL
        query_embedding_cast = f"ARRAY{query_embedding}::vector"  # Casting directly as vector array
        
        # Start building the SQL query with the required parts
        sql_query = f"""
            SELECT 
                embeddings.content,
                resources.resource_name,
                embeddings.embedding <-> {query_embedding_cast} AS distance
            FROM embeddings
            JOIN resources ON embeddings.resource_id = resources.id
        """
        
        # Add filters dynamically
        filters = []
        params = {"limit": limit}
        
        if resource_id is not None:
            filters.append("resources.id = :resource_id")
            params["resource_id"] = resource_id
        
        if permissions_allowed is not None:
            filters.append("resources.permissions_allowed = :permissions_allowed")
            params["permissions_allowed"] = permissions_allowed
        
        if category_id is not None:
            filters.append("resources.category_id = :category_id")
            params["category_id"] = category_id
        
        if sub_section_id is not None:
            filters.append("resources.sub_section_id = :sub_section_id")
            params["sub_section_id"] = sub_section_id
        
        if learning_type_id is not None:
            filters.append("resources.learning_type_id = :learning_type_id")
            params["learning_type_id"] = learning_type_id
        
        # Join all filters with AND and add them to the SQL query
        if filters:
            sql_query += " WHERE " + " AND ".join(filters)
        
        # Order by distance and apply the limit
        sql_query += " ORDER BY distance LIMIT :limit"
        
        # Execute the SQL query
        results = self.session.execute(text(sql_query), params).fetchall()
        
        # Format the results into a list of dictionaries
        formatted_results = [
            {
                "content": row[0],
                "resource_name": row[1],
                "distance": row[2]
            }
            for row in results
        ]
        return formatted_results
if __name__ == "__main__":
    db_manager = DatabaseManager()
    # db_manager.drop_all_tables()
    db_manager.delete_resources_embeddings()
    # db_manager.populate_users()
    # db_manager.populate_categories()
    # db_manager.populate_sections()
    # db_manager.populate_subsections()
    # db_manager.populate_learning_types()


 