import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# estado transitorio, se representa?
# entrada, punto suma
# controlador 
# actuador que segun la salida del controlador levante o baje servers
# perturbacion DOS
# proceso que con un random dentro de lo normal genere requests
# Salida de cantidad de requests atendidas
# transductor que sabiendo las requests que se atendieron y la cantidad de servidores activos diga 
# cuantas atendio cada server y lo transforme a un porcentaje de uso de CPU

input = 3  # Porcentaje de uso de CPU deseado en V
initial_requests = 0  # Número inicial de requests
time_step = 1  
total_time = 500  
max_requests = 800 #definir
v_nominal = 500
average_time = 0.005 #Cuanto tardamos en responder la request

# Coeficientes del controlador PD 
Kp = 0.5
Kd = 0.01

requests = initial_requests
previous_error = 0
num_servers = 1


def percentaje_translator(requests, num_servers):
    requests_per_server = requests / num_servers
    cpu_usage = requests_per_server / max_requests
    return cpu_usage # multiplicar por el estimativo del porcentaje a volts

def generate_requests():
    r = np.random.uniform(0.8, 1.2)
    return r * v_nominal

def process(average_time):
    return 1 / average_time

# Simulación del proceso
for t in range(1, total_time):
    requests += generate_requests()

    #Aca iria el DOS

    requests -= process(average_time) # no se si es necesario o si asumimos que no se acumulan y todas se responden en ese tiempo.

    volts_percentaje = percentaje_translator(requests, num_servers)

    error = input - volts_percentaje
    derivative = (error - previous_error) 

    control_signal = Kp * error + Kd * derivative

    if 1 > control_signal > -1:
        num_servers += 0
    elif 2 > control_signal >= 1:
        num_servers += 1
    elif control_signal > 3:
        num_servers += 3
    elif -1 >= control_signal > -2:
        num_servers -= 1
    elif -2 >= control_signal > -3:
        num_servers -= 2
    elif control_signal <= -3:
        num_servers -= 3 # chequear que efectivamente haya la cantidad de servers que se apagan