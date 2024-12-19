import pandas as pd
import sqlite3

def import_products_from_excel(excel_path, db_path="system.db"):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Read the Excel file into a DataFrame
    products_df = pd.read_excel(excel_path)
    for _, row in products_df.iterrows():
        # Insert product details into the database
        cursor.execute('''
            INSERT OR REPLACE INTO products (id, name, description, manufacturer, price, discount, stock, image)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row.get('ID', None),
            row.get('Name', ''),
            row.get('Description', ''),
            row.get('Manufacturer', ''),
            row.get('Price', 0.0),
            row.get('Discount', 0.0),
            row.get('Stock', 0),
            row.get('Image', '')
        ))

    # Commit and close the connection
    connection.commit()
    connection.close()
    print("Products imported successfully from Excel.")

# Provide the path to your Excel file
excel_file_path = "Товар_import_Канцелярия.xlsx"  # Adjust the path as needed
import_products_from_excel(excel_file_path)
