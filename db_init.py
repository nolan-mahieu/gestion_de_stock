import mysql.connector
from mysql.connector import errorcode
from db_config import db_config

def create_database(cursor, db_name):
    try:
        cursor.execute(f"CREATE DATABASE {db_name}")
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
        exit(1)

def create_tables(cursor):
    tables = {}

    tables['categorie'] = (
        "CREATE TABLE categorie ("
        "  id INT AUTO_INCREMENT PRIMARY KEY,"
        "  nom VARCHAR(255) NOT NULL"
        ") ENGINE=InnoDB")

    tables['produit'] = (
        "CREATE TABLE produit ("
        "  id INT AUTO_INCREMENT PRIMARY KEY,"
        "  nom VARCHAR(255) NOT NULL,"
        "  description TEXT,"
        "  prix INT NOT NULL,"
        "  quantite INT NOT NULL,"
        "  id_categorie INT,"
        "  FOREIGN KEY (id_categorie) REFERENCES categorie (id)"
        ") ENGINE=InnoDB")

    for table_name in tables:
        table_description = tables[table_name]
        try:
            cursor.execute(table_description)
            print(f"Table {table_name} created successfully.")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print(f"Table {table_name} already exists.")
            else:
                print(err.msg)

def main():
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()

        # Create database if not exists
        try:
            cursor.execute(f"USE {db_config['database']}")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                create_database(cursor, db_config['database'])
                cnx.database = db_config['database']
            else:
                print(err)
                exit(1)

        # Create tables
        create_tables(cursor)

    except mysql.connector.Error as err:
        print(err)
    finally:
        cursor.close()
        cnx.close()

if __name__ == "__main__":
    main()
