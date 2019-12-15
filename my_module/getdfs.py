import pandas as pd
import numpy as np
import os

#自作モジュール
import dispgraphs

###########################################################

length_hp_m = 0.3 # ピット直上ハイドロフォン長さ
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

# data_path = os.getcwd()[:-len('notebook')] + 'data\\'
data_path = os.path.abspath(__file__)[:-len('my_module/getdfs.py')] + 'data\\'


###########################################################

def get2018original(unit='m'):
    """
    2018年のデータを読み込んで繋げる
    unit:mの場合、ハイドロフォンデータとピットデータを/mに変換する
    """
    # インデックスをTIMESTANPに設定し，時系列データとして読み込む(index_col='TIMESTAMP', parse_dates=True)
    df01 = pd.read_csv(data_path + 'logger1_2018-03-13_2018-12-16_every1min_withoutRainfall_WL_Velocity.csv',
                       index_col='TIMESTAMP', parse_dates=True)
    df02 = pd.read_csv(data_path + 'logger2_2018-03-13_2018-12-16_every1min_withoutRainfall_WL_Velocity.csv',
                       index_col='TIMESTAMP', parse_dates=True)
    df03 = pd.read_csv(data_path + 'logger3_2018-03-20_2018-12-16_every1min_withoutRainfall_WL_Velocity.csv',
                       index_col='TIMESTAMP', parse_dates=True)
    df04 = pd.read_csv(data_path + 'Precipitation_WL_Velocity201801to201812_every_1min.csv',
                       index_col='TIMESTAMP', parse_dates=True)
    # print(df01,df02,df03,df04)

    df_2018 = pd.concat([df01, df02, df03, df04], axis=1, sort=False)

    #ピット内の差分値をとった特徴量を増やす
    df_2018['Load_Avg_difference'] = df_2018['Load_Avg'].diff()

    if unit=="m":
         colnames_of_RRCCLCL = names_of_R + names_of_RC + names_of_C + names_of_LC + names_of_L

         df_2018[names_of_center] = df_2018[names_of_center]/length_hp_m
         df_2018[colnames_of_RRCCLCL] = df_2018[colnames_of_RRCCLCL]/length_C_m
         df_2018['Load_Avg_difference'] = df_2018['Load_Avg_difference']/pit_width       
    else:
        pass

    return df_2018

def get2017original(unit='m'):
    """
    2017年のデータを読み込こむ
    unit:mの場合、ハイドロフォンデータとピットデータを/mに変換する
    """
    df_2017 = pd.read_csv(data_path + 'Fukadani201607to201711.csv',
                          index_col='TIMESTAMP', parse_dates=True)
    
    #ピット内の差分値をとった特徴量を増やす
    df_2017['Load_Avg_difference'] = df_2017['Load_Avg'].diff()

    if unit=="m":
        df_2017[names_of_center] = df_2017[names_of_center]/length_hp_m
        df_2017['Load_Avg_difference'] = df_2017['Load_Avg_difference']/pit_width   

    else:
        pass

    return df_2017

def get2015intermittent(unit='m'):
    """
    2015年のデータを読み込こむ。このデータは途切れ途切れ
    unit:mの場合、ハイドロフォンデータとピットデータを/mに変換する
    """
    df_2015 = pd.read_csv(data_path + 'Fukadani2015_some_events.csv',
                          index_col='TIMESTAMP', parse_dates=True)

    #ピット内の差分値をとった特徴量を増やす
    df_2015['Load_Avg_difference'] = df_2015['Load_Avg'].diff()
    
    if unit=="m":
        df_2015[names_of_center] = df_2015[names_of_center]/length_hp_m
        df_2015['Load_Avg_difference'] = df_2015['Load_Avg_difference']/pit_width       

    else:
        pass

    return df_2015
    
def get_furui():
    df_furui= pd.read_csv(data_path + 'furui_results.csv', index_col='TIMESTAMP', parse_dates=True)
    return df_furui


