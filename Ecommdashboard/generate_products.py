import pyodbc
import random

# SQL Server connection
conn = pyodbc.connect(
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=localhost\SQLEXPRESS;"
    r"DATABASE=EcomLiveDB;"
    r"Trusted_Connection=yes;"
)

cursor = conn.cursor()

print("Connected to SQL Server")

# Product categories
Products_data = {
    "Electronics": [
        ("Gaming Keyboard", "Logitech", 1999),
        ("Smart Watch", "Samsung", 7999),
        ("Bluetooth Speaker", "JBL", 2999),
        ("Laptop Stand", "Portronics", 899),
        ("Wireless Earbuds", "Boat", 2499)
    ],
    "Fashion": [
        ("Running Shoes", "Nike", 3499),
        ("Jeans", "Levis", 2499),
        ("Jacket", "Zara", 4999),
        ("Trousers", "H&M", 1999),
        ("Sneakers", "Adidas", 3999)
    ],
    "Beauty": [
        ("Face Cream", "Nivea", 499),
        ("Hair Dryer", "Philips", 1599),
        ("Perfume", "Skinn", 2999),
        ("Face Wash", "Himalaya", 299),
        ("Lip Balm", "Maybelline", 199)
    ],
    "Home Appliances": [
        ("Air Fryer", "Philips", 5499),
        ("Microwave Oven", "LG", 8999),
        ("Electric Kettle", "Prestige", 1499),
        ("Coffee Maker", "Philips", 3499),
        ("Vacuum Cleaner", "Dyson", 12999)
    ]
}

# find current max Product_Id
cursor.execute("SELECT MAX(Product_Id) FROM Products")
max_id = cursor.fetchone()[0]

if max_id is None:
    Product_id = 101
else:
    Product_id = max_id + 1

# Insert products
for Category in Products_data:
    for Product in Products_data[Category]:

        Product_Name = Product[0]
        Brand = Product[1]
        Price = Product[2]

        cursor.execute("""
            INSERT INTO Products
            (Product_Id, Product_name, Category, Brand, Unit_price)
            VALUES (?, ?, ?, ?, ?)
        """, Product_id, Product_Name, Category, Brand, Price)

        conn.commit()

        print(f"Inserted Product {Product_id} - {Product_Name}")

        Product_id += 1

print("Products inserted successfully.")