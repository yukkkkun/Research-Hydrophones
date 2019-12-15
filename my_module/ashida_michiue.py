import numpy as np
import pandas as pd

import math

#自作モジュール
import getdfs


#################
##初期値cm, g
rho = 1 #g/cm3
grav = 980 #cm/s**2
ib = 1/20 #? パーセント？角度？
s = 1.65
width = 500#cm
sigma_by_rho = 2.65
rho_s = 2.65 #g/cm**3
#################

#furui粒径界の上限
x_furui = [1, 2, 5, 7, 9, 15, 31.5, 50]
#Tot粒径界の上限
x_tot = [2, 5, 6, 7, 8.5, 10, 12.5, 15, 20, 30, 50]
g_furui = ['-1mm(g)', '1-2mm(g)', '2-5mm(g)', '5-7mm(g)', '7-9mm(g)', '9-15mm(g)', '19-31.5mm(g)', '31.5mm-(g)']
percent_furui = ['-1mm(%)', '1-2mm(%)', '2-5mm(%)', '5-7mm(%)', '7-9mm(%)', '9-15mm(%)', '19-31.5mm(%)', '31.5mm-(%)']

###３つの平均を算出######
df_furui = getdfs.get_furui()
furui_percents = [0]*len(percent_furui)
for i in range(1, 9, 3):
    furui_percents = furui_percents + np.array(df_furui[i:i+1][percent_furui])
furui_percent_cumsums = np.cumsum(furui_percents, axis=1).flatten()
furui_percent_cumsum_mean =  furui_percent_cumsums/3

#################

#直線近似
# y=mx+n
# ２点を通る方程式を返却
# (y=数値) or (x=数値) or (y=mx+n)
def makeLinearEquation(x1, y1, x2, y2):
    line = {}
    if y1 == y2:
        # y軸に平行な直線
        line["y"] = y1
    elif x1 == x2:
        # x軸に平行な直線
        line["x"] = x1
    else:
        # y = mx + n
        line["m"] = (y1 - y2) / (x1 - x2)
        line["n"] = y1 - (line["m"] * x1)
    return line

def calc_y(line, dia):
#     print("y=mx+n : ",line)
    percent = line["m"]*dia + line["n"]
#     print("pecent : ", percent)
    return percent
    

x= np.insert(x_furui, 0, 0)
y= np.insert(furui_percent_cumsum_mean, 0, 0)

def calcPercent(dia):
    """
    粒径から通過百分率のパーセントを算出する
    各プロット毎に直線近似
    """
    if (dia >= x[0]) & (dia < x[1]):
        line = makeLinearEquation(x[0], y[0], x[1], y[1])
        percent = calc_y(line, dia)

    elif (dia >= x[1]) & (dia < x[2]):
        line = makeLinearEquation(x[1], y[1], x[2], y[2])
        percent = calc_y(line, dia)

    elif (dia >= x[2]) & (dia < x[3]):
        line = makeLinearEquation(x[2], y[2], x[3], y[3])
        percent = calc_y(line, dia)

    elif (dia >= x[3]) & (dia < x[4]):
        line = makeLinearEquation(x[3], y[3], x[4], y[4])
        percent = calc_y(line, dia)

    elif (dia >= x[4]) & (dia < x[5]):
        line = makeLinearEquation(x[4], y[4], x[5], y[5])
        percent = calc_y(line, dia)

    elif (dia >= x[5]) & (dia < x[6]):
        line = makeLinearEquation(x[5], y[5], x[6], y[6])
        percent = calc_y(line, dia)

    elif (dia >= x[6]) & (dia < x[7]):
        line = makeLinearEquation(x[6], y[6], x[7], y[7])
        percent = calc_y(line, dia)

    elif (dia >= x[7]) & (dia <= x[8]):
        line = makeLinearEquation(x[7], y[7], x[8], y[8])
        percent = calc_y(line, dia)
        
    else:
        print("Diameter is out of range")
        
    return percent


