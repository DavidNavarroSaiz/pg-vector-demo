# main.py
from db.crud import DatabaseManager

# Initialize the database manager
db_manager = DatabaseManager()

try:
    # Populate tables
    db_manager.populate_users()
    db_manager.populate_categories()
    db_manager.populate_sections()
    db_manager.populate_subsections()
    db_manager.populate_learning_types()

    # Perform CRUD operations
    # db_manager.update_resource(resource_id=1, resource_name="Updated Resource")
    # db_manager.update_chunk(chunk_id=1, content="Updated content for chunk.")
    # db_manager.delete_resource(resource_id=1)

finally:
    # Close the session
    db_manager.close()
