import plyer.platforms.win.notification
from plyer import notification
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep
from datetime import datetime, timedelta
from threading import Thread
import sys, os
import balloontip

EXECUTABLE_PATH = 'C:\\Users\\peluc\\Downloads\\chromedriver.exe'

USERNAME = 'o.meza18'
PASSWORD = 'Solicitud.G55'

MATERIAS = {
    'url' : [
        'https://aula2.uas.edu.mx/centro/info/mod/attendance/view.php?id=15673&view=1', # Redacción de Textos en Ingles
        'https://aula2.uas.edu.mx/centro/info/mod/attendance/view.php?id=15632&view=1', # Programación de servidores web
        'https://aula2.uas.edu.mx/centro/info/mod/attendance/view.php?id=15809&view=1', # Seminarios de creatividad
        'https://aula2.uas.edu.mx/centro/info/mod/attendance/view.php?id=19387&view=1', # Administración de redes
        'https://aula2.uas.edu.mx/centro/info/mod/attendance/view.php?id=15850&view=1'  # Sistemas de información
    ],
    'id_status': [
        'id_status_1747',
        'id_status_1743',
        'id_status_1759',
        'id_status_1739', # ¡¡¡ CAMBIAR STATUS !!!
        'id_status_1763'
    ],
    'hora':[
        datetime.strptime('15:20:00', '%H:%M:%S'),
        datetime.strptime('16:20:00', '%H:%M:%S'),
        datetime.strptime('17:20:00', '%H:%M:%S'),
        datetime.strptime('18:20:00', '%H:%M:%S'),
        datetime.strptime('19:20:00', '%H:%M:%S')
    ],
    'asistencia' : [
        False,
        False,
        False,
        False,
        False
    ]
}

HOMEPAGEURL = 'https://aula2.uas.edu.mx/centro/info/login/index.php'
LOGOUTURL = 'https://aula2.uas.edu.mx/centro/info/login/logout.php?sesskey=XVfjJDDaSW'

chrome_options = webdriver.ChromeOptions()
chrome_options.headless = True

# Este será el index del array MATERIAS
materiaActual = 999

# Este será el nuevo hilo
t = False

def asignar_hora():
    global materiaActual
    claseActualIndex = 999

    # Obtener la materia actual
    for i in MATERIAS['hora']:   
        # Evaluar si se ha asignado alguna hora / materia
        if datetime.now().hour == i.hour:
            claseActualIndex = MATERIAS['hora'].index(i)

    if claseActualIndex == 999:
        materiaActual = 999
    else:
        materiaActual = claseActualIndex

class Temporizador(Thread):
    def __init__(self, hora, delay, funcion):

        super(Temporizador, self).__init__()
        self._estado = True
        self.hora = hora
        self.delay = delay
        self.funcion = funcion

    def stop(self):
        self._estado = False

    def run(self):
        # Definición de constantes y variables
        ultimaClase = MATERIAS['hora'][len(MATERIAS['hora']) - 1]

        aux = datetime.strptime(self.hora, '%H:%M:%S')
        hora = datetime.now()
        hora = hora.replace(hour = aux.hour, minute=aux.minute, second=aux.second, microsecond = 0)

        print('Ejecución automática iniciada', flush=True)
        print('Proxima ejecución programada el {0} a las {1}'.format(hora.date(),  hora.time()), flush=True)

        while self._estado:
            if hora <= datetime.now():
                asignar_hora()
                self.funcion()
                print('Ejecución programada ejecutada el {0} a las {1}'.format(hora.date(),  hora.time()), flush=True)

                if datetime.now().time() == ultimaClase.time(): # Si ya es la ultima hora (No hay mas clases)
                    self.stop()
                else:
                    hora += timedelta(hours=1)
                    print('Próxima ejecución programada el {0} a las {1}'.format(hora.date(),  hora.time()), flush=True)

            sleep(self.delay)
        else:
            print('Ejecución automática finalizada', flush=True)
            asistencias = 0
            if datetime.now().time() == ultimaClase.time():
                # Obtener el numero de asistencias
                for i in MATERIAS['asistencia']:   
                    if i:
                        asistencias = asistencias + 1

                print('Asistencias tomadas: {} / {}'.format(asistencias, len(MATERIAS['asistencia'])), flush=True)
                os._exit(1)
  
def corregir_ruta(path):
    if getattr(sys, "frozen", False):
        resolved_path = os.path.abspath(os.path.join(sys._MEIPASS, path))
    else:
        resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))

    return resolved_path

def verificar_horario():
    global materiaActual
    primeraHora = MATERIAS['hora'][0]

    # Asignar hora de clase
    asignar_hora()

    # Evaluar si se asigno horario de clase
    if materiaActual != 999:
         # Configurar la hora con la fecha de hoy
        aux = MATERIAS['hora'][materiaActual]
        claseActual = datetime.now()
        claseActual = claseActual.replace(hour = aux.hour, minute=aux.minute, second=aux.second, microsecond = 0)

        claseSig = claseActual
        claseSig += timedelta(hours=1)
        claseSig -= timedelta(minutes=20)

        # Evaluar si es posible tomar asistencia
        if datetime.now() > claseActual: # Si el [delay] ya ha pasado
            return True
        else:
            print("###  Aún no es posible tomar la asistencia  ###", flush=True)
            return False

    else:
        print("###  Fuera de horario de clase  ###", flush=True)
        return False

def verificar_existencia(driver, selector):
    try:
        driver.find_element_by_css_selector(selector)
    except NoSuchElementException:
        return False
    return True

