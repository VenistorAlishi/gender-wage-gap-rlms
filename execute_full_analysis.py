#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Полный скрипт для выполнения анализа гендерного разрыва в заработных платах
Выполняет все шаги из ноутбука gender_wage_gap_analysis.ipynb
"""

import sys
import os
import io
import json
from datetime import datetime

# Настройка кодировки для Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan, het_white, linear_reset
from statsmodels.stats.outliers_influence import variance_inflation_factor
from scipy import stats

# Настройка отображения
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)
plt.rcParams['font.family'] = 'DejaVu Sans'

# Создание папок для результатов
os.makedirs('results', exist_ok=True)
os.makedirs('figures', exist_ok=True)

print("="*70)
print("ПОЛНЫЙ АНАЛИЗ ГЕНДЕРНОГО РАЗРЫВА В ЗАРАБОТНЫХ ПЛАТАХ")
print("="*70)
print(f"Начало выполнения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Словарь для хранения результатов
results_summary = {
    'timestamp': datetime.now().isoformat(),
    'data_info': {},
    'models': {},
    'diagnostics': {}
}

# ============================================================================
# ШАГ 1: ЗАГРУЗКА ДАННЫХ
# ============================================================================
print("[1/8] Загрузка данных...")
try:
    data_file = 'data/RLMS_IND_1994_2024_v3_rus.dta'
    print(f"Загрузка из {data_file}...")
    df_full = pd.read_stata(data_file, convert_categoricals=False)
    print(f"Данные загружены. Размер: {df_full.shape}")
    results_summary['data_info']['full_size'] = list(df_full.shape)
    
    # Проверка переменных
    key_vars = ['year', 'region', 'h5']
    available_vars = [v for v in key_vars if v in df_full.columns]
    print(f"Доступные ключевые переменные: {available_vars}")
    
    available_years = sorted(df_full['year'].dropna().unique())
    print(f"Доступные годы: {available_years}")
    results_summary['data_info']['available_years'] = available_years
    
except Exception as e:
    print(f"ОШИБКА при загрузке данных: {e}")
    sys.exit(1)

# ============================================================================
# ШАГ 2: ФИЛЬТРАЦИЯ И ПОДГОТОВКА ДАННЫХ
# ============================================================================
print("\n[2/8] Фильтрация и подготовка данных...")
try:
    # Фильтрация по годам
    df = df_full[df_full['year'].isin([2010, 2020])].copy()
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
    print(f"Размер после фильтрации по регионам: {df.shape}")
    
    # Создание переменных
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
    if 'age' in df.columns:
        df['age_sq'] = df['age'] ** 2
    else:
        birth_vars = ['h4_1_y', 'birth_year', 'byear']
        for var in birth_vars:
            if var in df.columns:
                df['age'] = df['year'] - df[var]
                df['age_sq'] = df['age'] ** 2
                break
    
    # Образование
    if 'educ' in df.columns:
        df['education'] = df['educ'].astype(float)
    elif 'j1' in df.columns:
        education_map = {1: 9, 2: 11, 3: 13, 4: 15, 5: 17}
        df['education'] = df['j1'].map(education_map)
    
    # Опыт
    if 'j7' in df.columns:
        df['experience'] = df['j7'].astype(float)
        df['experience_sq'] = df['experience'] ** 2
    
    # Семейное положение
    if 'marst' in df.columns:
        df['married'] = (df['marst'] == 1).astype(int)
    
    # Регион и год
    df['moscow'] = (df['region'].isin(moscow_codes)).astype(int)
    df['year_2020'] = (df['year'] == 2020).astype(int)
    
    # Очистка
    variables_needed = ['ln_wage', 'female', 'age', 'age_sq']
    variables_optional = ['education', 'experience', 'experience_sq', 'married']
    variables_all = [v for v in variables_needed + variables_optional if v in df.columns]
    
    df_clean = df[variables_all + ['moscow', 'year_2020']].copy()
    df_clean = df_clean.dropna(subset=variables_needed)
    
    if 'age' in df_clean.columns:
        df_clean = df_clean[(df_clean['age'] >= 18) & (df_clean['age'] <= 65)]
    
    df = df_clean.copy()
    print(f"Итоговый размер выборки: {df.shape}")
    results_summary['data_info']['final_size'] = list(df.shape)
    results_summary['data_info']['variables'] = list(df.columns)
    
except Exception as e:
    print(f"ОШИБКА при подготовке данных: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# ШАГ 3: ОПИСАТЕЛЬНАЯ СТАТИСТИКА
# ============================================================================
print("\n[3/8] Вычисление описательной статистики...")
try:
    desc_stats = df[['ln_wage', 'female', 'age'] + 
                     [v for v in ['education', 'experience', 'married'] if v in df.columns]].describe()
    
    wage_by_gender = df.groupby('female')['ln_wage'].agg(['mean', 'std', 'count'])
    results_summary['data_info']['wage_by_gender'] = wage_by_gender.to_dict()
    
    print(f"Размер выборки: {len(df)}")
    print(f"Распределение по полу:\n{df['female'].value_counts()}")
    print(f"\nСредние заработные платы по полу:\n{wage_by_gender}")
    
except Exception as e:
    print(f"ОШИБКА при вычислении статистики: {e}")

# ============================================================================
# ШАГ 4-6: ОЦЕНКА МОДЕЛЕЙ
# ============================================================================
print("\n[4/8] Оценка моделей...")

y = df['ln_wage']
models = {}

# Модель 1: Базовая
print("\nОценка Модели 1 (Базовая)...")
vars_model1 = ['female', 'age', 'age_sq']
for var in ['education', 'experience', 'experience_sq']:
    if var in df.columns:
        vars_model1.append(var)

X1 = df[vars_model1].copy()
X1 = sm.add_constant(X1)
model1 = sm.OLS(y, X1).fit()
models['model1'] = {
    'rsquared': float(model1.rsquared),
    'rsquared_adj': float(model1.rsquared_adj),
    'aic': float(model1.aic),
    'female_coef': float(model1.params.get('female', 0)),
    'female_pvalue': float(model1.pvalues.get('female', 1))
}

# Модель 2: С семейным положением
print("Оценка Модели 2 (С семейным положением)...")
vars_model2 = vars_model1.copy()
if 'married' in df.columns:
    vars_model2.append('married')

X2 = df[vars_model2].copy()
X2 = sm.add_constant(X2)
model2 = sm.OLS(y, X2).fit()
models['model2'] = {
    'rsquared': float(model2.rsquared),
    'rsquared_adj': float(model2.rsquared_adj),
    'aic': float(model2.aic),
    'female_coef': float(model2.params.get('female', 0)),
    'female_pvalue': float(model2.pvalues.get('female', 1))
}

# Модель 4: С регионом и годом
print("Оценка Модели 4 (С регионом и годом)...")
vars_model4 = vars_model2.copy()
vars_model4.extend(['moscow', 'year_2020'])

X4 = df[vars_model4].copy()
X4 = sm.add_constant(X4)
model4 = sm.OLS(y, X4).fit()
models['model4'] = {
    'rsquared': float(model4.rsquared),
    'rsquared_adj': float(model4.rsquared_adj),
    'aic': float(model4.aic),
    'female_coef': float(model4.params.get('female', 0)),
    'female_pvalue': float(model4.pvalues.get('female', 1))
}

# Модель 5: С взаимодействием пола и региона
print("Оценка Модели 5 (С взаимодействием пола и региона)...")
df['female_moscow'] = df['female'] * df['moscow']
vars_model5 = vars_model4.copy()
vars_model5.append('female_moscow')

X5 = df[vars_model5].copy()
X5 = sm.add_constant(X5)
model5 = sm.OLS(y, X5).fit()
models['model5'] = {
    'rsquared': float(model5.rsquared),
    'rsquared_adj': float(model5.rsquared_adj),
    'aic': float(model5.aic),
    'female_coef': float(model5.params.get('female', 0)),
    'female_pvalue': float(model5.pvalues.get('female', 1)),
    'female_moscow_coef': float(model5.params.get('female_moscow', 0)),
    'female_moscow_pvalue': float(model5.pvalues.get('female_moscow', 1))
}

# Модель 6: С взаимодействием пола и года
print("Оценка Модели 6 (С взаимодействием пола и года)...")
df['female_year'] = df['female'] * df['year_2020']
vars_model6 = vars_model4.copy()
vars_model6.append('female_year')

X6 = df[vars_model6].copy()
X6 = sm.add_constant(X6)
model6 = sm.OLS(y, X6).fit()
models['model6'] = {
    'rsquared': float(model6.rsquared),
    'rsquared_adj': float(model6.rsquared_adj),
    'aic': float(model6.aic),
    'female_coef': float(model6.params.get('female', 0)),
    'female_pvalue': float(model6.pvalues.get('female', 1)),
    'female_year_coef': float(model6.params.get('female_year', 0)),
    'female_year_pvalue': float(model6.pvalues.get('female_year', 1))
}

results_summary['models'] = models

# Сохранение результатов моделей
for i, (name, model_obj) in enumerate([('model1', model1), ('model2', model2), 
                                       ('model4', model4), ('model5', model5), ('model6', model6)], 1):
    try:
        with open(f'results/{name}_summary.txt', 'w', encoding='utf-8') as f:
            f.write(model_obj.summary().as_text())
    except:
        pass

# ============================================================================
# ШАГ 7: ДИАГНОСТИКА МОДЕЛИ 4
# ============================================================================
print("\n[5/8] Проверка предпосылок Гаусса-Маркова (Модель 4)...")

diagnostics = {}

# Гетероскедастичность
try:
    bp_test = het_breuschpagan(model4.resid, X4)
    diagnostics['breusch_pagan'] = {
        'lm_stat': float(bp_test[0]),
        'pvalue': float(bp_test[1]),
        'heteroscedastic': bp_test[1] < 0.05
    }
    print(f"Тест Бройша-Пагана: LM={bp_test[0]:.4f}, p={bp_test[1]:.4f}")
except:
    pass

# VIF
try:
    vif_data = pd.DataFrame()
    vif_data['Variable'] = X4.columns
    vif_data['VIF'] = [variance_inflation_factor(X4.values, i) for i in range(X4.shape[1])]
    high_vif = vif_data[vif_data['VIF'] > 10]
    diagnostics['vif'] = {
        'max_vif': float(vif_data['VIF'].max()),
        'high_vif_vars': high_vif['Variable'].tolist() if len(high_vif) > 0 else []
    }
    print(f"Максимальный VIF: {vif_data['VIF'].max():.2f}")
except:
    pass

# Нормальность остатков
try:
    jb_stat, jb_p = stats.jarque_bera(model4.resid)
    diagnostics['normality'] = {
        'jarque_bera_stat': float(jb_stat),
        'jarque_bera_pvalue': float(jb_p),
        'normal': jb_p >= 0.05
    }
    print(f"Тест Жака-Бера: stat={jb_stat:.4f}, p={jb_p:.4f}")
except:
    pass

results_summary['diagnostics'] = diagnostics

# ============================================================================
# ШАГ 8: ГРАФИКИ
# ============================================================================
print("\n[6/8] Создание графиков...")

try:
    # График остатков
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    residuals = model4.resid
    fitted = model4.fittedvalues
    
    axes[0, 0].scatter(fitted, residuals, alpha=0.5, s=10)
    axes[0, 0].axhline(y=0, color='r', linestyle='--')
    axes[0, 0].set_xlabel('Предсказанные значения')
    axes[0, 0].set_ylabel('Остатки')
    axes[0, 0].set_title('Остатки vs предсказанные значения')
    axes[0, 0].grid(True, alpha=0.3)
    
    stats.probplot(residuals, dist="norm", plot=axes[0, 1])
    axes[0, 1].set_title('Q-Q plot остатков')
    axes[0, 1].grid(True, alpha=0.3)
    
    axes[1, 0].hist(residuals, bins=50, edgecolor='black', alpha=0.7)
    axes[1, 0].set_xlabel('Остатки')
    axes[1, 0].set_ylabel('Частота')
    axes[1, 0].set_title('Распределение остатков')
    axes[1, 0].grid(True, alpha=0.3)
    
    sample_size = min(1000, len(residuals))
    axes[1, 1].plot(residuals.iloc[:sample_size], alpha=0.7)
    axes[1, 1].axhline(y=0, color='r', linestyle='--')
    axes[1, 1].set_xlabel('Номер наблюдения')
    axes[1, 1].set_ylabel('Остатки')
    axes[1, 1].set_title(f'Остатки по порядку (первые {sample_size})')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('figures/residuals_diagnostics.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("График остатков сохранен")
except Exception as e:
    print(f"Ошибка при создании графиков: {e}")

# ============================================================================
# СОХРАНЕНИЕ РЕЗУЛЬТАТОВ
# ============================================================================
print("\n[7/8] Сохранение результатов...")

# JSON с результатами
with open('results/analysis_summary.json', 'w', encoding='utf-8') as f:
    json.dump(results_summary, f, ensure_ascii=False, indent=2)

# Таблица сравнения моделей
comparison = pd.DataFrame({
    'Модель': ['Модель 1', 'Модель 2', 'Модель 4', 'Модель 5', 'Модель 6'],
    'Коэффициент female': [
        models['model1']['female_coef'],
        models['model2']['female_coef'],
        models['model4']['female_coef'],
        models['model5']['female_coef'],
        models['model6']['female_coef']
    ],
    'p-value': [
        models['model1']['female_pvalue'],
        models['model2']['female_pvalue'],
        models['model4']['female_pvalue'],
        models['model5']['female_pvalue'],
        models['model6']['female_pvalue']
    ],
    'R²': [
        models['model1']['rsquared'],
        models['model2']['rsquared'],
        models['model4']['rsquared'],
        models['model5']['rsquared'],
        models['model6']['rsquared']
    ],
    'R² скорректированный': [
        models['model1']['rsquared_adj'],
        models['model2']['rsquared_adj'],
        models['model4']['rsquared_adj'],
        models['model5']['rsquared_adj'],
        models['model6']['rsquared_adj']
    ],
    'AIC': [
        models['model1']['aic'],
        models['model2']['aic'],
        models['model4']['aic'],
        models['model5']['aic'],
        models['model6']['aic']
    ]
})

comparison.to_csv('results/comparison_table.csv', index=False, encoding='utf-8-sig')
print("Таблица сравнения моделей сохранена")

# ============================================================================
# ИТОГОВЫЙ ОТЧЕТ
# ============================================================================
print("\n[8/8] Итоговый отчет...")
print("\n" + "="*70)
print("ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
print("="*70)
print(f"\nРазмер выборки: {len(df)} наблюдений")
print(f"\nСравнение моделей:")
print(comparison.to_string(index=False))

best_model_idx = comparison['R² скорректированный'].idxmax()
best_model = comparison.loc[best_model_idx, 'Модель']
print(f"\nЛучшая модель (по скорректированному R²): {best_model}")
print(f"  Коэффициент female: {comparison.loc[best_model_idx, 'Коэффициент female']:.4f}")
print(f"  p-value: {comparison.loc[best_model_idx, 'p-value']:.4f}")

if comparison.loc[best_model_idx, 'p-value'] < 0.05:
    gap_pct = abs(comparison.loc[best_model_idx, 'Коэффициент female']) * 100
    print(f"\nВЫВОД: Обнаружен статистически значимый гендерный разрыв!")
    print(f"  Заработные платы женщин на {gap_pct:.2f}% ниже заработных плат мужчин")
    print(f"  (при прочих равных условиях)")
else:
    print(f"\nВЫВОД: Статистически значимого гендерного разрыва не обнаружено")

print("\n" + "="*70)
print(f"Завершено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)
print("\nРезультаты сохранены в:")
print("  - results/analysis_summary.json")
print("  - results/comparison_table.csv")
print("  - results/model*_summary.txt")
print("  - figures/residuals_diagnostics.png")