def make_dataframe_diff_of_slots(df):
    """
    あとのget2018method2とget2017method2のための関数
    """
    # name[1]にはスロット１のデータ、name[2]には、スロット２のデータ、name[3]に、、、が入っている
    names = [0]*10
    for j in range(1, 11):
        names[j-1] = [i for i in df.columns if '({})'.format(j) in i]
    # （スロット１のデータ）−（スロット２のデータ）、（スロット２のデータ）－（スロット３のデータ）、、、としていき、
    # 粒径ごとのデータに分類する
    df_dia = [0]*10
    for i in range(1, 10):
        df_dia[i-1] = df[names[i-1]] - df[names[i]].values
    df_dia[9] = df[names[-1]]

    # 全てのデータを繋げる
    df_dia_all = pd.DataFrame()
    for i in range(1, 10):
        df_dia_all = pd.concat([df_dia_all, df_dia[i-1]], axis=1)
    df_dia_all = pd.concat([df_dia_all, df_dia[-1]], axis=1)
    
    df_dia_all['Load_Avg'] = df['Load_Avg']
    df_dia_all['Load_Avg_difference'] = df['Load_Avg_difference']
    
    #'WL_FMR_Avg'と'WaterLevel(cm)'は違う計測器で水深を測っているよう（要確認）で、
    #scatter graphで見ると値が１：１になった。そのため、'WL_FMR_Avg'を使っている。
    df_dia_all['WaterLevel(cm)'] = df['WL_FMR_Avg']

    df_dia_all['Velocity(m/s)'] = df['vel_P_Tot']
    print("I used the 'vel_P_Tot' data as velocity. I'm not pretty sure if it's the surface vel or mean vel. You have to make sure what this vel means. You also have to know that from 2018 data, there's another velocity data called 'Velocity(m/s). You might wanna know what's the difference between these 2.")


    return df_dia_all

def get2018method2(unit="m"):
    """
    """
    df_2018 = get2018original(unit=unit)
    df_2018_dia = make_dataframe_diff_of_slots(df_2018)

    return df_2018_dia

def get2017method2(unit="m"):
    df_2017 = get2017original(unit=unit)
    df_2017_dia = make_dataframe_diff_of_slots(df_2017)

    return df_2017_dia

def get2015method2(unit="m"):
    df_2015 = get2015intermittent(unit=unit)
    df_2015_dia = make_dataframe_diff_of_slots(df_2015)

    return df_2015_dia

###########################################################

def clean2018data(df_2018):
        # 2018年データの整理
    # 4/28、7/26 9/4-6 9/23にピット掃除をしていそうだったのでデータを全部削除
    # データに異常がみられる3/26,4/18を削除
    # イベントがなく、じわじわピット内流砂が減少していた10/4以降を削除
    sidxs = []
    eidxs = []

    sidxs.append('2018-04-28 0:00')
    eidxs.append('2018-04-29 0:00')

    sidxs.append('2018-07-16 0:00')
    eidxs.append('2018-07-17 0:00')

    sidxs.append('2018-09-04 0:00')
    eidxs.append('2018-09-06 0:00')

    sidxs.append('2018-09-23 0:00')
    eidxs.append('2018-09-24 0:00')

    sidxs.append('2018-03-26 0:00')
    eidxs.append('2018-03-27 0:00')

    sidxs.append('2018-04-18 0:00')
    eidxs.append('2018-04-19 0:00')

    sidxs.append('2018-10-04 0:00')
    eidxs.append(df_2018.index[-1])


    #df_dia_all_2018とdf_2018両方から削除
    for sidx, eidx in zip(sidxs, eidxs):
        drop_date_range = pd.date_range(sidx, eidx, freq='min')
        drop_date_range = drop_date_range & df_2018.index
        df_2018 = df_2018.drop(drop_date_range)
    
    return df_2018


def get2018cleaned(unit="m"):
    df_2018_ori = get2018original(unit=unit)
    df_2018_cleaned = clean2018data(df_2018_ori)

    return df_2018_cleaned

def get2018method2cleaned(unit="m"):
    df_2018_method2 = get2018method2(unit="m")
    df_2018_method2_cleaned = clean2018data(df_2018_method2)

    return df_2018_method2_cleaned

def clean2017data(df_2017):
    # ２０１７年データの整理
    # ピット掃除をしていそうだったのでデータを全部削除
    sidxs = []
    eidxs = []

    sidxs.append("2016-10-1 0:00")
    eidxs.append('2016-10-2 0:00')

    sidxs.append("2017-11-23 0:00")
    eidxs.append('2017-12-24 0:00')

    sidxs.append("2017-5-19 0:00")
    eidxs.append('2017-05-20 0:00')

    sidxs.append("2017-07-08 0:00")
    eidxs.append('2017-07-09 0:00')
            
    sidxs.append("2017-8-19 0:00")
    eidxs.append('2017-08-20 0:00')

    #エラーが多い時期を削除(Load_Avg_differenceがジグザグなところ)


    sidxs.append("2016-10-31 0:00")
    eidxs.append('2016-12-30 0:00')

    sidxs.append("2017-08-25 0:00")
    eidxs.append('2017-09-21 0:00')


    sidxs.append(df_2017.index[0])
    eidxs.append("2016-06-3 0:00")
      
    # sidxs.append('2018-10-04 0:00')
    # eidxs.append(df_all.index[-1])


    for sidx, eidx in zip(sidxs, eidxs):
        drop_date_range = pd.date_range(sidx, eidx, freq='min')
        drop_date_range = drop_date_range & df_2017.index
        df_2017 = df_2017.drop(drop_date_range)

    return df_2017

