from faker import Faker
import sqlite3
import random

fake = Faker()
conn = sqlite3.connect("tax_data.db")
cursor = conn.cursor()


cursor.executescript("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    ssn TEXT UNIQUE,
    address TEXT
);

CREATE TABLE IF NOT EXISTS tax_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    year INTEGER,
    income REAL,
    deductions REAL,
    tax_paid REAL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
""")

for _ in range(10):
    name = fake.name()
    email = fake.email()
    ssn = fake.ssn()
    address = fake.address()
    cursor.execute("INSERT INTO users (name, email, ssn, address) VALUES (?, ?, ?, ?)",
                   (name, email, ssn, address))
    user_id = cursor.lastrowid
    for year in range(2020, 2023):
        income = round(random.uniform(30000, 100000), 2)
        deductions = round(random.uniform(5000, 20000), 2)
        tax_paid = income * 0.2 - deductions  
        cursor.execute("INSERT INTO tax_records (user_id, year, income, deductions, tax_paid) VALUES (?, ?, ?, ?, ?)",
                       (user_id, year, income, deductions, tax_paid))

conn.commit()
conn.close()
print("Database populated with mock data.")