def calc_dia_rate(max_dia, min_dia):
    rate = calcPercent(max_dia) - calcPercent(min_dia)
    return rate/100

def calc_dia_from_percent(percent):
    try_dia = np.arange(0, 50, 0.1)
    
    dia_hold = []
    for dia in try_dia:
        dia_hold.append(calcPercent(dia))
    dia_hold = np.array(dia_hold)
    dia_hold = np.abs(dia_hold-percent)
    key = np.where(dia_hold == np.min(dia_hold))
    percent = try_dia[key]
    
    return percent


def calc_u_star_c_2(dia):
    if dia >= 3.03:
        u_star_c_2 = 80.9*dia
    elif 1.18 <= dia < 3.03:
        u_star_c_2 = 134.6*dia**(31/22)
    elif 0.565 <= dia < 1.18:
        u_star_c_2 = 55.0*dia
    elif 0.065 <= dia < 0.565:
        u_star_c_2 = 8.41*dia**(11/32)
    elif 0 <= dia < 0.065:
        u_star_c_2 = 226*dia
    else:
        print("Diameter is out of range")
#     print(u_star_c_2)

    return u_star_c_2

def calc_tau_star_ci_by_tau_star_cm(di, dm):
    if di/dm >= 0.4:
        tauci_by_taucm = (math.log(19, 10))**2/(math.log(19*(dm/di), 10))**2
    elif di/dm < 0.4:
        tauci_by_taucm = 0.85*(dm/di)
        
    return tauci_by_taucm


def calc_R(WaterLevel, width):
    '''
    R=A/S
    A:面積
    S:
    '''
    A = WaterLevel*width
    S = 2*WaterLevel + width
    # print('A :', A)
    # print('S :', S)
    return A/S

def calc_u_star(R):
    return np.sqrt(grav*R*ib)

def calc_tau_star(u_star, R, d):
    u_star = calc_u_star(R)
    tau_star = (u_star**2)/((sigma_by_rho-1)*grav*d)
    return tau_star

def calc_tau_star_i(u_star, R, di):
    u_star = calc_u_star(R)
    tau_star = (u_star**2)/((sigma_by_rho-1)*grav*di)
    return tau_star



def calc_u_star_e(U, R, dm, tau_star):
    '''
    Uは断面平均流速
    '''
    u_star_e = U/(6.0+5.75*math.log(R/(dm*(1+2*tau_star)),10))
    
    return u_star_e

def calc_tau_star_ei(di, u_star_e):
    tau_star_ei = (u_star_e**2)/((sigma_by_rho-1)*grav*di)
    
    return tau_star_ei

def calc_tau_star_cm(dm):
    tau_star_cm = calc_u_star_c_2(dm)/(s*grav*dm)
    return tau_star_cm

def calc_tau_star_ci(di, dm):
    tau_star_ci_by_tau_star_cm = calc_tau_star_ci_by_tau_star_cm(di, dm)
    tau_star_cm = calc_tau_star_cm(dm)
    tau_star_ci = tau_star_ci_by_tau_star_cm*tau_star_cm
    
    return tau_star_ci
    


