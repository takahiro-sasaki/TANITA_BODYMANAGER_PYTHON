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

parser.add_argument('--no_errorbars', help='if you don\'t need error bars, specify this argument') 

args = parser.parse_args()
print(args)

raw_sheet_df = pd.read_csv(args.source, header=None)

extracted_raw_df = raw_sheet_df[[13,15,23,25,27,29,31,33,35,37,39,51,53,55,57,59,61,75,77,79,81,83]]

col_name_table = {
    13: '年月日', 15: '時刻', 23: '身長(cm)', 25: '体重(kg)', 27: 'BMI', 29: '全身体脂肪率(％)',
    31: '右腕(皮下)脂肪率(％)', 33: '左腕(皮下)脂肪率(％)', 35: '右足(皮下)脂肪率(％)',
    37: '左足(皮下)脂肪率(％)', 39: '体幹部脂肪率(％)', 51: '全身筋肉量(kg)', 53: '右腕筋肉量(kg)',
    55: '左腕筋肉量(kg)', 57: '右足筋肉量(kg)', 59: '左足筋肉量(kg)', 61: '体幹部筋肉量(kg)',
    75: '推定骨量(kg)', 77: '内臓脂肪(レベル)', 79: '基礎代謝量(kcal／日)', 81: '体内年齢(才)', 83: '体水分率(％)'
}

renamed_raw_df = extracted_raw_df.rename(columns=col_name_table)
renamed_raw_df['年月日'] = pd.to_datetime(renamed_raw_df['年月日'], errors='coerce')
renamed_raw_df = renamed_raw_df.dropna(subset=['年月日'])

numeric_df = renamed_raw_df.select_dtypes(include='number')
date_index = renamed_raw_df['年月日']

daily = [
    numeric_df.set_index(date_index).resample("D").mean().interpolate(),
    numeric_df.set_index(date_index).resample("D").agg([min, max]).interpolate()
]

weekly = [
    numeric_df.set_index(date_index).resample("W").mean().interpolate(),
    numeric_df.set_index(date_index).resample("W").agg([min, max]).interpolate()
]

monthly = [
    numeric_df.set_index(date_index).resample("M").mean().interpolate(),
    numeric_df.set_index(date_index).resample("M").agg([min, max]).interpolate()
]

pd.set_option('display.max_rows', 200)
print(daily[0].head(20))
print(weekly[0].head(20))
print(monthly[0].head(20))

diagrams = []

if 'daily' in args.granularities:
    diagrams.append(daily)
if 'weekly' in args.granularities:
    diagrams.append(weekly)
if 'monthly' in args.granularities:
    diagrams.append(monthly)

items = [] if args.items == ['none'] else args.items

plt.rcParams['figure.figsize'] = [15, 10]

for itm in items:
    for gran in diagrams:
        if gran is daily:
            title = f'{itm} -- 日次'
            out_dir = './graph-daily'
        elif gran is weekly:
            title = f'{itm} -- 週平均'
            out_dir = './graph-weekly'
        elif gran is monthly:
            title = f'{itm} -- 月平均'
            out_dir = './graph-monthly'

        t = gran[0].index
        y = gran[0][itm]
        y_min = y - gran[1][itm]['min']
        y_max = gran[1][itm]['max'] - y
        y_min.where(y_min > 0, 0, inplace=True)
        ecol = 'none' if args.no_errorbars else 'blue'

        plt.errorbar(t, y, yerr=[y_min, y_max], fmt='o', markersize=4, ecolor=ecol,
                     elinewidth=0.8, color='blue', linestyle='-', capsize=2)
        plt.title(title)
        os.makedirs(out_dir, exist_ok=True)
        plt.savefig(f'{out_dir}/{itm}.png')
        plt.close()

pair = ['体重(kg)', '全身体脂肪率(％)']
for gran in diagrams:
    if gran is daily:
        title = f'{pair[0]} : {pair[1]} -- 日次'
        out_dir = './graph-daily'
    elif gran is weekly:
        title = f'{pair[0]} : {pair[1]} -- 週平均'
        out_dir = './graph-weekly'
    elif gran is monthly:
        title = f'{pair[0]} : {pair[1]} -- 月平均'
        out_dir = './graph-monthly'

    fig, ax1 = plt.subplots(1, 1, figsize=(12,9))
    plt.title(title)
    t = gran[0].index

    y1 = gran[0][pair[0]]
    y1_min = y1 - gran[1][pair[0]]['min']
    y1_max = gran[1][pair[0]]['max'] - y1
    ecol = 'blue' if not args.no_errorbars else 'none'
    ax1.errorbar(t, y1, yerr=[y1_min, y1_max], fmt='o', markersize=4, ecolor=ecol,
                 elinewidth=0.8, color='blue', linestyle='-', capsize=2)

    ax2 = ax1.twinx()
    y2 = gran[0][pair[1]]
    y2_min = y2 - gran[1][pair[1]]['min']
    y2_max = gran[1][pair[1]]['max'] - y2
    ecol = 'orange' if not args.no_errorbars else 'none'
    ax2.errorbar(t, y2, yerr=[y2_min, y2_max], fmt='o', markersize=4, ecolor=ecol,
                 elinewidth=0.8, color='orange', linestyle='-', capsize=2)

    ax1.set_xlabel('年月日')
    ax1.set_ylabel(pair[0], color='blue')
    ax1.grid(True)
    ax1.tick_params(axis='y', labelcolor='blue')

    ax2.set_ylabel(pair[1], color='orange')
    ax2.tick_params(axis='y', labelcolor='orange')

    ax1.set_ylim(50, 70)
    ax2.set_ylim(5, 25)

    os.makedirs(out_dir, exist_ok=True)
    plt.savefig(f'{out_dir}/{pair[0]}-{pair[1]}.png')
    plt.show()
    plt.close()