def get2017cleaned(unit="m"):
    df_2017_ori = get2017original(unit=unit)
    df_2017_cleaned = clean2017data(df_2017_ori)

    return df_2017_cleaned

def get2017method2cleaned(unit="m"):
    df_2017_method2 = get2017method2(unit="m")
    df_2017_method2_cleaned = clean2017data(df_2017_method2)

    return df_2017_method2_cleaned

###########################################################

def mean_of_df(df, meantime=30):
    """
    dfを３０分間隔平均にする。
    （'Load_Avg'と'Load_Avg_difference'は平均間隔にするとおかしくなるのでしない）
    """
    sum_interval = meantime
    df_mean = df.resample('{}T'.format(sum_interval)).sum() / sum_interval
    df_mean['Load_Avg'] = df['Load_Avg']
    df_mean['Load_Avg_difference'] = df['Load_Avg_difference'].resample(
        '{}T'.format(sum_interval)).sum() / sum_interval
    
    return df_mean

def get2018cleanedmean(meantime=30):
    """
    2018cleanedのmean
    """
    df_2018_cleaned = get2018cleaned(unit="m")
    df_2018_mean = mean_of_df(df_2018_cleaned)
    return df_2018_mean

def get2018method2cleanedmean(meantime=30):
    """
    2018method2cleanedのmean
    """
    df_2018method2_cleaned = get2018method2cleaned(unit="m")
    df_2018method2_mean = mean_of_df(df_2018method2_cleaned)
    return df_2018method2_mean

def get2017cleanedmean(meantime=30):
    df_2017_cleaned = get2017cleaned(unit="m")
    df_2017_mean = mean_of_df(df_2017_cleaned)
    return df_2017_mean


def get2017method2cleanedmean(meantime=30):
    df_2017method2_cleaned = get2017method2cleaned(unit="m")
    df_2017method2_mean = mean_of_df(df_2017method2_cleaned)
    return df_2017method2_mean


def get2015mean(meantime=30):
    df_2015 = get2015intermittent(unit="m")
    df_2015_mean = mean_of_df(df_2015)
    return df_2015_mean

def get2015method2mean(meantime=30):
    df_2015method2 = get2015method2(unit="m")
    df_2015method2_mean = mean_of_df(df_2015method2)
    return df_2015method2_mean



###########################################################

def drop_untrusted_pit_data(df, min_pit, max_pit):
    """
    Load_Avg(ピット内)が200kg以上1000kg以下のデータのみを抽出
    """
    df_dropped = df[(df['Load_Avg'] > min_pit)&(df['Load_Avg'] < max_pit)]
    return df_dropped

def get2017cleanedmean_pit_true(min_pit=200, max_pit=1000):
    df_2017 = get2017cleanedmean()
    df_2017_truepit = drop_untrusted_pit_data(df_2017, min_pit=min_pit, max_pit= max_pit)
    return df_2017_truepit

def get2017method2cleanedmean_pit_true(min_pit=200, max_pit=1000):
    df_2017method2 = get2017method2cleanedmean()
    df_2017method2_truepit = drop_untrusted_pit_data(df_2017method2, min_pit=min_pit, max_pit= max_pit)
    return df_2017method2_truepit

def get2018cleanedmean_pit_ture(min_pit=200, max_pit=1000):
    df_2018 = get2018cleanedmean()
    df_2018_truepit = drop_untrusted_pit_data(df_2018, min_pit=min_pit, max_pit= max_pit)
    return df_2018_truepit

def get2018method2cleanedmean_pit_ture(min_pit=200, max_pit=1000):
    df_2018method2 = get2018method2cleanedmean()
    df_2018method2_truepit = drop_untrusted_pit_data(df_2018method2, min_pit=min_pit, max_pit= max_pit)
    return df_2018method2_truepit  

def get2015mean_pit_true(min_pit=200, max_pit=1000):
    df_2015 = get2015mean()
    df_2015_truepit = drop_untrusted_pit_data(df_2015, min_pit=min_pit, max_pit= max_pit)
    return df_2015_truepit

def get2015method2mean_pit_true(min_pit=200, max_pit=1000):
    df_2015method2 = get2015method2mean()
    df_2015method2_truepit = drop_untrusted_pit_data(df_2015method2, min_pit=min_pit, max_pit= max_pit)
    return df_2015method2_truepit

