import sys, os
import encriptador
import json
import undetected_chromedriver as uc
from pushbullet import Pushbullet
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep, strptime, time
from datetime import date, datetime, timedelta
from threading import Thread

API_KEY_PATH = os.path.abspath("../assets/api_key.txt")

class Timer(Thread):
    def __init__(self, schedule, function):
        super(Timer, self).__init__()
        self._state = True
        self.schedule = schedule # Diccionario
        self.function = function

    def stop(self):
        self._state = False

    def run(self):
        last_class = datetime.strptime('5', '%H')
        print('PRÓXIMA EJECUCIÓN PROGRAMADA A LAS → {0}'.format(self.schedule.time()), flush=True)

        while self._state:
            if self.schedule <= datetime.now():
                # Ejecutar la función
                self.function()

                # Verificar si las clases han concluido
                if self.schedule.hour == last_class.hour:
                    # Finalizar el timer
                    self.stop()
                else:
                    # Programar la siguiente ejecución
                    self.schedule += timedelta(hours=1)
                    self.schedule = self.schedule.replace(minute=20,
                                                        second=0,
                                                        microsecond=0)

                    ##################################### TESTING
                    # self.schedule = datetime.now()
                    # self.schedule += timedelta(minutes=1)
                    #####################################

                    print('PRÓXIMA EJECUCIÓN PROGRAMADA A LAS → {0}'.format(self.schedule.time()), flush=True)

            sleep(1)
        else:
            print("### EJECUCIÓN AUTOMÁTICA FINALIZADA ###", flush=True)

