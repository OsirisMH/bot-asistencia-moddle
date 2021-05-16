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
from time import sleep, strptime
from datetime import date, datetime, timedelta
from threading import Thread

class Timer(Thread):
    def __init__(self, function):
        super(Timer, self).__init__()
        self._state = True
        self.function = function
        self.schedule = None
        self.last_class = None

    def set_schedule(self, class_time):
        self.schedule = class_time

    def stop(self):
        self._state = False

    def run(self):
        last_class = datetime.strptime('19', '%H')
        print('Proxima ejecución programada a las {0}'.format(self.schedule.time()), flush=True)

        while self._state:
            if self.schedule <= datetime.now():
                # Verificar si las clases no han concluido
                if self.schedule.hour != last_class:
                    # Ejecutar la función
                    self.function()
                else:
                    # Finalizar el timer
                    self.stop()

                # Programar la siguiente ejecución
                self.schedule += timedelta(hours=1)
                self.schedule = self.schedule.replace(minute=20,
                                                      second=0,
                                                      microsecond=0)

            sleep(1)
        else:
            print('Ejecución automática finalizada', flush=True)


class AttendanceBot():
    def __init__(self):
        self.json_path = '../data.json'
        self.data = None
        self.current_class = None
        self.schedule = { 'hour': None, 'min': None }
  
    def fix_time(self, time):
        if time is not None:
            date = datetime.strftime(datetime.now().date(), '%Y-%m-%' + 'd')+ " " +time
            return datetime.strptime(date, '%Y-%m-%' + 'd %H:%M:%S')
        else:
            return None

    def test_function(self):
        print("Esta es una función de prueba")

    def get_data(self):
        data_file = open(self.json_path, "r", encoding='utf-8')
        self.data = json.load(data_file)
        data_file.close()

    def update_data(self):
        data_file = open(self.json_path, "w", encoding='utf-8')
        json.dump(self.data, data_file, ensure_ascii=False)
        data_file.close()
    
    def change_class(self):
        aux = datetime.strptime(self.data['classes'][self.current_class]['schedule'], '%H:%M:%S')
        hour = datetime.now()
        self.schedule = hour.replace(hour = aux.hour, minute=aux.minute, second=aux.second, microsecond = 0)

    def print_attendances(self):
        attendances = self.data['current_attendance']['attendances_number']
        print('Asistencias tomadas: {} / {}'.format(attendances, '5'), flush=True)

    def check_delay(self, time):
        delay = datetime.strptime(self.data['delay'], '%H:%M:%S')
        if time.minute < delay.minute:
                self.schedule = self.schedule.replace(minute=20)
        else:
            if time.minute < datetime.strptime('00:57:00', '%H:%M:%S').minute:
                self.schedule = self.schedule.replace(minute=int(current_time.minute)+2)
            

    # Setear y ademas vereficar con la asistencia (is_taken) para proceder a la siguiente clase
    def set_class(self):
        # current_date = datetime.now()

        ########################################################
        current_date = datetime.strptime('10:25:00', '%H:%M:%S')
        ########################################################

        classes = self.data['classes']
        first_class = datetime.strptime(classes['1']['schedule'], '%H:%M:%S')
        last_class = datetime.strptime(classes['5']['schedule'], '%H:%M:%S')
        min = current_date.minute
        delay = datetime.strptime('20', '%M')
        last_min = datetime.strptime('57', '%M')

        if current_date.hour < first_class.hour:
            self.data['current_attendance']['current_class'] = "1"
            self.data['current_attendance']['next_class'] = "2"
            print("CLASE ASIGNADA 1 [PRIMERA]")
        else:
            if current_date.hour < last_class.hour:
                for i in classes:
                    if current_date.hour == datetime.strptime(classes[i]['schedule'], '%H:%M:%S').hour:
                        self.data['current_attendance']['current_class'] = i
                        self.data['current_attendance']['next_class'] = str(int(i) + 1) if i != '5' else None
                        print("CLASE ASIGNADA " + self.data['current_attendance']['current_class'])
                        break
            else:
                if current_date.hour == last_class.hour:
                    self.data['current_attendance']['current_class'] = "5"
                    self.data['current_attendance']['next_class'] = None
                    print("CLASE ASIGNADA 5 [ULTIMA]")
                else:
                    self.data['current_attendance']['current_class'] = None
                    self.data['current_attendance']['next_class'] = None
                    print("LAS CLASES YA HAN CONCLUIDO")

        self.current_class = self.data['current_attendance']['current_class']
        
        if self.current_class is not None:
            self.set_delay()
        else:
            self.schedule = None

    def start_timer(self, timer):
        timer.set_schedule(self.schedule)
        print(bot.current_class)
        # timer.start()



if __name__ == "__main__":
    bot = AttendanceBot()
    timer = Timer(1, bot.test_function)
    bot.get_data()
    try: 
        bot.set_class()
        bot.start_timer(timer)
        input("ESPERA")
        timer.stop()
    except KeyboardInterrupt as e:
        timer.stop()