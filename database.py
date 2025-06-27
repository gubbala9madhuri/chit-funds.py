import sqlite3

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('chit_funds.db')
cursor = conn.cursor()

# Create the 'members' table if it doesn't already exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    contribution REAL DEFAULT 0,
    loan_received REAL DEFAULT 0
);
''')

# Create the 'bids' table for managing bids
cursor.execute('''
CREATE TABLE IF NOT EXISTS bids (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER,
    bid_amount REAL,
    winner BOOLEAN,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members (id)
);
''')

# Create the 'penalties' table for managing late payment penalties
cursor.execute('''
CREATE TABLE IF NOT EXISTS penalties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER,
    penalty_amount REAL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members (id)
);
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Tables created successfully!")