#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт для выполнения анализа гендерного разрыва в заработных платах
Выполняет основные шаги из ноутбука для проверки работоспособности
"""

import sys
import os
import io

# Настройка кодировки для Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*70)
print("ПРОВЕРКА И ВЫПОЛНЕНИЕ АНАЛИЗА ГЕНДЕРНОГО РАЗРЫВА В ЗАРАБОТНЫХ ПЛАТАХ")
print("="*70)

# Шаг 1: Проверка импорта библиотек
print("\n[1/7] Проверка импорта библиотек...")
try:
    import pandas as pd
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')  # Используем non-interactive backend
    import matplotlib.pyplot as plt
    import seaborn as sns
    import statsmodels.api as sm
    from statsmodels.stats.diagnostic import het_breuschpagan, het_white
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    from scipy import stats
    print("[OK] Все библиотеки успешно импортированы")
except ImportError as e:
    print(f"[ERROR] Ошибка импорта: {e}")
    print("  Установите зависимости: pip install -r requirements.txt")
    sys.exit(1)

# Шаг 2: Проверка наличия данных
print("\n[2/7] Проверка наличия данных...")
data_file = 'data/RLMS_IND_1994_2024_v3_rus.dta'
if os.path.exists(data_file):
    print(f"[OK] Файл данных найден: {data_file}")
else:
    print(f"[ERROR] Файл данных не найден: {data_file}")
    print("  Убедитесь, что файл находится в папке data/")
    sys.exit(1)

# Шаг 3: Загрузка данных
print("\n[3/7] Загрузка данных...")
try:
    df_full = pd.read_stata(data_file, convert_categoricals=False)
    print(f"✓ Данные загружены. Размер: {df_full.shape}")
    
    # Проверка ключевых переменных
    key_vars = ['year', 'region', 'h5']
    missing_vars = [v for v in key_vars if v not in df_full.columns]
    if missing_vars:
        print(f"⚠ Предупреждение: отсутствуют переменные: {missing_vars}")
    else:
        print("✓ Все ключевые переменные найдены")
        
    # Проверка годов
    available_years = sorted(df_full['year'].dropna().unique())
    print(f"✓ Доступные годы: {available_years}")
    if 2010 in available_years and 2020 in available_years:
        print("✓ Нужные годы (2010, 2020) присутствуют в данных")
    else:
        print("⚠ Предупреждение: не все нужные годы присутствуют")
        
except Exception as e:
    print(f"✗ Ошибка при загрузке данных: {e}")
    sys.exit(1)

# Шаг 4: Фильтрация данных
print("\n[4/7] Фильтрация данных по годам и регионам...")
try:
    df = df_full[df_full['year'].isin([2010, 2020])].copy()
    print(f"✓ Данные отфильтрованы по годам. Размер: {df.shape}")
    
    # Поиск регионов
    unique_regions = df['region'].dropna().unique()
    print(f"✓ Найдено уникальных регионов: {len(unique_regions)}")
    
    # Попытка найти Москву и Тулу
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
        print(f"⚠ Используются первые два региона: {moscow_codes[0]}, {tula_codes[0]}")
    else:
        print(f"✓ Найдены коды: Москва={moscow_codes}, Тула={tula_codes}")
    
    df = df[df['region'].isin(moscow_codes + tula_codes)].copy()
    print(f"✓ Данные отфильтрованы по регионам. Размер: {df.shape}")
    
except Exception as e:
    print(f"✗ Ошибка при фильтрации: {e}")
    sys.exit(1)

# Шаг 5: Создание переменных
print("\n[5/7] Создание переменных...")
try:
    # Пол
    if 'h5' in df.columns:
        df['female'] = (df['h5'] == 2).astype(int)
        print("✓ Переменная 'female' создана")
    
    # Заработная плата
    wage_vars = ['j13.2', 'j13_2', 'j132', 'j13.3', 'j13_3', 'j133']
    wage_var = None
    for var in wage_vars:
        if var in df.columns:
            wage_var = var
            break
    
    if wage_var:
        df_wage = df[df[wage_var] > 0].copy()
        df_wage['ln_wage'] = np.log(df_wage[wage_var])
        df = df_wage.copy()
        print(f"✓ Переменная 'ln_wage' создана из {wage_var}")
    else:
        print("⚠ Переменная заработной платы не найдена")
    
    # Возраст
    if 'age' in df.columns:
        df['age_sq'] = df['age'] ** 2
        print("✓ Переменные 'age' и 'age_sq' созданы")
    else:
        birth_vars = ['h4_1_y', 'birth_year', 'byear']
        birth_var = None
        for var in birth_vars:
            if var in df.columns:
                birth_var = var
                break
        if birth_var:
            df['age'] = df['year'] - df[birth_var]
            df['age_sq'] = df['age'] ** 2
            print(f"✓ Возраст вычислен из {birth_var}")
    
    # Образование
    if 'educ' in df.columns:
        df['education'] = df['educ'].astype(float)
        print("✓ Переменная 'education' создана")
    elif 'j1' in df.columns:
        education_map = {1: 9, 2: 11, 3: 13, 4: 15, 5: 17}
        df['education'] = df['j1'].map(education_map)
        print("✓ Переменная 'education' создана из j1")
    
    # Опыт
    if 'j7' in df.columns:
        df['experience'] = df['j7'].astype(float)
        df['experience_sq'] = df['experience'] ** 2
        print("✓ Переменные 'experience' и 'experience_sq' созданы")
    
    # Семейное положение
    if 'marst' in df.columns:
        df['married'] = (df['marst'] == 1).astype(int)
        print("✓ Переменная 'married' создана")
    
    # Регион и год
    df['moscow'] = (df['region'].isin(moscow_codes)).astype(int)
    df['year_2020'] = (df['year'] == 2020).astype(int)
    print("✓ Переменные 'moscow' и 'year_2020' созданы")
    
    # Очистка данных
    variables_needed = ['ln_wage', 'female', 'age', 'age_sq']
    variables_all = [v for v in variables_needed if v in df.columns]
    df_clean = df[variables_all + ['moscow', 'year_2020']].copy()
    df_clean = df_clean.dropna(subset=variables_needed)
    
    if 'age' in df_clean.columns:
        df_clean = df_clean[(df_clean['age'] >= 18) & (df_clean['age'] <= 65)]
    
    df = df_clean.copy()
    print(f"✓ Данные очищены. Итоговый размер: {df.shape}")
    
except Exception as e:
    print(f"✗ Ошибка при создании переменных: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Шаг 6: Описательная статистика
print("\n[6/7] Вычисление описательной статистики...")
try:
    print(f"\nРазмер выборки: {len(df)}")
    print(f"Распределение по полу:")
    print(df['female'].value_counts())
    print(f"\nРаспределение по регионам:")
    print(df['moscow'].value_counts())
    print(f"\nРаспределение по годам:")
    print(df['year_2020'].value_counts())
    
    if 'ln_wage' in df.columns:
        wage_by_gender = df.groupby('female')['ln_wage'].agg(['mean', 'std', 'count'])
        print(f"\nСредние заработные платы по полу:")
        print(wage_by_gender)
        print("✓ Описательная статистика вычислена")
    
except Exception as e:
    print(f"✗ Ошибка при вычислении статистики: {e}")

# Шаг 7: Проверка возможности оценки моделей
print("\n[7/7] Проверка возможности оценки моделей...")
try:
    vars_model1 = ['female', 'age', 'age_sq']
    optional_vars = ['education', 'experience', 'experience_sq']
    for var in optional_vars:
        if var in df.columns:
            vars_model1.append(var)
    
    X1 = df[vars_model1].copy()
    X1 = sm.add_constant(X1)
    y = df['ln_wage']
    
    # Проверка на достаточное количество наблюдений
    if len(X1) < 10:
        print("⚠ Недостаточно наблюдений для оценки модели")
    else:
        model1 = sm.OLS(y, X1).fit()
        print(f"✓ Модель 1 успешно оценена")
        print(f"  R² = {model1.rsquared:.4f}")
        print(f"  Коэффициент female = {model1.params.get('female', 'N/A'):.4f}")
        print(f"  p-value = {model1.pvalues.get('female', 'N/A'):.4f}")
    
except Exception as e:
    print(f"✗ Ошибка при оценке модели: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("ПРОВЕРКА ЗАВЕРШЕНА")
print("="*70)
print("\nСледующие шаги:")
print("1. Откройте ноутбук gender_wage_gap_analysis.ipynb в Jupyter")
print("2. Запустите все ячейки последовательно")
print("3. Проверьте результаты анализа")
print("\nДля запуска Jupyter:")
print("  jupyter notebook gender_wage_gap_analysis.ipynb")
print("  или")
print("  jupyter lab gender_wage_gap_analysis.ipynb")

