import requests
from requests.auth import HTTPBasicAuth
import base64

BASE = "http://127.0.0.1:5000"
auth_header = None  # Guarda la autorización luego del login
current_user = None  # Guarda el usuario logueado


def registrar():
    usuario = input("Ingrese nuevo usuario: ")
    contraseña = input("Ingrese contraseña: ")

    res = requests.post(BASE + "/registro", json={
        "usuario": usuario,
        "contraseña": contraseña
    })

    try:
        data = res.json()
        print("Respuesta del servidor:", data.get("message") or data.get("error"))
    except:
        print("Error al procesar la respuesta")


def login():
    global auth_header, current_user
    usuario = input("Usuario: ")
    contraseña = input("Contraseña: ")

    res = requests.post(BASE + "/login", json={
        "usuario": usuario,
        "contraseña": contraseña
    })

    try:
        data = res.json()
        print("Respuesta del servidor:", data.get("message") or data.get("error"))
        if res.ok:
            auth_header = "Basic " + base64.b64encode(f"{usuario}:{contraseña}".encode()).decode()
            current_user = usuario
    except:
        print("Error al procesar la respuesta")


def listar_tareas():
    if not auth_header:
        print("Primero iniciá sesión")
        return

    res = requests.get(BASE + "/tareas", headers={"Authorization": auth_header})
    try:
        tareas = res.json()
        if isinstance(tareas, list):
            if not tareas:
                print(f"No hay tareas aún para {current_user}.")
            else:
                print(f"\n<h1>Bienvenido {current_user} a sus tareas</h1>\n")
                print("--- Tareas ---")
                for t in tareas:
                    print(f"ID: {t['id']} | Título: {t['titulo']} | Descripción: {t['descripcion']}")
        else:
            print("Error:", tareas.get("error"))
    except:
        print("Error al procesar la respuesta")


def crear_tarea():
    if not auth_header:
        print("Primero iniciá sesión")
        return

    titulo = input("Título de la tarea: ")
    descripcion = input("Descripción: ")

    if not titulo:
        print("El título es obligatorio")
        return

    res = requests.post(BASE + "/tareas", headers={"Authorization": auth_header}, json={
        "titulo": titulo,
        "descripcion": descripcion
    })

    try:
        data = res.json()
        print("Respuesta del servidor:", data.get("message") or data.get("error"))
    except:
        print("Error al procesar la respuesta")


def editar_tarea():
    if not auth_header:
        print("Primero iniciá sesión")
        return

    id_tarea = input("ID de la tarea a editar: ")
    nuevo_titulo = input("Nuevo título: ")
    nueva_descripcion = input("Nueva descripción: ")

    res = requests.put(BASE + f"/tareas/{id_tarea}", headers={"Authorization": auth_header}, json={
        "titulo": nuevo_titulo,
        "descripcion": nueva_descripcion
    })

    try:
        data = res.json()
        print("Respuesta del servidor:", data.get("message") or data.get("error"))
    except:
        print("Error al procesar la respuesta")


def eliminar_tarea():
    if not auth_header:
        print("Primero iniciá sesión")
        return

    id_tarea = input("ID de la tarea a eliminar: ")

    res = requests.delete(BASE + f"/tareas/{id_tarea}", headers={"Authorization": auth_header})

    try:
        data = res.json()
        print("Respuesta del servidor:", data.get("message") or data.get("error"))
    except:
        print("Error al procesar la respuesta")


def menu():
    while True:
        print("\n=== Sistema de Gestión de Tareas ===")
        print("1. Registrar usuario")
        print("2. Login")
        print("3. Listar tareas")
        print("4. Crear tarea")
        print("5. Editar tarea")
        print("6. Eliminar tarea")
        print("7. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            registrar()
        elif opcion == "2":
            login()
        elif opcion == "3":
            listar_tareas()
        elif opcion == "4":
            crear_tarea()
        elif opcion == "5":
            editar_tarea()
        elif opcion == "6":
            eliminar_tarea()
        elif opcion == "7":
            print("Saliendo...")
            break
        else:
            print("Opción inválida")


if __name__ == "__main__":
    menu()