class AttendanceBot():
    def __init__(self):
        self.data = None
        self.json_path = '../data.json'
        self.current_class = None
        self.schedule = None
        self.timer = None
        self.driver = None
        self.chrome_options = None

    def get_data(self):
        data_file = open(self.json_path, "r", encoding='utf-8')
        self.data = json.load(data_file)
        data_file.close()

    def update_data(self):
        data_file = open(self.json_path, "w", encoding='utf-8')
        json.dump(self.data, data_file, ensure_ascii=False)
        data_file.close()

    def reset_value(self, option):
        for i in self.data['current_attendance'][option]:
            i = None

    def fix_datetime(self, time):
        if time is not None:
            aux = self.schedule
            hora = datetime.now()
            hora = hora.replace(hour = aux.hour, minute=aux.minute, second=aux.second, microsecond = 0)
            return hora
        else:
            return None

    def element_exists(self, selector):
        try:
            self.driver.find_element_by_css_selector(selector)
        except NoSuchElementException:
            return False
        return True

    def init_driver(self):
        # Configuración del webdriver [Chrome]
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # self.chrome_options.headless = True

    def login(self):
        self.driver = uc.Chrome(options = self.chrome_options)

        # Redireccionar a la página principal de Aula Virtual
        self.driver.get(self.data['homepage_url'])

        # Introducir los datos del usuario
        inputUsername = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        inputUsername.send_keys(self.data['user']['username'])

        inputPass = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        inputPass.send_keys(encriptador.descifar_contra())

        loginButton = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.ID, "loginbtn"))
        )

        # Desencadenar un clic en iniciar sesión
        loginButton.click()
        sleep(1)

        print("#####     SESIÓN INICIADA     #####", flush=True)

    def take_attendance(self):
        # Inicialización de variables
        message = ''

        # Acceder a la lista de asistencia
        self.driver.get(self.data['classes'][self.current_class]['url'])
        sleep(1)

        # Obtener el nombre de la materia
        class_name = self.data['classes'][self.current_class]['name']
        
        # ALGO...
        if self.element_exists("#region-main > div > table.generaltable.attwidth.boxaligncenter > tbody > tr > td.statuscol.cell.c2.lastcol > a"):
            # Selección asistencia
            element = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#region-main > div > table.generaltable.attwidth.boxaligncenter > tbody > tr > td.statuscol.cell.c2.lastcol > a"))
            )
            element.click()
            sleep(1)

            # Seleccionar presente
            element = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, self.data['classes'][self.current_class]['id_status']))
            )
            element.click()
            sleep(1)

            # Guardar cambios
            element = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, 'id_submitbutton'))
            )
            element.click()
            sleep(1)

            # Guardar el registro de asistencia
            self.data['current_attendance']['attendances_number'] += 1
            self.current_class = str(int(self.current_class) + 1)

            # Enviar el aviso de la toma de asistencia
            message = "Asistencia tomada - " + class_name
            print(message, flush=True)
        else:
            message = "No se ha podido tomar asistencia..."
            print("{}".format(message), flush=True)

        self.current_class = str(int(self.current_class) + 1)
        print(self.current_class)
        notification(API_KEY_PATH, message)

    def logout(self):
        # Redirección al log out
        self.driver.get(self.data['logout_url'])

        # Desencadenar click en el botón Cerrar
        self.driver.find_element_by_css_selector('button[type="submit"]').click()
        
        # Aviso en consola
        print("#####     SESIÓN CERRADA     #####", flush=True)

        # Cerrar procesos de selenium
        self.driver.quit()

    def main_process(self):
        self.login()
        self.take_attendance()
        self.logout()
    
    def set_class(self):
        self.get_data()
        time = datetime.now()
        
        # ########################################## TESTING
        # time = datetime.strptime('14:57', '%H:%M')
        # ##########################################
        
        first_class = datetime.strptime(self.data['classes']['1']['schedule'], '%H:%M')
        last_class = datetime.strptime(self.data['classes']['5']['schedule'], '%H:%M')

        if time.time() < first_class.time():
            self.schedule =  datetime.strptime(self.data['classes']['1']['schedule'], '%H:%M')
            self.current_class = "1"
        else:
            if time.hour <= last_class.hour:
                for i in self.data['classes']:
                    if time.hour == datetime.strptime(self.data['classes'][i]['schedule'], '%H:%M').hour:
                        self.schedule =  datetime.strptime(self.data['classes'][i]['schedule'], '%H:%M')
                        self.current_class = str(i)
                        break
            else:
                self.schedule = None
                self.current_class = None

        if self.schedule is not None and time.time() >= first_class.time():
            if time.minute >= datetime.strptime(self.data['delay'], '%M').minute:
                if time.minute < datetime.strptime('57', '%M').minute:
                    self.schedule = self.schedule.replace(minute=time.minute+2)
                else:
                    #### Tomar asistencia ####
                    self.main_process()
                    ##########################
                    if self.schedule.hour + 1 < 20:
                        self.schedule += timedelta(hours=1)
                        self.current_class = str(int(self.current_class) + 1)
                    else:
                        self.schedule = None
                        self.current_class = None

    def start_bot(self):
        self.init_driver()
        self.set_class()
        if self.schedule is None:
            print("SCHEDULE NONE")
        else:
            print("### BOT INICIADO ###")
            self.schedule = self.fix_datetime(self.schedule)

            ################################################ TESTING
            # self.schedule = datetime.now()
            # self.schedule += timedelta(minutes=1)
            # self.schedule = self.fix_datetime(self.schedule)
            ################################################
            
            self.timer = Timer(self.schedule, self.main_process)
            self.timer.start()

    def stop_bot(self):
        if self.timer.is_alive():
            self.timer.stop()
        else:
            print("### EL BOT ESTÁ APAGADO ###")

def notification(api_key, msg):
    with open(api_key, mode='r') as f:
        key = f.read()

    pb = Pushbullet(key)
    push = pb.push_note('BOT ASISTENCIA', msg)

if __name__ == "__main__":
    try: 
        bot = AttendanceBot()
        bot.start_bot()
        input()
        bot.stop_bot()
    except KeyboardInterrupt as e:
        bot.stop_bot()