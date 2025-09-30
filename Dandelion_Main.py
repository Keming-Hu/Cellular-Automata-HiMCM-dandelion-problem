import Cell
import scipy.io as sio
import numpy as np
import sys
import pygame
from pygame.locals import *
import matplotlib.pyplot as plt
import matplotlib

MAX=250
MAX_T=365
win_width = 800
win_height = 800
gamma=3.0
parallel=True

def draw(win, shad):
    for i in range(0,MAX):
        for j in range(0,MAX):
            if shad[i][j]!=0:c=55+2*shad[i][j]
            else: c=0
            color=(c,c,c)
            if i==MAX//2 and j==MAX//2:color=(255,0,0)
            pygame.draw.rect(win, color, pygame.Rect(
            i* (win_width / MAX),
            j * (win_height / MAX),
            win_width / MAX,
            win_height / MAX))
        
def Suit(te,hu,ph,ac):
        if te<Cell.Dand.Temp_min: st_te=0
        elif te<Cell.Dand.Temp_best: st_te=(te-Cell.Dand.Temp_min)/(Cell.Dand.Temp_best-Cell.Dand.Temp_min)
        elif te<Cell.Dand.Temp_max: st_te=(Cell.Dand.Temp_max-te)/(Cell.Dand.Temp_max-Cell.Dand.Temp_best)
        else: st_te=0
        st_te=np.tanh(st_te*gamma)

        if hu<Cell.Dand.Humi_min: st_hu=0
        elif hu<Cell.Dand.Humi_max: st_hu=(hu-Cell.Dand.Humi_min)/(Cell.Dand.Humi_max-Cell.Dand.Humi_min)
        else: st_hu=0
        st_hu=np.tanh(st_hu*gamma)

        if ph<Cell.Dand.Phot_min: st_ph=0
        elif ph<Cell.Dand.Phot_max: st_ph=(ph-Cell.Dand.Phot_min)/(Cell.Dand.Phot_max-Cell.Dand.Phot_min)
        else: st_ph=0
        st_ph=np.tanh(st_ph*gamma)


        if ac<Cell.Dand.pH_min: st_ac=0
        elif ac<Cell.Dand.pH_best: st_ac=(ac-Cell.Dand.pH_min)/(Cell.Dand.pH_best-Cell.Dand.pH_min)
        elif ac<Cell.Dand.pH_max: st_ac=(Cell.Dand.pH_max-ac)/(Cell.Dand.pH_max-Cell.Dand.pH_best)
        else: st_ac=0
        st_ac=np.tanh(st_ac*gamma)
        
        return Cell.Dand.st_slow*((Cell.Dand.st_fast/Cell.Dand.st_slow)**float(st_te*st_hu*st_ph*st_ac))

matD=sio.loadmat('Precipitation.mat')
Prec=np.array(matD['Prec'])  #降水

matD=sio.loadmat('Wind_speed.mat')
Wind_speed=np.array(matD['speeddata'])  #风速

matD=sio.loadmat('Dir_avg.mat')  #日均风向
Wind_dir=np.array(matD['angledata_daily'])

matD=sio.loadmat('Dir_dev.mat')  #日均风向标准差
Dir_dev=np.array(matD['angledata_hourly'])

matD=sio.loadmat('Zero_plane_disp_H.mat') #Diplacement Height
Disp_H=np.array(matD['Disp_H'])

matD=sio.loadmat('Light.mat')  #光照
Phot=np.array(matD['Phot'])

matD=sio.loadmat('Temperature.mat') #温度
Temp=np.array(matD['Temp'])

matD=sio.loadmat('Humidity.mat') #湿度
Humi=np.array(matD['Humi'])

#特殊上下界设定模块
Cell.Dand.Phot_max=3.2*(10**7)*1.0
Cell.Dand.Phot_min=0.0
Cell.Dand.Humi_max=0.07
Cell.Dand.Humi_min=-0.02
Cell.cell.MAX_L=MAX

