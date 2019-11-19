import pandas as pd
import numpy as np
import os

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