def calc_q_ashida_michiue(df, max_dia, min_dia, dm, start=None, end=None, interval=30):
    """
    dm : cmで入れる
    df : 'df' should have 'WaterLevel(cm)' col
    start, end : 始まりと終わりの期間
    interval : データ間のインターバル
    """

    if start== None:
        start = str(df.axes[0][0])
    else:
        pass

    if end == None:
        end = str(df.axes[0][-1])
    else:
        pass
        
    print("粒径中央値 dm[cm]：", dm)

    di = (max_dia + min_dia)/2
    print('対象粒径平均値 di[cm]', di)

    p_di = calc_dia_rate(max_dia, min_dia)
    print("対象粒径界割合 p_di : ", p_di)

    q_bi_sum = 0
    q_weigh_sum = 0

    # for i in range(len(df)):
    for i in range(1): # test


        WaterLevel = np.array(df['WaterLevel(cm)'][i:i+1])
        R = calc_R(WaterLevel, width)

        u_star = calc_u_star(R)
        u_star_cm_2 = calc_u_star_c_2(dm)
        tau_star_cm = calc_tau_star_cm(dm)

        #Uは断面平均流速じゃないといけない！！これはたぶんおかしい！
        U = np.array(df['Velocity(m/s)'][i:i+1])*100 #cm/s

        u_star = calc_u_star(R)

        tau_star = calc_tau_star(u_star, R, d=di)

        u_star_e = calc_u_star_e(U, R, dm, tau_star)

        tau_star_ei = calc_tau_star_ei(di, u_star_e)

        tau_star_ci = calc_tau_star_ci(di, dm)

        tau_star_i = calc_tau_star_i(u_star, R, di)

        u_star_ci = np.sqrt(calc_u_star_c_2(di))

        q_bi = 17*p_di*u_star_e*di*tau_star_ei*(1-(tau_star_ci/tau_star_i))*(1-(u_star_ci/u_star))
        q_weigh = q_bi*rho_s

        # q_bi_sum += q_bi*60*interval
        q_bi_sum += q_bi

        # q_weigh_sum += q_weigh*60*interval
        q_weigh_sum += q_weigh


        # print('WaterLevel(cm) :', WaterLevel)
        # print('R : ', R)
        # print('u_star : ', u_star)
        # print('u_star_cm_2 : ', u_star_cm_2)
        # print('tau_star_cm : ', tau_star_cm)
        # print('U [cm/s]: ', U)
        # print('u_star : ', u_star)
        # print('tau_star :', tau_star)
        # print('u_star_e : ', u_star_e)
        # print('tau_star_ei : ', tau_star_ei)
        # print('tau_star_ci : ', tau_star_ci)
        # print('tau_star_i : ', tau_star_i)
        # print('u_star_ci : ', u_star_ci)
        # print('p_di : ', p_di)
        # print('u_star_e : ', u_star_e)
        # print('di : ', di)
        # print('tau_star_ei : ', tau_star_ei)
        # print('tau_star_ci : ', tau_star_ci)
        # print('tau_star_i : ', tau_star_i)
        # print('u_star_ci : ', u_star_ci)
        # print('u_star : ', u_star)
        # print('q_bi(cm**3/s)', q_bi)
        # print('q_weigh(g/s)', q_weigh)

    print('q_bi(cm**3)', q_bi)
    print('q_weigh(g)', q_weigh)

    return q_bi_sum, q_weigh_sum


# if __name__ == "__main__":

    # USE_YEAR = '2017_2018'
    # if USE_YEAR == '2017_2018':
    #     cols_use = names_of_center + ['Load_Avg', 'Load_Avg_difference', 'WaterLevel(cm)', 'Velocity(m/s)']

    #     print('COL_USE :' +  str(cols_use))

    #     df2017 = getdfs.get2017method2cleanedmean_pit_true()
    #     df2017 = df2017[cols_use]

    #     list_df2018_3events = getdfs.get2018_3events_method2_mean()
    #     for i, df2018_each in enumerate(list_df2018_3events):
    #         list_df2018_3events[i] = df2018_each[cols_use]

    #     df_all = pd.DataFrame()
    #     df_all = df_all.append(df2017)
    #     del df2017

    #     for i, df2018_each in enumerate(list_df2018_3events):
    #         df_all = df_all.append(df2018_each)

    #     del list_df2018_3events


    # dm = calc_dia_from_percent(50)
    # calc_q_ashida_michiue(df_all, max_dia=0.065, min_dia=0, dm=dm,
    #                                     start='2017-09-21 00:00:00', end='2017-09-23 00:00:00',
    #                                     interval=30)

        