import pandas as pd
import numpy as np
import os
import math

from logging import getLogger, StreamHandler, DEBUG, INFO, WARNING
from scipy.optimize import minimize

#自作モジュール
import dispgraphs
import getdfs
import sklardietrich

#############
#ログ設定
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(INFO)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False
#############
###########################################################

W_IDEAL = np.array([0.15, 0.22, 0.29, 0.65, 0.91, 1.96, 3.01, 6.91, 10.81, 50])*0.001

length_hp_m = 0.275 #m ピット直上ハイドロフォン長さ
length_C_m = 0.5 #m 5本の真ん中ハイドロフォン長さ
pit_width = 0.2 #mピット流入口長さ

bump_hp_m = 0.025 #m

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

data_path = os.getcwd()[:-len('my_module')] + 'data\\'

UNIT = 'cm'

if UNIT == 'cm':
    ##初期値m, g
    rho = 1 #g/cm3
    grav = 980 #cm/s**2
    ib = 1/20 #? パーセント？角度？
    s = 1.65
    width = 500#m
    sigma_by_rho = 2.65
    rho_s = 2.65 #g/cm**3
    Rb = s #? 砂礫の水中比重
    # W_IDEAL = np.array([0.15, 0.22, 0.29, 0.65, 0.91, 1.96, 3.01, 6.91, 10.81, 50]) #g
    # D_IDEAL = 2*((W_IDEAL/rho_s)*(3/4)*(1/math.pi))**(1/3)

    bump_hp_m = 0.025 * 100 #cm


###########################################################

#時間があればTensorflowで書きたい！

def organize_dfs(df_optimize, names_of_cols, df_waterlevel, df_qobs):
    '''
    df_optimize : 綺麗なデータ。マイナスデータ等を除外してからの方が良い
    df_waterlevel : df_optimizeに対応したwaterlevel これも綺麗なデータのみを使う
    
    '''
        # 目的関数(Tot(５)以上)
    if len(df_optimize.columns) == len(names_of_cols):
        logger.debug('{}'.format(len(df_optimize.columns)))
        logger.debug('{}'.format(len(names_of_cols)))
        #チャンネル数を保持
        channel_num = len(df_optimize.columns)
        
        logger.debug('Use cols are {}. The number of use cols is {}'.format(names_of_cols, channel_num))

    else:
        logger.error('The number of columns of df_optimize and the number of names_of_cols should be matched')

    #columnsの順番を揃える
    df_optimize = df_optimize[names_of_cols]

    #df_waterlevelの異常値を削除
    #水深2cm以下は削除
    df_waterlevel = df_waterlevel[df_waterlevel>2]
    #水深20cm以上は削除
    df_waterlevel = df_waterlevel[df_waterlevel<20]

    #df_optimizeとdf_waterlevelを結合してお互いにNaNがある部分を消去→再分離する
    df_concat = pd.concat([df_optimize, df_waterlevel, df_qobs], axis=1)
    #NANが一つでもあれば削除
    df_concat = df_concat.dropna(how='all')

    #再分離
    df_optimize = df_concat[names_of_cols]
    df_waterlevel = df_concat[str(df_waterlevel.name)]
    df_qobs = df_concat[str(df_qobs.name)]

    return df_optimize, df_waterlevel, df_qobs


def repeat_opt_func(func, repeat, cons):

    temp = 1000000000 
    results = []
    for i in range(repeat):
        Const0 = np.append(np.random.rand(6), 2)# 初期値は適当
        result = minimize(func, x0=Const0, constraints=cons, method="COBYLA")
        if result.fun < temp:
            results.append(result)
            temp = result.fun
            print('func : ', temp)
            print('x : ', result.x)
        
    return results



