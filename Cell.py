import numpy as np
import random as rd
import scipy

class Dand:

    Temp_max=30.0
    Temp_min=-10.0
    Temp_best=18.0
    
    Humi_max=1
    Humi_min=0

    Phot_max=1
    Phot_min=0

    pH_min=4.0
    pH_best=7.1
    pH_max=8.0   #各类统一量纲需要用的参数都设为类变量

    st_fast=float(1/(79-14)) #14
    st_slow=float(1/(139-21)) #21

    def __init__(self,Ti):    #Ma 为成熟度, Germ为是否发芽，发芽前成熟度都等于0
        self.Ma=0               #目前版本的成熟度是按加算
        self.Germ=False
        self.Birth=Ti

    def grow(self,d_g,ti,te):
        t = ti - self.Birth
        if d_g==-1:
            self.Ma=1e5+7    #为产完种子对应的生长值,可以1e5+7
        elif self.Germ:
            if self.Ma<1e5+6:
                #if self.Ma==0: self.Ma+=21.0/139.0+float(np.random.rand())*(14.0/79.0-21.0/139.0)  #问题：是否采用rand?
                self.Ma+=rd.gauss(d_g,(Dand.st_fast-Dand.st_slow)/4.0)   #Suit是根据气候条件和拥挤程度返回生长值的函数，现在待定
                #print("{:.6f}".format(float(self.Ma)))
        elif t>0:
            mu=0.1698*(te**2)-5.928*te+62.45
            sigma=0.02813*(te**2)-0.8233*te+10.38
            G_p=0.7*scipy.stats.norm.cdf(t,mu,sigma)
            G_p_1 = 0.7*scipy.stats.norm.cdf(t-1,mu,sigma)
            rate = (G_p-G_p_1)/(1-G_p_1)
            cmp=np.random.rand()
            if rate>=cmp:
                self.Germ=True

class cell:

    K=0.40
    Z0=0.03
    Lim=100
    Tot=0
    F_mu=0.39
    coeff=F_mu/(((0.8*2.0)**0.5)**0.75)
    F_sigma=((F_mu-coeff*(0.8**0.75))+(coeff*(2.0**0.75)-F_mu))/2
    MAX_L=0
    
    def __init__(self,Plants,Pos_x,Pos_y):
        #self.Soil=Soil
        self.Plants=Plants
        self.Pos_x=Pos_x
        self.Pos_y=Pos_y

    def can_grow(self):
        if len(self.Plants) > 0 and not all([x.Ma>=1e5+6 for x in self.Plants]):
            return True
        return False

    def Growth(self,D_g,Ti,Temp):   #Temp:温度; Prec:降水; Phot:光照
        l=len(self.Plants)
        for i in range(0,l):
            self.Plants[i].grow(D_g,Ti,Temp)   #self.Tot决定拥挤程度，可能添加

    def can_spread(self):
        if any([x.Ma>=1 and x.Ma<1e5+6 for x in self.Plants]):
            return True
        return False

    def Spread(self,Wind_dir,Wind_speed,Disp_H,Dir_dev,Prec,Ti,size):  #风速风向
        cnt=0
        added_seeds = np.zeros(size, dtype=int) ###
        while (cnt<len(self.Plants) and self.Plants[cnt].Ma>=1 and self.Plants[cnt].Ma<1e5+6):   #Grown_Ma 代表的就是成熟蒲公英的成熟度,并且不能已经吹完
            sd_avg=(151+int(50*np.random.rand()))*(1+int(10*np.random.rand()))
            if Prec<0.05:
                for i in range(0,sd_avg):
                    Dir=rd.gauss(Wind_dir,Dir_dev)
                    F=rd.gauss(cell.F_mu,cell.F_sigma)
                    #print(cell.F_sigma)
                    H=0.05+0.40*np.random.rand()
                    Mu=Wind_speed*cell.K/np.log((H-Disp_H)/self.Z0)
                    W=1.25*Mu*rd.gauss(0,1)
                    if W>F:
                        W=F-0.00000001    #W<F Constraint
                    Dis=Mu/(cell.K*(F-W))*((H-Disp_H)*np.log((H-Disp_H)/(np.e*cell.Z0))+cell.Z0) #calculate random distance with windspeed
                    if Dis<0:
                        print("Negative Dis!")
                        Dis=0
                    Dis_x=int(Dis*np.sin(Dir))
                    Dis_y=int(Dis*np.cos(Dir))
                    x=self.Pos_x
                    y=self.Pos_y
                    if x+Dis_x>=0 and x+Dis_x<cell.MAX_L and y+Dis_y>=0 and y+Dis_y<cell.MAX_L:
                        added_seeds[x+Dis_x, y+Dis_y] += 1 ###
            self.Plants[cnt].grow(-1,-1,-1)  #表示吹完了
            cnt+=1
        return added_seeds ###

    def Add_New(self,Ti):
            plt_num=len(self.Plants)
            if plt_num<cell.Lim:
                if len(self.Plants)==0: cell.Tot+=1
                self.Plants.append(Dand(Ti))  
"""
Linean Suit:
if te<Cell.Dand.Temp_min: st_te=0
        elif te<Cell.Dand.Temp_best: st_te=(te-Cell.Dand.Temp_min)/(Cell.Dand.Temp_best-Cell.Dand.Temp_min)
        elif te<Cell.Dand.Temp_max: st_te=(Cell.Dand.Temp_max-te)/(Cell.Dand.Temp_max-Cell.Dand.Temp_best)
        else: st_te=0

        if hu<Cell.Dand.Humi_min: st_hu=0
        elif hu<Cell.Dand.Humi_max: st_hu=(hu-Cell.Dand.Humi_min)/(Cell.Dand.Humi_max-Cell.Dand.Humi_min)
        else: st_hu=0

        if ph<Cell.Dand.Phot_min: st_ph=0
        elif ph<Cell.Dand.Phot_max: st_ph=(ph-Cell.Dand.Phot_min)/(Cell.Dand.Phot_max-Cell.Dand.Phot_min)
        else: st_ph=0

        if pr<Dand.Prec_min: st_pr=0
        elif pr<Dand.Prec_max: st_pr=(pr-Dand.Prec_min)/(Dand.Prec_max-Dand.Prec_min)
        else: st_pr=0
        
        if ac<Cell.Dand.pH_min: st_ac=0
        elif ac<Cell.Dand.pH_best: st_ac=(ac-Cell.Dand.pH_min)/(Cell.Dand.pH_best-Cell.Dand.pH_min)
        elif ac<Cell.Dand.pH_max: st_ac=(Cell.Dand.pH_max-ac)/(Cell.Dand.pH_max-Cell.Dand.pH_best)
        else: st_ac=0   """

    
