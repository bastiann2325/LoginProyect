import mysql.connector
import os

db_config = {
    'user': '2tutmTfhp6UrCbM.root',
    'password' : 'fmT13UDy7122rMGf', 
    'host': 'gateway01.us-east-1.prod.aws.tidbcloud.com',
    'port': 4000,
    'database': 'test'
}

connection = None  

try:
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)


    cursor.execute("SELECT 1")
    result = cursor.fetchone()

    print("Conexión exitosa a la base de datos. Resultado de la consulta:", result)

except mysql.connector.Error as err:
    print("Error al conectarse a la base de datos:", err)

finally:
    if connection and connection.is_connected():
        cursor.close()
        connection.close()
    
    print("Conexión cerrada.") 