###########################################################
#2018年の綺麗な３つのデータのみ取得、リストで返す

def get2018_3events_original():
    df_2018_original = get2018original()
    list_df2018_events = [0]*3

    list_df2018_events[0] = df_2018_original['2018-04-15 0:00': '2018-04-16 0:00']
    list_df2018_events[1] = df_2018_original['2018-09-08 0:00': '2018-09-08 8:00']
    list_df2018_events[2] = df_2018_original['2018-09-30 21:00': '2018-10-1 6:00']

    return list_df2018_events

def get2018_3events_mean(meantime=30):
    df_2018_mean = get2018cleanedmean_pit_ture()
    list_df2018_events = [0]*3

    list_df2018_events[0] = df_2018_mean['2018-04-15 0:00': '2018-04-16 0:00']
    list_df2018_events[1] = df_2018_mean['2018-09-08 0:00': '2018-09-08 8:00']
    list_df2018_events[2] = df_2018_mean['2018-09-30 21:00': '2018-10-1 6:00']

    return list_df2018_events


def get2018_3events_method2():
    df_2018_method2 = get2018method2cleaned()
    list_df2018mthod2_events = [0]*3

    list_df2018mthod2_events[0] = df_2018_method2['2018-04-15 0:00': '2018-04-16 0:00']
    list_df2018mthod2_events[1] = df_2018_method2['2018-09-08 0:00': '2018-09-08 8:00']
    list_df2018mthod2_events[2] = df_2018_method2['2018-09-30 21:00': '2018-10-1 6:00']

    return list_df2018mthod2_events

def get2018_3events_method2_mean(meantime=30):
    df_2018_method2_mean = get2018method2cleanedmean_pit_ture()
    list_df2018mthod2_events_mean = [0]*3

    list_df2018mthod2_events_mean[0] = df_2018_method2_mean['2018-04-15 0:00': '2018-04-16 0:00']
    list_df2018mthod2_events_mean[1] = df_2018_method2_mean['2018-09-08 0:00': '2018-09-08 8:00']
    list_df2018mthod2_events_mean[2] = df_2018_method2_mean['2018-09-30 21:00': '2018-10-1 6:00']
    

    return list_df2018mthod2_events_mean

###########################################################
#2017年の綺麗なデータのみ取得、リストで返す

start_time_2017 = ["2016-06-25 0:00", '2016-07-05 0:00', '2016-07-31 0:00', '2016-08-08 0:00', '2016-10-03 0:00', '2017-07-01 0:00', '2017-07-10 0:00', '2017-09-22 0:00']
end_time_2017 = ["2016-06-25 12:00", '2016-07-16 0:00', '2016-08-3 0:00', '2016-09-01 0:00', '2016-10-31 0:00', '2017-07-02 18:00', '2017-08-15 0:00', '2017-9-28 0:00']

# ["2016-06-25 0:00": "2016-06-25 12:00"]
# ['2016-07-05 0:00': '2016-07-16 0:00']
# ['2016-07-31 0:00': '2016-08-3 0:00']
# ['2016-08-08 0:00': '2016-09-01 0:00']
# ['2016-10-03 0:00': '2016-10-31 0:00'] #ピット内重量がギザギザしてる。木などがひっかかって流砂が上手く取り込めていない可能性あり
# ['2017-07-01 0:00': '2017-07-02 18:00']
# ['2017-07-10 0:00': '2017-08-15 0:00'] #他のイベントに比べ期間が長い
# ['2017-09-22 0:00': '2017-9-28 0:00']

def get2017_8events_original():
    df_2017_original = get2017original()
    num_of_events = len(start_time_2017)
    list_df2017_events = [0]*num_of_events

    for i in range(num_of_events):
        list_df2017_events[i] = df_2017_original[start_time_2017[i]:end_time_2017[i]]

    return list_df2017_events

def get2017_8events_mean(meantime=30):
    df_2017_mean = get2017cleanedmean_pit_true()
    num_of_events = len(start_time_2017)
    list_df2017_events = [0]*num_of_events

    for i in range(num_of_events):
        list_df2017_events[i] = df_2017_mean[start_time_2017[i]:end_time_2017[i]]

    return list_df2017_events


def get2017_8events_method2():
    df_2017_method2 = get2017method2cleaned()
    num_of_events = len(start_time_2017)
    list_df2017_events = [0]*num_of_events

    for i in range(num_of_events):
        list_df2017_events[i] = df_2017_method2[start_time_2017[i]:end_time_2017[i]]


    return list_df2017_events

