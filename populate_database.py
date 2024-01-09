import random

import psycopg2
from faker import Faker

# Configuration for your database
db_config = {
    "dbname": "kugaconstruct",
    "user": "postgres",
    "password": "postgres",
    "host": "127.0.0.1",
}


# Establish a connection to the database
conn = psycopg2.connect(**db_config)
cur = conn.cursor()

# Initialize Faker
fake = Faker()

# Number of records to insert for each table
num_records = 10

# Insert fake data into Suppliers
for _ in range(num_records):
    cur.execute(
        "INSERT INTO Suppliers (name, contact_name, contact_info, address, material_type) VALUES (%s, %s, %s, %s, %s)",
        (fake.company(), fake.name(), fake.email(), fake.address(), fake.word()),
    )

# Insert fake data into Clients
for _ in range(num_records):
    cur.execute(
        "INSERT INTO Clients (company_name, contact_name, contact_info) VALUES (%s, %s, %s)",
        (fake.company(), fake.name(), fake.email()),
    )

# Insert fake data into Employees
for _ in range(num_records):
    cur.execute(
        "INSERT INTO Employees (first_name, last_name, position, contact_info) VALUES (%s, %s, %s, %s)",
        (fake.first_name(), fake.last_name(), fake.job(), fake.email()),
    )

# Insert fake data into Projects
for i in range(1, num_records + 1):
    cur.execute(
        "INSERT INTO Projects (project_name, start_date, end_date, budget, client_id) VALUES (%s, %s, %s, %s, %s)",
        (
            fake.bs(),
            fake.date(),
            fake.date(),
            round(random.uniform(10000, 50000), 2),
            i,
        ),
    )

# Insert fake data into Materials
for i in range(1, num_records + 1):
    cur.execute(
        "INSERT INTO Materials (material_name, supplier_id, price) VALUES (%s, %s, %s)",
        (fake.word(), i, round(random.uniform(10, 500), 2)),
    )

# Insert fake data into Equipment
for _ in range(num_records):
    cur.execute(
        "INSERT INTO Equipment (equipment_name, status, maintenance_schedule) VALUES (%s, %s, %s)",
        (fake.word(), random.choice(["good", "repair", "maintenance"]), fake.date()),
    )

# Insert fake data into Project_Employees
for i in range(1, num_records + 1):
    for j in range(
        1, random.randint(2, num_records)
    ):  # Randomly assign 1 to num_records-1 employees to each project
        cur.execute(
            "INSERT INTO Project_Employees (project_id, employee_id) VALUES (%s, %s)",
            (i, j),
        )

# Insert fake data into Project_Materials
for i in range(1, num_records + 1):
    for j in range(
        1, random.randint(1, num_records)
    ):  # Randomly assign 1 to num_records materials to each project
        cur.execute(
            "INSERT INTO Project_Materials (project_id, material_id, quantity) VALUES (%s, %s, %s)",
            (i, j, random.randint(1, 20)),
        )

# Commit the transaction
conn.commit()

# Close the connection
cur.close()
conn.close()

print("Fake data inserted successfully!")
