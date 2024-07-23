import numpy as np
import matplotlib.pyplot as plt
import math

volts_input = 3  
initial_requests = 0
total_time = 301
max_requests_server = 2000 
min_servers = 4 
max_servers = 10 
v_nominal_por_server = 1200 
cant_nominal_servers = 5 
tiempo_scan = 1 

# Coeficientes del controlador PD 
Kp = 1
Kd = 0.0008

requests = initial_requests
previous_error = 0
num_servers = min_servers
percentages_CPU = [0]
percentages_CPU_V = [0]
cant_CPUs = [num_servers]
cant_requests = [initial_requests]
times = [0]

# 5V    --- 100% --- 2000 rps
# 4.5V  --- 90%  --- 1800 rps
# 4.25V --- 85%  --- 1700 rps
# 4V    --- 80%  --- 1600 rps
# 3.75V --- 75%  --- 1500 rps
# 3.5V  --- 70%  --- 1400 rps
# 3V    --- 60%  --- 1200 rps
# 2.5V  --- 50%  --- 1000 rps
# 2.25V --- 45%  --- 900 rps
# 2V    --- 40%  --- 800 rps
# 1.75V --- 35%  --- 700 rps
# 1.5V  --- 30%  --- 600 rps
# 1.25V --- 25%  --- 500 rps
# 1V    --- 20%  --- 400 rps
# 0.75V --- 15%  --- 300 rps
# 0.5V  --- 10%  --- 200 rps

# Señal de error
# 1.25V --- 25% - fin Umbral 3
# 1V    --- 20% - fin Umbral 2 e inicio Umbral 3
# 0.75V --- 15% - fin Umbral 1 e inicio Umbral 2
# 0.5V  --- 10% - inicio Umbral 1

# Umbral 0 = [50% a 70%]
# Umbral 1 = [45% a 50%] y [70% a 75%] -> add/elim 1 server
# Umbral 2 = [40% a 45%] y [75% a 80%] -> add/elim 2 servers
# Umbral 3 = [35% a 40%] y [80% a 85%] -> add/elim 3 servers

def percentaje_translator(requests, num_servers, temp):
    requests_per_server = requests / num_servers
    cpu_usage = 100 * requests_per_server / max_requests_server
    if temp:
        cpu_usage += 10
    volts = cpu_usage * 5 / 100  # calculo el porcentaje de uso de CPU en V
    return (volts, cpu_usage)

inicializacion = {1: 1200, 2:3600, 3:4800, 4:5700, 5:6000}
def generate_requests(t):
    if t in inicializacion:
        return inicializacion[t]
    r = np.random.uniform(0.89, 1.11)
    return r * v_nominal_por_server * cant_nominal_servers

# Perturbaciones
perturbaciones = {136: 2250, 151: 2250, 166: 2250}
def generate_perturbacion(t):
    if t in perturbaciones:
        return perturbaciones[t]
    return 0

# Umbral de control
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

# Perturbaciones de temperatura
aumento_temperatura = set(range(100, 104)).union(range(250, 254))
def temp_perturbation(t):
    return t in aumento_temperatura

# Simulación del proceso
for t in range(1, total_time, tiempo_scan): 
    requests = generate_requests(t)

    # if t in range(50, 60):
    # #     requests += int(input('Ingrese cantidad de requests extra: '))
    # #     volts_input = float(input('Ingrese volts de entrada: '))

    perturbacion_extra_req = generate_perturbacion(t)
    requests += perturbacion_extra_req

    temp = temp_perturbation(t)

    (volts_percentaje, cpu_usage) = percentaje_translator(requests, num_servers, temp)

    error = volts_input - volts_percentaje
    derivative = (error - previous_error)
    previous_error = error

    control_signal = umbrales(error) + round(Kd * derivative, 3)

    new_num_servers = math.ceil(num_servers + control_signal)
    limited_new_num_servers = max(min_servers, min(max_servers, new_num_servers))
    
    percentages_CPU.append(cpu_usage)
    percentages_CPU_V.append(volts_percentaje)
    cant_CPUs.append(limited_new_num_servers)
    cant_requests.append(requests)
    times.append(t)
    print(f'Tiempo: {t} - Cantidad de servidores activos: {num_servers} - Porcentaje de uso de CPU: {cpu_usage:.2f}%')
    print(f'Cantidad de requests: {int(requests)} - Señal de control: {control_signal:.3f} - Nuevo numero de servidores: {limited_new_num_servers}')

    num_servers = limited_new_num_servers
    print('-----------------------------------------------------------------')


plt.figure(figsize=(15, 10))

# Gráfico de temperatura
plt.subplot(3, 1, 1)
plt.plot(times, percentages_CPU, label='% CPU en Volts')
plt.axhline(y=35, color='y', linestyle='--', label='Umbral 3')
plt.axhline(y=40, color='g', linestyle='--', label='Umbral 2')
plt.axhline(y=45, color='b', linestyle='--', label='Umbral 1')
plt.axhline(y=50, color='b', linestyle='--', label='')
plt.axhline(y=60, color='r', linestyle='--', label='% CPU deseado')
plt.axhline(y=70, color='b', linestyle='--', label='')
plt.axhline(y=75, color='b', linestyle='--', label='')
plt.axhline(y=80, color='g', linestyle='--', label='')
plt.axhline(y=85, color='y', linestyle='--', label='')
plt.xlabel('Tiempo (seg)')
plt.ylabel('% CPU (V)')
plt.title('Simulación de control de CPU')
plt.legend()
plt.grid(True)

plt.subplot(3, 1, 2)
plt.plot(times, cant_CPUs, label='cant CPU')
plt.xlabel('Tiempo (seg)')
plt.ylabel('cant CPU')
plt.legend()
plt.grid(True)

plt.subplot(3, 1, 3)
plt.plot(times, cant_requests, label='cant requests')
plt.xlabel('Tiempo (seg)')
plt.ylabel('cant requests')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()
