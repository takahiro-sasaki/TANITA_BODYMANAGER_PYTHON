# coding: utf-8

import os
import argparse
import pandas as pd
import matplotlib as mpl 
import matplotlib.pyplot as plt

mpl.rcParams['font.family'] = 'IPAexGothic'

parser = argparse.ArgumentParser(description='Generate body conditions\' transition diagrams')
parser.add_argument('-s', '--source', metavar='S', type=str, 
                    default='./GRAPHV1/DATA/DATA1.CSV',
                    help='path to the data source file (default=\'./GRAPHV1/DATA/DATA1.CSV\')')
parser.add_argument('-g', '--granularities', metavar='G', nargs='+', 
                    default=['weekly'], 
                    help='granularities (default = \'weekly\' ; other possible options are \'daily\' and \'monthly\')')
parser.add_argument('-i', '--items', metavar='I', nargs='+', 
                    default=['体重(kg)', '全身体脂肪率(％)', '全身筋肉量(kg)', '推定骨量(kg)', '基礎代謝量(kcal／日)', '体水分率(％)'], 
                    help='items to be output (default = \'体重(kg)\', \'全身体脂肪率(％)\', \'全身筋肉量(kg)\', \'推定骨量(kg)\', \'基礎代謝量(kcal／日)\', \'体水分率(％)\' ; other possible options are  \'身長(cm)\', \'BMI\', \'右腕(皮下)脂肪率(％)\', \'左腕(皮下)脂肪率(％)\', \'右足(皮下)脂肪率(％)\', \'左足(皮下)脂肪率(％)\', \'体幹部脂肪率(％)\', \'右腕筋肉量(kg)\', \'左腕筋肉量(kg)\', \'右足筋肉量(kg)\', \'左足筋肉量(kg)\', \'体幹部筋肉量(kg)\', \'内臓脂肪(レベル)\', \'体内年齢(才)\') ; or \'none\' ')

args = parser.parse_args()
print(args)

raw_sheet_df = pd.read_csv(args.source,  header=None)

daily_output = './graph-daily'
weekly_output = './graph-weekly'
monthly_output = './graph-monthly'

# for col in range(len(raw_sheet_df.columns)):
#    print ('{}: {}'.format(str(col), raw_sheet_df.iloc[0,col]))

#13 Date
#15 Time
#23 身長(cm)
#25 体重(kg)
#27 BMI
#29 全身体脂肪率(％)
#31 右腕（皮下）脂肪率(％)
#33 左腕（皮下）脂肪率(％)
#35 右足（皮下）脂肪率(％)
#37 左足（皮下）脂肪率(％)
#39 体幹部脂肪率(％)
#51 全身筋肉量（kg)
#53 右腕筋肉量(kg)
#55 左腕筋肉量(kg)
#57 右足筋肉量(kg)
#59 左足筋肉量(kg)
#61 体幹部筋肉量(kg)
#75 推定骨量(kg)
#77 内臓脂肪（レベル）
#79 基礎代謝量（kcal/日）
#81 体内年齢(才)
#83 体水分率(％)


extracted_raw_df = raw_sheet_df[[13,15,23,25,27,29,31,33,35,37,39,51,53,55,57,59,61,75,77,79,81,83]]

col_name_table ={
    13: '年月日', 
    15:'時刻', 
    23: '身長(cm)',
    25: '体重(kg)',
    27: 'BMI',
    29: '全身体脂肪率(％)',
    31: '右腕(皮下)脂肪率(％)',
    33: '左腕(皮下)脂肪率(％)',
    35: '右足(皮下)脂肪率(％)',
    37: '左足(皮下)脂肪率(％)',
    39: '体幹部脂肪率(％)',
    51: '全身筋肉量(kg)',
    53: '右腕筋肉量(kg)',
    55: '左腕筋肉量(kg)',
    57: '右足筋肉量(kg)',
    59: '左足筋肉量(kg)',
    61: '体幹部筋肉量(kg)',
    75: '推定骨量(kg)',
    77: '内臓脂肪(レベル)',
    79: '基礎代謝量(kcal／日)',
    81: '体内年齢(才)',
    83: '体水分率(％)',
                }

renamed_raw_df = extracted_raw_df.rename(columns=col_name_table)
renamed_raw_df['年月日'] = pd.to_datetime(renamed_raw_df['年月日']) 


daily = renamed_raw_df.set_index('年月日').resample("D").mean()
weekly = renamed_raw_df.set_index('年月日').resample("W").mean()
monthly = renamed_raw_df.set_index('年月日').resample("M").mean()


print(daily.head(10))
print(weekly.head(10))
print(monthly.head(10))



granularities = []

if (args.granularities.count('daily')):
    granularities.append(daily)
if (args.granularities.count('weekly')):
    granularities.append(weekly)
if (args.granularities.count('monthly')):
    granularities.append(monthly)

if args.items == ['none']:
    items =[]
else:
    items = args.items

plt.rcParams['figure.figsize'] = [15, 10]

for itm in items:
    for gran in granularities:
        if gran is daily:
            title = '{} -- 日次'.format(itm)
            out_dir = daily_output
        elif gran is weekly:
            title = '{} -- 週平均'.format(itm)
            out_dir = weekly_output
        elif gran is monthly:
            title = '{} -- 月平均'.format(itm)
            out_dir = monthly_output   
    
        plt.plot(gran[itm])
        plt.title(title)

        os.makedirs(out_dir, exist_ok=True)
        plt.savefig('{}/{}.png'.format(out_dir, itm))
#        plt.show()
        plt.close()


pair = ['体重(kg)', '全身体脂肪率(％)']
for gran in granularities:
    
    if gran is daily:
        title = '{} : {} -- 日次'.format(pair[0], pair[1])
        out_dir = daily_output
    elif gran is weekly:
        title = '{} : {} -- 週平均'.format(pair[0], pair[1])
        out_dir = weekly_output
    elif gran is monthly:
        title = '{} : {} -- 月平均'.format(pair[0], pair[1])
        out_dir = monthly_output
        
    fig = plt.figure()
    plt.title(title)
    ax1 = fig.add_subplot(111)
    
    t = gran.index
 
    fs = 1.0
    y1 = gran[pair[0]]

    ln1=ax1.plot(t, y1,'C0', marker='o', label=pair[0])

    ax2 = ax1.twinx()
    y2 = gran[pair[1]]

    ln2=ax2.plot(t,y2,'C1', marker='o', label=pair[1])

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1+h2, l1+l2, loc='lower right')

    ax1.set_xlabel('年月日')
    ax1.set_ylabel(pair[0])
    ax1.grid(True)
    ax2.set_ylabel(pair[1])

    os.makedirs(out_dir, exist_ok=True)
    plt.savefig('{}/{}-{}.png'.format(out_dir, pair[0], pair[1]))
#    plt.show()
    plt.close()

