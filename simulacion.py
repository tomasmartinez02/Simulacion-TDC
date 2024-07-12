import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time

# estado transitorio, se representa?
# entrada, punto suma
# controlador 
# actuador que segun la salida del controlador levante o baje servers
# perturbacion DOS
# proceso que con un random dentro de lo normal genere requests
# Salida de cantidad de requests atendidas
# transductor que sabiendo las requests que se atendieron y la cantidad de servidores activos diga 
# cuantas atendio cada server y lo transforme a un porcentaje de uso de CPU

volts_input = 3  # Porcentaje de uso de CPU deseado en V equivalente a 60%
initial_requests = 0  # Número inicial de requests
time_step = 1  
total_time = 500  
max_requests_server = 2000 # por calculo de relacion de solidaridad
min_servers = 3 # -> si o si tiene que ser 3 o más. Si es 1 o 2 se comporta raro cuando hay pocas requests
max_servers = 10 #definir
v_nominal_por_server = 1200 # requests por segundo equivalente a 60% por relacion de solidaridad
average_time = 0.0005 #definir Cuanto tardamos en responder la request

# Coeficientes del controlador PD 
Kp = -1
Kd = 0

requests = initial_requests
previous_error = 0
num_servers = min_servers

# 5V --- 100% --- 2000 rps
# 4.5V --- 90% --- 1800 rps
# 4V --- 80% --- 1600 rps
# 3.5V --- 70% --- 1400 rps
# 3V --- 60% --- 1200 rps
# 2.5V --- 50% --- 1000 rps
# 2V --- 40% --- 800 rps
# 1.5V --- 30% --- 600 rps
# 1.25V --- 25% fin Umbral 3
# 1V --- 20% fin Umbral 2 e inicio Umbral 3
# 0.75V --- 15% fin Umbral 1 e inicio Umbral 2
# 0.5V --- 10% inicio Umbral 1

# Umbral 0 = [50% a 70%]
# Umbral 1 = [45% a 50%] y [70% a 75%] -> add/elim 1 server
# Umbral 2 = [40% a 45%] y [75% a 80%] -> add/elim 2 servers
# Umbral 3 = [35% a 40%] y [80% a 85%] -> add/elim 3 servers

def percentaje_translator(requests, num_servers):
    requests_per_server = requests / num_servers
    cpu_usage = 100 * requests_per_server / max_requests_server
    print('cpu_usage', cpu_usage)
    volts = cpu_usage * 5 / 100  # calculo el porcentaje de uso de CPU en V
    return volts

def generate_requests():
    r = np.random.uniform(0.8, 1.2)
    return r * v_nominal_por_server

def process(average_time):
    return 1 / average_time

# def Kp_umbrales(error):
#     abs_error = abs(error)
#     if abs_error < 0.5:             # 0.5V = 10% CPU
#         return -1
#     elif 0.5 <= abs_error < 0.75:   # 0.75V = 15% CPU
#         return -2
#     elif 0.75 <= abs_error < 1:     # 1V = 20% CPU
#         return -2.67
#     elif 1 <= abs_error < 1.25:     # 1.25V = 25% CPU
#         return -3
#     else:
#         return -3

def umbrales(error):
    abs_error = abs(error)
    if abs_error < 0.5:             # 0.5V = 10% CPU
        return 0
    elif 0.5 <= abs_error < 0.75:   # 0.75V = 15% CPU
        return -1 if error > 0 else 1
    elif 0.75 <= abs_error < 1:     # 1V = 20% CPU
        return -2 if error > 0 else 2
    elif 1 <= abs_error < 1.25:     # 1.25V = 25% CPU
        return -3 if error > 0 else 3
    else:
        return -3 if error > 0 else 3

# Simulación del proceso
for t in range(1, total_time): # habría que poner que el Scan es cada 15 seg ???
    print('num_servers', num_servers)

    # requests = generate_requests()
    requests = int(input("Please enter an integer: "))
    print('requests', requests)

    #Aca iria el DOS

    # requests -= process(average_time) # no se si es necesario o si asumimos que no se acumulan y todas se responden en ese tiempo.

    volts_percentaje = percentaje_translator(requests, num_servers)

    error = volts_input - volts_percentaje
    derivative = (error - previous_error)
    previous_error = error

    # kp2 = Kp_umbrales(error)
    # control_signal = kp2 * error + Kd * derivative #umbrales???

    control_signal = umbrales(error) + Kd * derivative
    print ('control_signal', control_signal)
    
    new_num_servers = 0
    if 1 > control_signal > -1:
        new_num_servers = num_servers
    elif 2 > control_signal >= 1:
        new_num_servers = num_servers + 1
    elif 3 > control_signal >= 2:
        new_num_servers = num_servers + 2
    elif control_signal >= 3:
        new_num_servers = num_servers + 3
    elif -1 >= control_signal > -2:
        new_num_servers = num_servers - 1
    elif -2 >= control_signal > -3:
        new_num_servers = num_servers - 2
    elif control_signal <= -3:
        new_num_servers = num_servers - 3
    
    print('NEW new_num_servers', new_num_servers)
    num_servers = max(min_servers, min(max_servers, new_num_servers))
    print('-----------------------------------------------------------------')