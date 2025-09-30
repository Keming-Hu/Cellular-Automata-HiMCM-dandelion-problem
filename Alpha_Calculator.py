import numpy as np
te=float(input()) #Input Temperature
hu=float(input()) #Input Humidity

gamma=3.0

Temp_max=30.0
Temp_min=-10.0
Temp_best=18.0

Humi_max=0.07
Humi_min=-0.02

if te<Temp_min: st_te=0
elif te<Temp_best: st_te=(te-Temp_min)/(Temp_best-Temp_min)
elif te<Temp_max: st_te=(Temp_max-te)/(Temp_max-Temp_best)
else: st_te=0

if hu<Humi_min: st_hu=0
elif hu<Humi_max: st_hu=(hu-Humi_min)/(Humi_max-Humi_min)
else: st_hu=0

st_hu=np.tanh(st_hu*gamma)

st_te=np.tanh(st_te*gamma)

print(st_te)  #Temperature alpha
print(st_hu)   #Humidity alpha