def iniciar_sesion(driver):
    # Redireccionar a la página principal de Aula Virtual
    driver.get(HOMEPAGEURL)

    # Introducir los datos del usuario
    inputUsername = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    inputUsername.send_keys(USERNAME)

    inputPass = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.NAME, "password"))
    )
    inputPass.send_keys(PASSWORD)

    loginButton = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "loginbtn"))
    )

    # Desencadenar un clic en iniciar sesión
    loginButton.click()
    sleep(1)

    print("#####     SESIÓN INICIADA     #####", flush=True)

def cerrar_Sesion(driver):
    # Redirección al log out
    driver.get(LOGOUTURL)

    # Desencadenar click en el botón Cerrar
    driver.find_element_by_css_selector('button[type="submit"]').click()
    
    # Aviso en consola
    print("#####     SESIÓN CERRADA     #####", flush=True)

    # Cerrar procesos de selenium
    driver.quit()

def tomar_asistencia(driver):
    # Inicialización de variables
    global materiaActual
    nombreMateria = ''
    mensaje = ''

    # Acceder a la lista de asistencia
    driver.get(MATERIAS['url'][materiaActual]);
    sleep(1)

    # Obtener el nombre de la materia
    nombreMateria = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )
    nombreMateria = nombreMateria.text
    
    if verificar_existencia(driver, "#region-main > div > table.generaltable.attwidth.boxaligncenter > tbody > tr > td.statuscol.cell.c2.lastcol > a"):
        # Selección asistencia
        elemento = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#region-main > div > table.generaltable.attwidth.boxaligncenter > tbody > tr > td.statuscol.cell.c2.lastcol > a"))
        )
        elemento.click()
        sleep(1)

        # Seleccionar presente
        elemento = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, MATERIAS['id_status'][materiaActual]))
        )
        elemento.click()
        sleep(1)

        # Guardar cambios
        elemento = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, 'id_submitbutton'))
        )
        elemento.click()
        sleep(1)

        # Guardar el registro de asistencia
        MATERIAS['asistencia'][materiaActual] = True
    
        # Enviar el aviso de la toma de asistencia
        mensaje = "Asistencia tomada - " + nombreMateria
        print(mensaje, flush=True)
    else:
        mensaje = "No se ha podido tomar asistencia..."
        print("{}".format(mensaje), flush=True)

    notification.notify(title = "## Aviso ##",
                        message = mensaje,
                        app_icon = corregir_ruta("icon.ico"),
                        timeout = 10,
                        toast = False)
    sleep(1)

def inicializar_hilo():
    # Declaración de variables
    global t # Declaramos la variable como global

    primeraClase = MATERIAS['hora'][0]
    ultimaClase = MATERIAS['hora'][len(MATERIAS['hora']) - 1]
    primeraHora = primeraClase.strftime('%H:%M:%S')

    horaActual = datetime.now()
    horaActual = horaActual.replace(second=0, microsecond=0)

    # Evaluar si aun no inician las clases
    if horaActual.time() < primeraClase.time(): ##iniciar hilo antes del delay
        # Programar los eventos
        t = Temporizador(primeraHora, 1, main)
        t.start()
    else:
        # Evaluar si no han terminado las clases
        if verificar_horario():
            if datetime.now().time() < ultimaClase.time():
                # Si el usuario lo desea, tomar la primera asistencia
                resp = input("¿Deseas tomar la asistencia de esta clase? (S/N)")
                resp = resp.lower()
                if(resp == 's'):
                    main()

                # Programar el resto de eventos
                claseSig = horaActual.replace(minute=20, second=0, microsecond=0)
                claseSig += timedelta(hours=1)
                claseSig = claseSig.strftime("%H:%M:%S")
                t = Temporizador(claseSig, 1, main)
                t.start()
            else:
                print("###  Ultima clase  ###")
                main()

def main():
    # Abrir el navegador
    # driver = webdriver.Chrome(options = chrome_options, executable_path=EXECUTABLE_PATH)
    driver = uc.Chrome(options = chrome_options)
    # Realizar el inicio de sesión
    iniciar_sesion(driver)
    # Realizar la toma de asistencia
    tomar_asistencia(driver)
    # Cerrar la sesión
    cerrar_Sesion(driver)
        
def menu():
    global t
    opcion = 0

    while opcion != 4:
        if opcion == 1: # Iniciar automatización
            inicializar_hilo()
            sleep(1)

        if opcion == 2: # Detener automatización
            if t != False:
                t.stop() # Detenemos el hilo
                sleep(2)
            else:
                print("La asistencia automática esta DESACTIVADA", flush=True)
                sleep(1)
        
        if opcion == 3: # Tomar asistencia manualmente
            if verificar_horario():
                main()
            sleep(2)

        print("", flush=True)
        print("\t---  Menu  ---")
        print("1 - Iniciar asistencia automática")
        print("2 - Detener asistencia automática")
        print("3 - Tomar asistencia")
        print("4 - Salir")

        while True:
            try:
                opcion = int(input("Elije una opción: "))
                break
            except ValueError:
                print("Debes escribir un número.")

        print("", flush=True)

# if __name__ == "__main__":
#     try: 
#         menu()
#         if t != False:
#             t.stop() # Detenemos el hilo
#     except KeyboardInterrupt as e:
#         if t != False:
#             t.stop() # Detenemos el hilo
#         sys.exit(e)

if __name__ == "__main__":
    
    balloontip.balloon_tip("Ss","ss")
    sleep(1000)