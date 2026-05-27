import pyodbc
import random
from datetime import datetime, timedelta

# SQL Server connection
conn = pyodbc.connect(
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=localhost\SQLEXPRESS;"
    r"DATABASE=EcomLiveDB;"
    r"Trusted_Connection=yes;"
)
cursor = conn.cursor()

print("Connected to SQL Server")

# Sample data
first_names = [
    "Ankit","Payal","Raj","Sejal","Rishi","Anisha",
    "Kabir","Nisha","Ajay","Priya","Vikram","Meira",
    "Ritu","Sunny","Vishal","Ishita","Nehal","Dipak"
]

last_names = [
    "Darji","sharma","Verma","Mehta","Singh","Khatri",
    "Roy","Kapoor","Malhotra","Gupta"
]

Cities = [
    "Mumbai","Delhi","Surat","Ahmedabad",
    "Pune","Bangalore","Hyderabad","Chennai"
]

Segments = ["Regular","Premium","Gold"]

# Start from next customer id
cursor.execute("SELECT MAX(Customer_Id) FROM Customers")
max_id = cursor.fetchone()[0]

if max_id is None:
    Customer_Id = 1
else:
    Customer_Id = max_id + 1

# Generate 50 customers
for i in range(50):

    Name = random.choice(first_names) + " " + random.choice(last_names)
    Segment = random.choice(Segments)
    City = random.choice(Cities)

    # random signup date within last 180 days
    days_ago = random.randint(1,180)
    Signup_Date = datetime.now() - timedelta(days=days_ago)

    cursor.execute("""
        INSERT INTO Customers
        (Customer_Id, Customer_name, Segment, City, Signup_Date)
        VALUES (?, ?, ?, ?, ?)
    """, Customer_Id,Name,Segment,City, Signup_Date)

    conn.commit()

    print(f"Inserted Customer {Customer_Id} - {Name}")

    Customer_Id += 1

print("Customers inserted successfully.")