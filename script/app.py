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

                    print('PRÓXIMA EJECUCIÓN PROGRAMADA A LAS → {0}'.format(self.schedule.time()), flush=True)

            sleep(1)
        else:
            print("### EJECUCIÓN AUTOMÁTICA FINALIZADA ###", flush=True)

class AttendanceBot():
    def __init__(self):
        self.data = None
        self.json_path = '../data.json'
        self.schedule = None
        self.timer = None

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

    def take_attendance(self):
        print("#### FUNCIÓN EJECUTADA ####")

    def set_class(self):
        self.get_data()
        time = datetime.now()
        
        ##########################################
        time = datetime.strptime('14:57', '%H:%M')
        ##########################################
        
        first_class = datetime.strptime(self.data['classes']['1']['schedule'], '%H:%M')
        last_class = datetime.strptime(self.data['classes']['5']['schedule'], '%H:%M')

        if time.time() < first_class.time():
            self.schedule =  datetime.strptime(self.data['classes']['1']['schedule'], '%H:%M')
        else:
            if time.hour <= last_class.hour:
                for i in self.data['classes']:
                    if time.hour == datetime.strptime(self.data['classes'][i]['schedule'], '%H:%M').hour:
                        self.schedule =  datetime.strptime(self.data['classes'][i]['schedule'], '%H:%M')
                        break
            else:
                self.schedule = None

        if self.schedule is not None and time.time() >= first_class.time():
            if time.minute >= datetime.strptime(self.data['delay'], '%M').minute:
                if time.minute < datetime.strptime('57', '%M').minute:
                    self.schedule = self.schedule.replace(minute=time.minute+2)
                else:
                    #### Tomar asistencia ####
                    self.take_attendance()
                    ##########################
                    if self.schedule.hour + 1 < 20:
                        self.schedule += timedelta(hours=1)
                    else:
                        self.schedule = None

    def start_bot(self):
        self.set_class()
        if self.schedule is None:
            print("SCHEDULE NONE")
        else:
            print("### BOT INICIADO ###")
            # self.schedule = self.fix_datetime(self.schedule)

            ################################################
            self.schedule = datetime.now()
            self.schedule += timedelta(minutes=1)
            self.schedule = self.fix_datetime(self.schedule)
            ################################################
            
            self.timer = Timer(self.schedule, self.take_attendance)
            self.timer.start()

    def stop_bot(self):
        if self.timer.is_alive():
            self.timer.stop()
        else:
            print("### EL BOT ESTÁ APAGADO ###")


if __name__ == "__main__":
    try: 
        bot = AttendanceBot()
        bot.start_bot()
        input()
        bot.stop_bot()
    except KeyboardInterrupt as e:
        bot.stop_bot()
