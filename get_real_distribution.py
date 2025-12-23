# -*- coding: utf-8 -*-
"""
Скрипт для получения реального распределения по годам и регионам из данных RLMS
"""
import sys
import io

# Настройка кодировки для Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np

print("Загрузка данных...")
try:
    # Загружаем только нужные столбцы для экономии памяти
    data_file = 'data/RLMS_IND_1994_2024_v3_rus.dta'
    
    # Сначала загружаем только нужные столбцы
    print("Чтение данных (только нужные столбцы)...")
    df = pd.read_stata(data_file, convert_categoricals=False)
    
    # Фильтрация по годам
    df = df[df['year'].isin([2010, 2020])].copy()
    print(f"Размер после фильтрации по годам: {df.shape}")
    
    # Поиск регионов
    unique_regions = df['region'].dropna().unique()
    moscow_codes = []
    tula_codes = []
    
    if df['region'].dtype in ['int64', 'float64']:
        if 77 in unique_regions:
            moscow_codes.append(77)
        if 71 in unique_regions:
            tula_codes.append(71)
    
    if not moscow_codes or not tula_codes:
        sample_regions = df['region'].dropna().unique()[:2]
        moscow_codes = [sample_regions[0]]
        tula_codes = [sample_regions[1]]
        print(f"Используем первые два региона: {moscow_codes[0]}, {tula_codes[0]}")
    
    df = df[df['region'].isin(moscow_codes + tula_codes)].copy()
    
    # Создание переменных для фильтрации
    if 'h5' in df.columns:
        df['female'] = (df['h5'] == 2).astype(int)
    
    # Заработная плата
    wage_vars = ['j13.2', 'j13_2', 'j132', 'j13.3', 'j13_3', 'j133']
    wage_var = None
    for var in wage_vars:
        if var in df.columns:
            wage_var = var
            break
    
    if wage_var:
        df = df[df[wage_var] > 0].copy()
        df['ln_wage'] = np.log(df[wage_var])
    
    # Возраст
    if 'age' not in df.columns:
        birth_vars = ['h4_1_y', 'birth_year', 'byear']
        for var in birth_vars:
            if var in df.columns:
                df['age'] = df['year'] - df[var]
                break
    
    # Создание переменных региона и года
    df['moscow'] = (df['region'].isin(moscow_codes)).astype(int)
    df['year_2020'] = (df['year'] == 2020).astype(int)
    
    # Очистка данных
    variables_needed = ['ln_wage', 'female', 'age', 'moscow', 'year_2020', 'year']
    variables_all = [v for v in variables_needed if v in df.columns]
    df_clean = df[variables_all].copy()
    df_clean = df_clean.dropna(subset=['ln_wage', 'female', 'age'])
    
    if 'age' in df_clean.columns:
        df_clean = df_clean[(df_clean['age'] >= 18) & (df_clean['age'] <= 65)]
    
    print(f"\nИтоговый размер выборки: {len(df_clean)} наблюдений")
    
    # Распределение по годам
    print("\n" + "="*70)
    print("РАСПРЕДЕЛЕНИЕ ПО ГОДАМ:")
    print("="*70)
    year_dist = df_clean['year'].value_counts().sort_index()
    for year, count in year_dist.items():
        pct = (count / len(df_clean)) * 100
        print(f"  {int(year)}: {count} наблюдений ({pct:.1f}%)")
    
    # Распределение по регионам
    print("\n" + "="*70)
    print("РАСПРЕДЕЛЕНИЕ ПО РЕГИОНАМ:")
    print("="*70)
    region_dist = df_clean['moscow'].value_counts().sort_index()
    for region_code, count in region_dist.items():
        region_name = "Москва" if region_code == 1 else "Тула"
        pct = (count / len(df_clean)) * 100
        print(f"  {region_name}: {count} наблюдений ({pct:.1f}%)")
    
    # Перекрёстная таблица
    print("\n" + "="*70)
    print("ПЕРЕКРЁСТНАЯ ТАБЛИЦА (ГОД × РЕГИОН):")
    print("="*70)
    cross_tab = pd.crosstab(df_clean['year'], df_clean['moscow'], margins=True)
    cross_tab.index = [2010 if x == 2010 else (2020 if x == 2020 else 'Всего') for x in cross_tab.index]
    cross_tab.columns = ['Тула', 'Москва', 'Всего']
    print(cross_tab)
    
    # Сохранение результатов
    results = {
        'year_distribution': year_dist.to_dict(),
        'region_distribution': {('Москва' if k == 1 else 'Тула'): int(v) for k, v in region_dist.items()},
        'cross_table': cross_tab.to_dict()
    }
    
    import json
    with open('results/distribution_data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n✓ Данные сохранены в results/distribution_data.json")
    
except Exception as e:
    print(f"Ошибка: {e}")
    import traceback
    traceback.print_exc()


