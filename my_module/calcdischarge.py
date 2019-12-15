import pandas as pd
import numpy as np
import os
import math
from matplotlib import pyplot as plt

#自作モジュール
import dispgraphs
import getdfs

###########################################################

length_hp_m = 0.275 # ピット直上ハイドロフォン長さ
length_C_m = 0.5 # 5本の真ん中ハイドロフォン長さ
pit_width = 0.2 #ピット流入口長さ

suffix = ['_Tot(1)', '_Tot(2)', '_Tot(3)', '_Tot(4)', '_Tot(5)',
            '_Tot(6)', '_Tot(7)', '_Tot(8)', '_Tot(9)', '_Tot(10)']

names_of_center = ['hp'+ s for s in suffix] # 直上中央ハイドロフォン
names_of_C = ['C'+ s for s in suffix] # 中央ハイドロフォン
names_of_RC = ['RC'+ s for s in suffix] # 中央右ハイドロフォン
names_of_LC = ['LC'+ s for s in suffix] # 中央左ハイドロフォン
names_of_R = ['R'+ s for s in suffix] # 右ハイドロフォン
names_of_L = ['L'+ s for s in suffix] # 左ハイドロフォン
names_of_VR = ['VR'+ s for s in suffix] # 右鉛直ハイドロフォン
names_of_VL = ['VL'+ s for s in suffix] # 左鉛直ハイドロフォン

data_path = os.getcwd()[:-len('notebook')] + 'data\\'

###########################################################

def calc_q(df, W_IDEAL, list_beta, alpha, gamma, start=None, end=None):
    
    if start== None:
        start = str(df.axes[0][0])
    else:
        pass

    if end == None:
        end = str(df.axes[0][-1])
    else:
        pass

    num_of_channel = len(W_IDEAL)
    channel_names = names_of_center[-num_of_channel:]
    
    df = df[start:end]

    qcalc = df[channel_names].mul(np.array(W_IDEAL).reshape(1,num_of_channel)).mul(list_beta.reshape(1,num_of_channel)).sum(axis=1)*(1/((1-alpha)*(1-gamma)))
    qcalc_each = df[channel_names].mul(np.array(W_IDEAL).reshape(1,num_of_channel)).mul(list_beta.reshape(1,num_of_channel)) * (1/((1-alpha)*(1-gamma)))
    
    return qcalc, qcalc_each

def disp_sediment_distribution(df, df_qcalc, qcalc_each, alpha, start, end, num_of_channel, furui_num):
    """
    furui_num
    1: 2017-11-23
    2: 2018-04-28
    3: 2018-07-16
    """
    df_furui = getdfs.get_furui()
    x_furui = [1, 2, 5, 7, 9, 15, 31.5, 50] #furui粒径界の上限
    x_tot = [2, 5, 6, 7, 8.5, 10, 12.5, 15, 20, 30, 50] #Tot粒径界の上限
    percent_furui = ['-1mm(%)', '1-2mm(%)', '2-5mm(%)', '5-7mm(%)', '7-9mm(%)', '9-15mm(%)', '19-31.5mm(%)', '31.5mm-(%)']

    if furui_num == 1:
        furui = df_furui[1:2][percent_furui]
    elif furui_num == 2:
        furui = df_furui[4:5][percent_furui]
    elif furui_num == 3:
        furui = df_furui[7:8][percent_furui]
    else:
        print('Chose out of 1 - 3')
    
    print('furui :', furui)

    furui_percent_cumsum = np.cumsum(furui, axis=1)

    if num_of_channel == 10:
        x_tot = x_tot

    elif num_of_channel == 6:
        x_tot = x_tot[-7:]
    
    qcalc_each = qcalc_each[start:end]

    percent_ini = alpha*100

    print('I set the initial alpha rate as {} here, because you set the alpha when optimizing'.format(percent_ini))
    percents = [percent_ini]
    percents.extend(list(qcalc_each.sum()/qcalc_each.sum().sum()*(100-percent_ini)))
    percents_cumsum = np.cumsum(percents)

    plt.figure(figsize=(6,4))
    ax = plt.subplot(1,1,1) 
    
    ax.scatter(x_tot, percents_cumsum)

    ax.set_xscale('log')
    ax.set_ylim(0,105)
    ax.set_xlim((0.1), 100)

    ax.scatter(x_furui, furui_percent_cumsum)
    plt.show()

    print('I set the initial alpha rate as {} here so that you can see how accurate the sediment distribution given by method2 even though I set the alpha as {} when optimizing'.format(percent_ini, alpha))
    
    if num_of_channel == 10:
        percent_ini = float(furui_percent_cumsum[percent_furui[-7]])

    elif num_of_channel == 6:
        percent_ini = float(furui_percent_cumsum[percent_furui[-4]])
        
    percents = [percent_ini]
    percents.extend(list(qcalc_each.sum()/qcalc_each.sum().sum()*(100-percent_ini)))
    percents_cumsum = np.cumsum(percents)

    plt.figure(figsize=(6,4))
    ax = plt.subplot(1,1,1) 
    
    ax.scatter(x_tot, percents_cumsum)

    ax.set_xscale('log')
    ax.set_ylim(0,105)
    ax.set_xlim((0.1), 100)

    ax.scatter(x_furui, furui_percent_cumsum)
    plt.show()

    dispgraphs.compare_graphs_time_series(df_qcalc, df['Load_Avg_difference'], start=start, end=end)
    plt.show()

