from cryptography.fernet import Fernet
import json
import os


def genera_clave():
    clave = Fernet.generate_key()
    path = os.path.abspath("../assets/pass.key")
    with open(path, "wb") as password:
        password.write(clave)

def cargar_clave():
    path = os.path.abspath("../assets/pass.key")
    return open(path, "rb").read()

def cifrar_contra(contra):
    json_path = os.path.abspath("../config.json")

    genera_clave()
    clave = cargar_clave()

    password = contra.encode()
    f = Fernet(clave)
    pass_encrypted = f.encrypt(password)

    a_file = open(json_path, "r")
    json_object = json.load(a_file)
    a_file.close()

    json_object["user"]["password"] = pass_encrypted.decode("utf-8")

    a_file = open(json_path, "w")
    json.dump(json_object, a_file)
    a_file.close()

def descifar_contra(clave):
    json_path = os.path.abspath("../config.json")

    f = Fernet(clave)

    a_file = open(json_path, "r")
    json_oject = json.load(a_file)
    a_file.close()

    contra = json_oject['user']['password'].encode()
    contra = f.decrypt(contra)
    contra = contra.decode('utf-8')

    return contra

print(descifar_contra(cargar_clave()))