# defの名前の説明
# optimizeの後に、定数となるものを書いている
def optimize_const_alpha_gamma_optbeta_c(df_optimize, names_of_cols, W_IDEAL, D_IDEAL, df_waterlevel, df_qobs, alpha=0.3, gamma = 0.5, repeat=10):
    '''
    df_optimize : 綺麗なデータ。マイナスデータ等を除外してからの方が良い
    df_waterlevel : df_optimizeに対応したwaterlevel これも綺麗なデータのみを使う
    '''

    #チャンネルに対応するWを保持


    #dfを整理
    df_optimize, df_waterlevel, df_qobs = organize_dfs(df_optimize, names_of_cols, df_waterlevel, df_qobs)

    def func(Const):
        '''
        ここに最小化するコスト関数を設定する。
        コスト関数をreturnで返す
        Const[:-1]: beta
        Const[-1] : C 
        '''
        f_n = 1

        df_w = df_optimize.mul(W_IDEAL.reshape(1,len(W_IDEAL))).mul(Const[:-1].reshape(1,len(W_IDEAL)))
        df_w_sum = df_w.sum(axis=1)
        df_qcalc = df_w_sum * (Const[-1]/(f_n*alpha*gamma))
    #     cost = np.abs(df_qcalc-df_all_plus['Load_Avg_difference'])
        cost = np.square(df_qcalc-df_qobs)
    #     cost = np.sqrt(np.abs(df_qcalc-df_all_plus['Load_Avg_difference']))
    #     cost = np.log(np.abs(np.log1p(df_qcalc)-np.log1p(df_all_plus['Load_Avg_difference'])))

        Cost = cost.sum()
        return Cost

    def output_result_of_func():
        """
        Const[0]-Const[5] : beta1-beta6
        Const[6] : gamma
        Const[7] (if it exist) : alpha
        
        """
        error_less = 0.8
        error_more = 1.2
        
        cons = (
                {'type': 'ineq', 'fun': lambda Const: Const[0]-error_less},
                {'type': 'ineq', 'fun': lambda Const: -Const[0]+error_more},
                {'type': 'ineq', 'fun': lambda Const: Const[1]-error_less},
                {'type': 'ineq', 'fun': lambda Const: -Const[1]+error_more},
                {'type': 'ineq', 'fun': lambda Const: Const[2]-error_less},
                {'type': 'ineq', 'fun': lambda Const: -Const[2]+error_more},
                {'type': 'ineq', 'fun': lambda Const: Const[3]-error_less},
                {'type': 'ineq', 'fun': lambda Const: -Const[3]+error_more},
                {'type': 'ineq', 'fun': lambda Const: Const[4]-error_less},
                {'type': 'ineq', 'fun': lambda Const: -Const[4]+error_more},
                {'type': 'ineq', 'fun': lambda Const: Const[5]-error_less},
                {'type': 'ineq', 'fun': lambda Const: -Const[5]+error_more},

                {'type': 'ineq', 'fun': lambda Const:  Const[6]},
                # {'type': 'ineq', 'fun': lambda Const:  1-Const[6]},
                
                {'type': 'ineq', 'fun': lambda Const: Const[1]*W_IDEAL[1] - Const[0]*W_IDEAL[0]},
                {'type': 'ineq', 'fun': lambda Const: Const[2]*W_IDEAL[2] - Const[1]*W_IDEAL[1]},
                {'type': 'ineq', 'fun': lambda Const: Const[3]*W_IDEAL[3] - Const[2]*W_IDEAL[2]},
                {'type': 'ineq', 'fun': lambda Const: Const[4]*W_IDEAL[4] - Const[3]*W_IDEAL[3]},
                {'type': 'ineq', 'fun': lambda Const: Const[5]*W_IDEAL[5] - Const[4]*W_IDEAL[4]},
                
                )
        #optimize cost function
        results = repeat_opt_func(func, repeat, cons)
        return results[-1]

    Correction_factor = output_result_of_func()
    
    return Correction_factor 


