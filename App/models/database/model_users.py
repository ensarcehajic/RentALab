from sqlalchemy import create_engine,Column, Integer, String, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from adminUser import user,password,host,port
# Connect to the new database
engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/rentalab')
Base = declarative_base()

# Define the 'users' table
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(128))
    uloga = Column(String(20), nullable=False, unique=False)
    

# Check if the table exists and delete it if it does
try:
    inspector = inspect(engine)
    if 'users' in inspector.get_table_names():
        print("Table 'users' exists. Dropping it...")
        User.__table__.drop(engine)  # Drop the 'users' table
        print("Table 'users' dropped successfully.")
    else:
        print("Table 'users' dose not exist.")
        
except Exception as e:
    print("Error checking and dropping the table:", e)


try:
    # Create the table
    Base.metadata.create_all(engine)
    print("Table 'users' created in 'rentalab' database.")

except Exception as e:
    print("Error creating the table:", e)

try:   
    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Define your data (example)
    new_user = User(
        email="example@example.com",
        password_hash="hashed_password",
        uloga="tester"
    )
    
    # Add the new user to the session
    session.add(new_user)
    
    # Commit the transaction (this saves the data into the database)
    session.commit()
    session.close()
    print("Data inserted successfully!")
except Exception as e:
    print("Error inserting data in to table:", e)