def get2017_8events_method2_mean(meantime=30):
    df_2017_method2_mean = get2017method2cleanedmean_pit_true()
    num_of_events = len(start_time_2017)
    list_df2017_events = [0]*num_of_events

    for i in range(num_of_events):
        list_df2017_events[i] = df_2017_method2_mean[start_time_2017[i]:end_time_2017[i]]    

    return list_df2017_events

###########################################################

###########################################################
#指定日時のデータのみ取得


###########################################################
# 飽和していないデータのみを算出。飽和している部分はNaNで渡す
# このコードめっちゃ適当に書いて頭悪い(ちゃんと動くけど)から
# もっとスマートにできるなら改良してほしい
def get_nosaturated_df(df):
    '''
    df:method2形式のdfを。
    
    もし基準値がNanの場合は、その時間のデータ全て使わない
    '''
    #増加量((A - B) / Bで変化率を算出する。)
    df_increment = df.pct_change()

    # inf を NaNに変換
    df_increment.replace([np.inf, -np.inf], np.nan)
    
    threshold = 0
    
    # Tot(10)が50以下の時はTot(6)とTot(7)を信頼する
    # Tot(10)が50以上の時はTot(9)とTot(10)を信頼する

    df_bool_large_tot10 = df_increment[df['hp_Tot(10)'] > 50]
    # df_large_tot10 = df[df['hp_Tot(10)'] > 50]

    df_bool_small_tot10 = df_increment[df['hp_Tot(10)'] <= 50]
    # df_small_tot10 = df[df['hp_Tot(10)'] <= 50]
    
    #largeの時は判断にTot(10)とTot(9)を使う

    df_bool = pd.DataFrame() #最終的に必要なデータのみをTrueとしたboolean

    for i in range(len(df_bool_large_tot10)):
        df_now = df_bool_large_tot10[i:i+1]
        sign = float((df_now['hp_Tot(10)']+df_now['hp_Tot(9)'])/2)

        if sign > threshold:
            #each_bool : 1 row DataFrame
            each_bool = df_now > threshold 
            df_bool = pd.concat([df_bool, each_bool])

        if sign <= threshold:
            each_bool = df_now <= threshold
            df_bool = pd.concat([df_bool, each_bool])

    for i in range(len(df_bool_small_tot10)):
        df_now = df_bool_small_tot10[i:i+1]
        sign = float((df_now['hp_Tot(6)']+df_now['hp_Tot(7)'])/2)

        if sign > threshold:
            #each_bool : 1 row DataFrame
            each_bool = df_now > threshold
            df_bool = pd.concat([df_bool, each_bool])

        elif sign <= threshold:
            each_bool = df_now <= threshold
            df_bool = pd.concat([df_bool, each_bool], sort=False)

        else: #sign = nanの時は全てFalse
            df_now.loc[:,:] = [False]*len(df_now.columns)
            df_bool = pd.concat([df_bool, df_now[:]], sort=False)

    #時間通りに並び替え
    df_bool = df_bool.sort_index()
    # print(df_bool)
    #左からFalse, False, False...ときてTureになりまたFalseになったときのFalseはTrueに変換
    #(つまり、低倍率/7~10チャンネルは常時Trueにする)
    colnames = list(df_bool.columns)
    df_corrected = pd.DataFrame()
    for i in range(len(df_bool)):
        df_row = df_bool[i:i+1]

    #     now = 
        # count_true = 0
        j_hold = 0
        #一列毎に見て、Trueをみつけたらそれよりも右を全部Trueに
        for j, colname in enumerate(colnames):
            if bool(df_row[colname][0]):
                #特に意味は無いが、分かりやすくここで何番目のカラムかを保持
                j_hold = j
                break

        #i番目よりも右側のカラム名を取得
        true_colnames = colnames[j_hold:]
        #i番目よりも右側のカラムを全てTrueに
        df_row.loc[:,j_hold:] = [True]*len(true_colnames)
        df_corrected = df_corrected.append(df[i:i+1][df_row[:]], sort=False)


    #グラフに表示(青：original,　オレンジ：判定後Trueのみ)
    axes = dispgraphs.scatter_graphs(df, list_y_names=names_of_center, list_x_names=['Load_Avg_difference']*10
                             ,figsize=(3*4, 3*3), alpha=0.3)
    dispgraphs.scatter_graphs(df_corrected, list_y_names=names_of_center, list_x_names=['Load_Avg_difference']*10
                             ,figsize=(3*4, 3*3), alpha=0.3, overlap=True, axes=axes)
    
    return df_corrected


###########################################################


if __name__ == "__main__":
    df_2018 = get2018cleanedmean_pit_ture()
    df2018_corrected = get_nosaturated_df(df_2018)