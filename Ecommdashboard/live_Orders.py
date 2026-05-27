import pyodbc
import random
import time
from datetime import datetime, timedelta



# SQL Server connection
conn = pyodbc.connect(
    r"DRIVER={SQL Server};"
    r"SERVER=localhost\SQLEXPRESS;"
    r"DATABASE=EcomLiveDB;"
    r"Trusted_Connection=yes;"
)
cursor = conn.cursor()

Customers = [1, 2, 3, 4, 5]

Products = {
    101: 799,
    102: 2499,
    103: 599,
    104: 3499,
    105: 299
}

Payment_Statuses = ["Completed", "Pending", "Cancelled"]

while True:
    Customer_id = random.choice(Customers)
    Product_id = random.choice(list(Products.keys()))
    Quantity = random.randint(1, 3)
    Unit_Price = Products[Product_id]
    Total_price = Unit_Price * Quantity
    Payment_Status = random.choices(
        Payment_Statuses,
        weights=[70, 20, 10],
        k=1
    )[0]
    days_ago = random.randint(0, 30)
    hours_ago = random.randint(0, 23)
    minutes_ago = random.randint(0, 59)

    Order_Time = datetime.now() - timedelta(
        days=days_ago,
        hours=hours_ago,
        minutes=minutes_ago
    )


    cursor.execute("""
        INSERT INTO Orders (Customer_id, Product_id, Quantity, Price, Payment_Status, Order_Time)
        VALUES (?, ?, ?, ?, ?, ?)
    """, Customer_id, Product_id,Quantity,Total_price,Payment_Status,Order_Time)

    conn.commit()

    print(f"Inserted order: customer={Customer_id}, product={Product_id}, qty={Quantity}, Price={Total_price}, status={Payment_Status}, time={Order_Time}")

    time.sleep(5)