def disp_results_method2(df, W_IDEAL, Correction_factor, alpha):
    num_of_channel = len(W_IDEAL)
    channel_names = names_of_center[-num_of_channel:]

    df_qcalc = df[channel_names].mul(np.array(W_IDEAL).reshape(1,num_of_channel)).mul(Correction_factor[:-1].reshape(1,num_of_channel)).sum(axis=1)*(1/((1-alpha)*(1-Correction_factor[-1])))
    qcalc_each = df[channel_names].mul(np.array(W_IDEAL).reshape(1,num_of_channel)).mul(Correction_factor[:-1].reshape(1,num_of_channel)) * (1/((1-alpha)*(1-Correction_factor[-1])))

    print('Bedload Discharge', '#'*10)
    print(df_qcalc)
    print('#'*20)
    print('Whole period')
    dispgraphs.compare_graphs_time_series(df_qcalc, df['Load_Avg_difference'], start=df.axes[0][0], end=df.axes[0][-1])
    plt.show()

    print('#'*20)
    print('2016-06-25 02:00:00 to 2016-7-01 06:00:00')
    dispgraphs.compare_graphs_time_series(df_qcalc, df['Load_Avg_difference'], start='2016-06-25 02:00:00', end='2016-7-01 06:00:00')
    plt.show()

    print('#'*20)

    print('2017-07-11 02:00:00 to 2017-7-15 06:00:00')
    dispgraphs.compare_graphs_time_series(df_qcalc, df['Load_Avg_difference'], start='2017-07-11 02:00:00', end='2017-7-15 06:00:00')
    plt.show()

    print('#'*20)
    print('2018-09-8 00:00:00 to 2018-9-9 06:00:00')
    dispgraphs.compare_graphs_time_series(df_qcalc, df['Load_Avg_difference'], start='2018-09-8 00:00:00', end='2018-9-9 06:00:00')
    plt.show()

    print('#'*20)
    dispgraphs.compare_graphs_scatter(df['Load_Avg_difference'], df_qcalc , linear_regression=True)
    plt.xlim(-2, 50)
    plt.ylim(-2, 50)
    plt.show()

    print('#'*20)
    print('compare_with_furui_result')
    print('#'*20)
    ##########################
    #ふるい結果①
    print('9/21')
    start_921 = '2017-09-21 00:00:00'
    end_921 = '2017-09-23 00:00:00'

    disp_sediment_distribution(df=df, df_qcalc=df_qcalc, qcalc_each=qcalc_each, alpha=alpha, start=start_921, end=end_921, num_of_channel=num_of_channel, furui_num=1)
    plt.show()

    ##########################
    #ふるい結果②
    print('#'*20)
    print('4/15')
    start_415 = '2018-04-15 0:00'
    end_415 = '2018-04-28 0:00'

    disp_sediment_distribution(df=df, df_qcalc=df_qcalc, qcalc_each=qcalc_each, alpha=alpha, start=start_415, end=end_415, num_of_channel=num_of_channel, furui_num=2)
    plt.show()

    ##########################
    #ふるい結果3    
    print('#'*20)
    print('4/15')
    start_716 = '2018-05-01 0:00'
    end_716 = '2018-05-20 0:00'

    disp_sediment_distribution(df=df, df_qcalc=df_qcalc, qcalc_each=qcalc_each, alpha=alpha, start=start_716, end=end_716, num_of_channel=num_of_channel, furui_num=3)
    plt.show()

    ##########################


def qcalc_each_method2(df_qcalc, start=None, end=None):
    if start== None:
        start = str(df_qcalc.axes[0][0])
    else:
        pass

    if end == None:
        end = str(df_qcalc.axes[0][0])
    else:
        pass

    qcalc_sum = df_qcalc[start:end].sum()
    
    return qcalc_sum


