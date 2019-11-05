import pandas as pd
import os

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
    else:
        pass

    return df_2017


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

###########################################################
#指定日時のデータのみ取得


###########################################################