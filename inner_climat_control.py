# coding=utf-8
# Benoetigte Module werden importiert und eingerichtet
import glob
import time
from time import sleep
import RPi.GPIO as GPIO

# Einstellen wie oft gemessen werden soll. (Es reicht einmal pro Minute)
sleeptime = 60

"""Der One-Wire EingangsPin wird deklariert und der integrierte PullUp-Widerstand aktiviert
Der PullUp-Widerstand ist im Sensor enthalten"""
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Nach Aktivierung des Pull-UP Widerstandes wird gewartet,
# bis die Kommunikation mit dem Temperatursensor DS18B20 Sensor aufgebaut ist
print('Warte auf Initialisierung...')

base_dir = '/sys/bus/w1/devices/'
while True:
    try:
        device_folder = glob.glob(base_dir + '28*')[0] # todo Was bedeutet diese Glob function?
        break
    except IndexError:
        sleep(0.5)
        continue
device_file = device_folder + '/w1_slave'


# Funktion wird definiert, mit dem der aktuelle Messwert am Sensor ausgelesen werden kann
def TemperaturMessung():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

# Zur Initialisierung, wird der Sensor einmal "blind" ausgelesen
TemperaturMessung()

# Die Temperaturauswertung: Beim Raspberry Pi werden erkannte "one-Wire Slaves" im Ordner
# /sys/bus/w1/devices/ einem eigenen Unterordner zugeordnet. In diesem Ordner befindet sich die Datei w1-slave
# in dem die Daten, die über dem One-Wire Bus gesendet wurden gespeichert sind.
# In dieser Funktion werden diese Daten analysiert und die Temperatur herausgelesen und ausgegeben
def TemperaturAuswertung():
    lines = TemperaturMessung()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = TemperaturMessung()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

# Hauptprogrammschleife
# Die gemessene Temperatur wird in der Konsole ausgegeben - zwischen den einzelnen Messungen
# ist eine Pause, deren Länge mit der Variable "sleeptime" eingestellt werden kann
try:
    while True:
        print ('---------------------------------------')
        print("Temperatur:", TemperaturAuswertung(), "°C")
        time.sleep(sleeptime)

except KeyboardInterrupt:
    GPIO.cleanup()
