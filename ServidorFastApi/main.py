from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware

# Configuración de la base de datos
db_config = {
    'user' : '2tutmTfhp6UrCbM.root',
    'password': 'fmT13UDy7122rMGf',
    'host' : 'gateway01.us-east-1.prod.aws.tidbcloud.com',
    'port': 4000,
    'database' : 'test'
}

# Modelo de datos para el login
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str

# Modelo de datos para actualización
class UpdateRequest(BaseModel):
    current_email: str
    new_email: str
    new_password: str

# Inicializar FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las direcciones IP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Función para obtener la conexión a la base de datos
def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection

# Ruta para el login
@app.post("/login")
def login(login_request: LoginRequest):

    # Obtener la conexión a la base de datos
    connection = get_db_connection()

    # Crear un cursor para ejecutar consultas
    cursor = connection.cursor(dictionary=True)

    # Ejecutar la consulta para verificar las credenciales
    query = "SELECT * FROM login WHERE email = %s AND password = %s"
    cursor.execute(query, (login_request.email, login_request.password))
    user = cursor.fetchone()

    # Cerrar la conexión a la base de datos
    cursor.close()
    connection.close()

    # Verificar si se encontró un usuario con las credenciales proporcionadas
    if user:
        return {"message": "Login exitoso", "user": user}
    else:
        return {"message": "Credenciales inválidas"}

# Ruta para el registro
@app.post("/register")
def register(register_request: RegisterRequest):
    print(f"Register attempt with email: {register_request.email}")
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Verificar si el email ya existe
    check_query = "SELECT * FROM login WHERE email = %s"
    cursor.execute(check_query, (register_request.email,))
    existing_user = cursor.fetchone()

    if existing_user:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=400, detail="Email already registered")

    # Insertar nuevo usuario
    insert_query = "INSERT INTO login (email, password) VALUES (%s, %s)"
    cursor.execute(insert_query, (register_request.email, register_request.password))
    connection.commit()

    # Obtener el usuario recién creado
    cursor.execute(check_query, (register_request.email,))
    new_user = cursor.fetchone()

    cursor.close()
    connection.close()

    if new_user:
        return {"message": "Registration successful", "user": new_user}
    else:
        raise HTTPException(status_code=500, detail="Registration failed")

# Añade esta ruta para eliminar usuario
@app.delete("/delete_user/{email}")
def delete_user(email: str):
    print(f"Delete attempt for email: {email}")
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Verificar si el email existe
    check_query = "SELECT * FROM login WHERE email = %s"
    cursor.execute(check_query, (email,))
    existing_user = cursor.fetchone()

    if not existing_user:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=404, detail="User not found")

    # Eliminar usuario
    delete_query = "DELETE FROM login WHERE email = %s"
    cursor.execute(delete_query, (email,))
    connection.commit()

    affected_rows = cursor.rowcount

    cursor.close()
    connection.close()

    if affected_rows > 0:
        return {"message": f"User {email} deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Delete operation failed")


# Añade esta ruta para obtener todos los usuarios
@app.get("/users")
def get_all_users():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = "SELECT * FROM login"
        cursor.execute(query)
        users = cursor.fetchall()

        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        connection.close()

# Ruta para actualizar usuarios
@app.put("/update_user")
def update_user(update_request: UpdateRequest):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Verificar si el usuario actual existe
        check_query = "SELECT * FROM login WHERE email = %s"
        cursor.execute(check_query, (update_request.current_email,))
        existing_user = cursor.fetchone()

        if not existing_user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Verificar si el nuevo email ya está en uso
        if update_request.current_email != update_request.new_email:
            cursor.execute(check_query, (update_request.new_email,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="El nuevo email ya está en uso")

        # Actualizar usuario
        update_query = "UPDATE login SET email = %s, password = %s WHERE email = %s"
        cursor.execute(update_query, (
            update_request.new_email,
            update_request.new_password,
            update_request.current_email
        ))
        connection.commit()

        return {"message": "Usuario actualizado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar: {str(e)}")
    finally:
        cursor.close()
        connection.close()

# Ruta de prueba
@app.get("/")
def read_root():
    return {"Hola", "Profe"}
    
# Ejecutar la aplicación FastAPI
if __name__ == "_main_":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)  #mediante la ip de nuestra maquina