Board=[]
Shadow=[]
for i in range(0,MAX):
        Row=[]
        S_row=[]
        for j in range(0,MAX):
            Row.append(Cell.cell([],i,j))
            S_row.append(0)
        Board.append(Row)
        Shadow.append(S_row)

Board[MAX//2][MAX//2].Add_New(-1)
Board[MAX//2][MAX//2].Plants[0].Ma=1
Shadow[MAX//2][MAX//2]=1

init = False
change_start = True
#Pygame模块

pygame.init()
win = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption('Dandelion')
clock = pygame.time.Clock()

print("OK")
Total=[]

#############################
import multiprocessing
from itertools import chain
from functools import partial
import time
import pickle
import os

t = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
output_dir = os.path.join("output", t)
os.makedirs(output_dir, exist_ok=True)

def grow_one_cell(cell, **kwargs):
    cell.Growth(**kwargs)

def spread_one_cell(cell, **kwargs):
    return cell.Spread(**kwargs)

pool = multiprocessing.Pool()
map_func = pool.imap if parallel else map
###############################

for t in range(0,MAX_T):
    print(t)
    time_start = time.time()
    clock.tick(6)    
    for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_SPACE:
                # 支持按空格暂停/恢复状态变更
                change_start = not change_start
    if change_start:
        draw(win,Shadow)
    pygame.display.update()
    
    delta_G=Suit(Temp[t],Humi[t],Phot[t],6.8)
    display_time_end = time.time()
    print(f"Display: {display_time_end - time_start:.5f} s")

    ##################################

    grow_func = partial(grow_one_cell, D_g=delta_G,Ti=t,Temp=Temp[t])
    _ = list(map_func(grow_func, [x for x in chain(*Board) if x.can_grow()]))
    grow_time_end = time.time()
    print(f"Grow: {grow_time_end-display_time_end:.5f} s")

    size = (len(Board), max([len(x) for x in Board]))
    spread_func = partial(spread_one_cell, Wind_dir=Wind_dir[t],Wind_speed=Wind_speed[t],Disp_H=Disp_H[t],Dir_dev=Dir_dev[t],Prec=Prec[t],Ti=t,size=size)
    all_added_seeds = np.zeros(size, dtype=int)
    for added_seeds in map_func(spread_func, [x for x in chain(*Board) if x.can_spread()]):
        if added_seeds is not None:
            all_added_seeds += added_seeds
    spread_time_end = time.time()
    print(f"Spread: {spread_time_end - grow_time_end:.5f} s")

    for i in range(0,MAX):
        for j in range(0,MAX):
            for i_seed in range(all_added_seeds[i,j]):
                Board[i][j].Add_New(Ti=t)
    add_time_end = time.time()
    print(f"Add: {add_time_end - spread_time_end:.5f} s")
    ########################################

    for i in range(0,MAX):
        for j in range(0,MAX):
            Shadow[i][j]=len(Board[i][j].Plants)
    Total.append(Cell.cell.Tot*1.0)

    pickle.dump(Board, open(os.path.join(output_dir, f"{t}.pkl"), "wb"))
    save_time_end = time.time()
    print(f"Save: {save_time_end - add_time_end:.5f} s")

pool.close()
pool.join()

#数值检查模块
"""            
for i in range(0,MAX):
    print(i)
    flag=0
    for j in range(0,MAX):
        if len(Board[i][j].Plants)!=0:
            flag=1
    if flag!=0:
        for j in range(0,MAX):
            print("{:d} ".format(len(Board[i][j].Plants)),end="")
        print("\n")
print("\n")
"""
Total=np.array(Total)/10000.0
Time_S=np.array(list(range(1,MAX_T+1)))

#覆盖率模块
"""
fig = plt.figure(1,figsize=(4,3),dpi=200)
plt.plot(Time_S,Total,lw=1,color="blue",label="Coverage Rate")
plt.ylim(-0.1,1.1)
plt.xlabel('Day_Number')
plt.ylabel('CR');
plt.legend();
plt.show();
"""

print("End")
    
