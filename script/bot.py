import sys, os
import balloontip
import encriptador
import json
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


# Declaración de variables
json_path = "../data.json"

# Configuración del webdriver [Chrome]
chrome_options = webdriver.ChromeOptions()
chrome_options.headless = False

# Este será el nuevo hilo
t = False

# Leer la configuración
data_file = open(json_path, "r", encoding='utf8')
data = json.load(data_file)
data_file.close()

def actualizar_datos():
    data_file = open(json_path, "w", encoding='utf8')
    json.dump(data, data_file, ensure_ascii=False)
    data_file.close()

def asignar_hora():
    hora_actual = datetime.now().time()
    
    # Obtener la materia actual
    for i in data['materias']:   
        # Evaluar si se ha asignado alguna hora / materia
        if hora_actual == datetime.strptime(data['materias'][i]['horario'], '%H:%M:%S').time():
            data['asistencia']['claseActual'] = str(i)
            data['asistencia']['siguienteClase'] = str(int(i) + 1)
            break

    actualizar_datos()

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

                if data['asistencia']['claseActual'] == '5': # Si ya es la ultima hora (No hay mas clases)
                    self.stop()
                else:
                    hora += timedelta(hours=1)
                    hora = hora.replace(hour = hora.hour, minute=15, second=0, microsecond = 0)
                    print('Próxima ejecución programada el {0} a las {1}'.format(hora.date(),  hora.time()), flush=True)

            sleep(self.delay)
        else:
            print('Ejecución automática finalizada', flush=True)
            asistencias = data['asistencia']['asistenciasTomadas']
            print('Asistencias tomadas: {} / {}'.format(asistencias, '5'), flush=True)
            # os._exit(1)
  
def corregir_ruta(path):
    if getattr(sys, "frozen", False):
        resolved_path = os.path.abspath(os.path.join(sys._MEIPASS, path))
    else:
        resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))

    return resolved_path

def verificar_horario():

    clase = 0
    primera_clase = datetime.strptime(data['materias']['1']['horario'], '%H:%M:%S').time()
    ultima_clase = datetime.strptime(data['materias']['5']['horario'], '%H:%M:%S').time()
    hora_test = datetime.now()
    delay = datetime.strptime(data['delay'], '%H:%M:%S').time().minute

    # hora_test = datetime.strptime('19:57:00', '%H:%M:%S') # ELIMINAR DESPUES DE PRUEBAS
   
    if hora_test.hour < primera_clase.hour:
        # print("DESDE CERO, ANTES DE CLASES")
        t = Temporizador("15:15:00", 1, main)
        t.start()
    else:
        ultima_clase = ultima_clase.replace(hour = 20, minute=0, second=0, microsecond = 0) # Reajustar horario de salida
        if hora_test.hour < ultima_clase.hour:
            for i in data['materias']:
                if hora_test.hour == datetime.strptime(data['materias'][i]['horario'], '%H:%M:%S').time().hour:
                    data['asistencia']['claseActual'] = i
                    clase = i
                    if i != "5":
                        data['asistencia']['siguienteClase'] = str(int(i) + 1)
                    else:
                        data['asistencia']['siguienteClase'] = None
                    actualizar_datos()
                    break
        

            if hora_test.minute < delay:
                # Programación habitual
                horario = datetime.strptime(data['materias'][clase]['horario'], '%H:%M:%S')
                horario += timedelta(minutes=15)
                t = Temporizador(horario.time(), 1, main)
                t.start()
                # print("CLASES INICIADAS ANTES DEL DELAY")
                # print(horario.time())
            else:
                if hora_test.minute < datetime.strptime('00:57:00', '%H:%M:%S').time().minute:
                    # Programas con minutos acutal + 2
                    horario = datetime.strptime(data['materias'][clase]['horario'], '%H:%M:%S')
                    horario += timedelta(minutes=int(hora_test.minute) + 2)
                    t = Temporizador(horario.time(), 1, main)
                    t.start()
                    # print("CLASES INICIADAS DESPUES DEL DELAY")
                    # print(horario.time())
                else:
                    # print("CLASES INICIADAS TOMA INMEDIATA DEBIDO AL LIMITE")
                    # Tomar asistencia inmediatamente
                    if clase != '5':
                        horario = datetime.strptime(data['materias'][str(int(clase) + 1)]['horario'], '%H:%M:%S')
                        horario += timedelta(minutes=15)    
                        t = Temporizador(horario.time(), 1, main)
                        t.start() 
                        # print(horario.time())
                    else:
                        print('Ejecución automática finalizada', flush=True)
                        asistencias = data['asistencia']['asistenciasTomadas']
                        print('Asistencias tomadas: {} / {}'.format(asistencias, '5'), flush=True)
        else:
            print("Las clases ya han concluido")



def verificar_existencia(driver, selector):
    try:
        driver.find_element_by_css_selector(selector)
    except NoSuchElementException:
        return False
    return True

def iniciar_sesion(driver):
    # Redireccionar a la página principal de Aula Virtual
    driver.get(data['homePageUrl'])

    # Introducir los datos del usuario
    inputUsername = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    inputUsername.send_keys(data['user']['username'])

    inputPass = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.NAME, "password"))
    )
    inputPass.send_keys(encriptador.descifar_contra())

    loginButton = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "loginbtn"))
    )

    # Desencadenar un clic en iniciar sesión
    loginButton.click()
    sleep(1)

    print("#####     SESIÓN INICIADA     #####", flush=True)

def tomar_asistencia(driver):
    # Inicialización de variables
    # clase_actual = data['asistencia']['claseActual']
    clase_actual = str("1")
    mensaje = ''

    # Acceder a la lista de asistencia
    driver.get(data['materias'][clase_actual]['url'])
    sleep(1)

    # Obtener el nombre de la materia
    nombreMateria = data['materias'][clase_actual]['nombre']
    
    # ALGO...
    if verificar_existencia(driver, "#region-main > div > table.generaltable.attwidth.boxaligncenter > tbody > tr > td.statuscol.cell.c2.lastcol > a"):
        # Selección asistencia
        elemento = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#region-main > div > table.generaltable.attwidth.boxaligncenter > tbody > tr > td.statuscol.cell.c2.lastcol > a"))
        )
        elemento.click()
        sleep(1)

        # Seleccionar presente
        elemento = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, data['materias'][clase_actual]['id_status']))
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
        data['materias'][clase_actual]['asistencia'] = True
        data['asistencia']['asistenciasTomadas'] += 1
        actualizar_datos()

        # Enviar el aviso de la toma de asistencia
        mensaje = "Asistencia tomada - " + nombreMateria
        print(mensaje, flush=True)
    else:
        mensaje = "No se ha podido tomar asistencia..."
        print("{}".format(mensaje), flush=True)

    balloontip.balloon_tip("### AVISO ###", mensaje)
    sleep(1)

def cerrar_Sesion(driver):
    # Redirección al log out
    driver.get(data['logoutPageUrl'])

    # Desencadenar click en el botón Cerrar
    driver.find_element_by_css_selector('button[type="submit"]').click()
    
    # Aviso en consola
    print("#####     SESIÓN CERRADA     #####", flush=True)

    # Cerrar procesos de selenium
    driver.quit()

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
    # driver = uc.Chrome(options = chrome_options)
    # iniciar_sesion(driver)
    # sleep(1)
    # tomar_asistencia(driver)
    # sleep(1)
    # cerrar_Sesion(driver)
    verificar_horario()

    