# optimizeの後に、定数となるものを書いている
def optimize_const_alpha_nconst_gamma_optbeta_c(df_optimize, names_of_cols, W_IDEAL, df_waterlevel, df_qobs, alpha=0.3, gamma = 0.5, repeat=10):
    '''
    df_optimize : 綺麗なデータ。マイナスデータ等を除外してからの方が良い
    df_waterlevel : df_optimizeに対応したwaterlevel これも綺麗なデータのみを使う
    '''

    #sklardietrichからgammaを計算。あとで使用
    def calc_gamma(list_h_s, bump_hp_m):
        list_gamma = []
        for h_s in list_h_s:
            if np.isnan(h_s):
                gamma = 1
                list_gamma.append(gamma)

            elif h_s <= bump_hp_m:
                gamma = 1
                list_gamma.append(gamma)

            else:
                gamma = bump_hp_m/h_s
                list_gamma.append(gamma)
        
        return list_gamma 
    #チャンネルに対応するWを保持


    #dfを整理
    df_optimize, df_waterlevel, df_qobs = organize_dfs(df_optimize, names_of_cols, df_waterlevel, df_qobs)

    f_n = 1
    D_IDEAL = 2*((W_IDEAL/rho_s)*(3/4)*(1/math.pi))**(1/3)
    logger.debug('D_IDEAL : {}'.format(D_IDEAL))

    #calc gamma by sklardietrich
    list2d_gamma = [] 
    for waterlevel in df_waterlevel:
        R = sklardietrich.calc_R(waterlevel, width)
        list_h_s = [sklardietrich.calc_h_s(R=R, d=D_IDEAL[i]) for i in range(len(D_IDEAL))]
            
        #gammaを計算
        list_gamma = calc_gamma(list_h_s, bump_hp_m)
        logger.debug('list_gamma : {}'.format(list_gamma))
        list2d_gamma.append(list_gamma)
        
        #gammaをdfに格納する。その際のcolumns名を作成
        # colnames_gamma = ['gamma_{}'.format(names_of_cols[i]) for i in range(len(names_of_cols))]
        #dfに変換
        # df_gamma = pd.DataFrame(list2d_gamma, index=df_waterlevel.index, columns=colnames_gamma)
        # print(df_gamma)
        # print(df_optimize)

    df_gamma_by_optimize = df_optimize / np.array(list2d_gamma)

    def func(Const):
        '''
        ここに最小化するコスト関数を設定する。
        コスト関数をreturnで返す
        Const[:-1]: beta
        Const[-1] : C 
        '''
        df_w = df_gamma_by_optimize.mul(W_IDEAL.reshape(1,len(W_IDEAL))).mul(Const[:-1].reshape(1,len(W_IDEAL)))
        df_w_sum = df_w.sum(axis=1)
        df_qcalc = df_w_sum * (Const[-1]/(f_n*alpha*gamma))
    #     cost = np.abs(df_qcalc-df_all_plus['Load_Avg_difference'])
        cost = np.square(df_qcalc-df_qobs)
    #     cost = np.sqrt(np.abs(df_qcalc-df_all_plus['Load_Avg_difference']))
    #     cost = np.log(np.abs(np.log1p(df_qcalc)-np.log1p(df_all_plus['Load_Avg_difference'])))
        Cost = cost.sum()
        return Cost

    def output_result_of_func():
        """
        Const[0]-Const[5] : beta1-beta6
        Const[6] : gamma
        Const[7] (if it exist) : alpha
        
        """
        error_less = 0.7
        error_more = 1.3
        
        cons = (
                {'type': 'ineq', 'fun': lambda Const: Const[0]-error_less},
                {'type': 'ineq', 'fun': lambda Const: -Const[0]+error_more},
                {'type': 'ineq', 'fun': lambda Const: Const[1]-error_less},
                {'type': 'ineq', 'fun': lambda Const: -Const[1]+error_more},
                {'type': 'ineq', 'fun': lambda Const: Const[2]-error_less},
                {'type': 'ineq', 'fun': lambda Const: -Const[2]+error_more},
                {'type': 'ineq', 'fun': lambda Const: Const[3]-error_less},
                {'type': 'ineq', 'fun': lambda Const: -Const[3]+error_more},
                {'type': 'ineq', 'fun': lambda Const: Const[4]-error_less},
                {'type': 'ineq', 'fun': lambda Const: -Const[4]+error_more},
                {'type': 'ineq', 'fun': lambda Const: Const[5]-error_less},
                {'type': 'ineq', 'fun': lambda Const: -Const[5]+error_more},

                {'type': 'ineq', 'fun': lambda Const:  Const[6]},
                # {'type': 'ineq', 'fun': lambda Const:  1-Const[6]},
                
                {'type': 'ineq', 'fun': lambda Const: Const[1]*W_IDEAL[1] - Const[0]*W_IDEAL[0]},
                {'type': 'ineq', 'fun': lambda Const: Const[2]*W_IDEAL[2] - Const[1]*W_IDEAL[1]},
                {'type': 'ineq', 'fun': lambda Const: Const[3]*W_IDEAL[3] - Const[2]*W_IDEAL[2]},
                {'type': 'ineq', 'fun': lambda Const: Const[4]*W_IDEAL[4] - Const[3]*W_IDEAL[3]},
                {'type': 'ineq', 'fun': lambda Const: Const[5]*W_IDEAL[5] - Const[4]*W_IDEAL[4]},
                
                )
        #optimize cost function
        results = repeat_opt_func(func, repeat, cons)
        logger.info('result : {}'.format(results[-1]))
        return results[-1]

    Correction_factor = output_result_of_func()
    logger.info('Correction_factor : {}'.format(Correction_factor))
    
    return Correction_factor 


#########################
if __name__ == "__main__":

    names_of_cols = names_of_center[4:]
    W_IDEAL = W_IDEAL[4:]
    # D_IDEAL = D_IDEAL[4:]
    logger.debug('{}'.format(names_of_cols))
    df_2017 = getdfs.get2017method2cleanedmean_pit_true()

    df_optimize = df_2017[names_of_cols]
    df_waterlevel = df_2017['WaterLevel(cm)']
    df_qobs = df_2017['Load_Avg_difference']

    Correction_factor = optimize_const_alpha_nconst_gamma_optbeta_c(df_optimize, names_of_cols, W_IDEAL, df_waterlevel, df_qobs, alpha=0.3, gamma=0.5)
    print(Correction_factor)


