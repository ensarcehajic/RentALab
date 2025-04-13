from sqlalchemy import create_engine, text
from adminUser import user,password,host,port

# Connect to the default 'postgres' database (used to issue CREATE DATABASE)
engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/postgres')

try:
    # Create a single connection for both checking and dropping the database
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")

        # Check if the 'rentalab' database exists
        result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = 'rentalab'"))
        if result.fetchone():  # If the database exists
            print("Database 'rentalab' exists. Dropping it...")

            # Forcefully terminate all active connections to the 'rentalab' database
            conn.execute(text("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'rentalab' AND pid <> pg_backend_pid()"))
            
            # Drop the database
            conn.execute(text("DROP DATABASE rentalab"))
            print("Database 'rentalab' dropped successfully.")
        else:
            print("Database 'rentalab' does not exist.")

        # Creating the 'rentalab' database (it will be created after dropping it)
        conn.execute(text("CREATE DATABASE rentalab"))
        print("Database 'rentalab' created successfully!")

except Exception as e:
    print("Error during database operation:", e)
