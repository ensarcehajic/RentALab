from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from adminUser import user,password,host,port

# Connect to the 'rentalab' database
engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/rentalab')

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Run a simple query to fetch all rows from the 'users' table
    result = session.execute(text("SELECT * FROM users"))

    # Fetch and print all results
    rows = result.fetchall()
    if rows:
        print("Data from 'users' table:")
        for row in rows:
            print(row)
    else:
        print("No data found in 'users' table.")
except Exception as e:
    print("Error running query:", e)
finally:
    session.close()