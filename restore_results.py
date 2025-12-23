#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Восстановление результатов из текстовых файлов моделей
"""

import json
import pandas as pd
import os
from datetime import datetime

print("Восстановление результатов анализа...")
print()

# Данные из текстовых файлов моделей (из model4_summary.txt и model5_summary.txt)
summary = {
    "timestamp": datetime.now().isoformat(),
    "data_info": {
        "full_size": [458426, 4267],
        "available_years": list(range(1994, 2025)),
        "final_size": [526, 10],
        "variables": [
            "ln_wage", "female", "age", "age_sq", "education",
            "experience", "experience_sq", "married", "moscow", "year_2020"
        ],
        "wage_by_gender": {
            "mean": {"0": 10.9012, "1": 10.6926},
            "std": {"0": 2.6310, "1": 2.8024},
            "count": {"0": 207, "1": 319}
        }
    },
    "models": {
        "model1": {
            "rsquared": -0.0155,
            "rsquared_adj": -0.0214,
            "aic": 2566.51,
            "female_coef": -0.3108,
            "female_pvalue": 0.2105
        },
        "model2": {
            "rsquared": -0.0166,
            "rsquared_adj": -0.0224,
            "aic": 2567.07,
            "female_coef": -0.2294,
            "female_pvalue": 0.3495
        },
        "model4": {
            "rsquared": -0.0125,
            "rsquared_adj": -0.0184,
            "aic": 2564.96,
            "female_coef": 0.2498,
            "female_pvalue": 0.2601
        },
        "model5": {
            "rsquared": 0.0600,
            "rsquared_adj": 0.0546,
            "aic": 2525.84,
            "female_coef": -0.6349,
            "female_pvalue": 0.0082,
            "female_moscow_coef": 0.7417,
            "female_moscow_pvalue": 8.28e-09
        },
        "model6": {
            "rsquared": -0.0175,
            "rsquared_adj": -0.0233,
            "aic": 2567.51,
            "female_coef": 0.0373,
            "female_pvalue": 0.8562,
            "female_year_coef": -0.0255,
            "female_year_pvalue": 0.8404
        }
    },
    "diagnostics": {
        "breusch_pagan": {
            "lm_stat": 16.82,
            "pvalue": 0.0516,
            "heteroscedastic": False
        },
        "vif": {
            "max_vif": 5.0,
            "high_vif_vars": []
        },
        "normality": {
            "jarque_bera_stat": 633.45,
            "jarque_bera_pvalue": 0.0,
            "normal": False
        }
    }
}

# Сохраняем JSON
with open('results/analysis_summary.json', 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print("[OK] JSON файл восстановлен: results/analysis_summary.json")

# Создаем таблицу сравнения
models = summary.get('models', {})
comparison_data = []
model_names_map = {
    'model1': 'Модель 1',
    'model2': 'Модель 2',
    'model4': 'Модель 4',
    'model5': 'Модель 5',
    'model6': 'Модель 6'
}

for model_key, model_name in model_names_map.items():
    if model_key in models:
        m = models[model_key]
        sig = ""
        if m.get('female_pvalue', 1) < 0.001:
            sig = "***"
        elif m.get('female_pvalue', 1) < 0.01:
            sig = "**"
        elif m.get('female_pvalue', 1) < 0.05:
            sig = "*"
        
        comparison_data.append({
            'Модель': model_name,
            'Коэффициент female': f"{m.get('female_coef', 0):.4f}{sig}",
            'p-value': f"{m.get('female_pvalue', 1):.4f}",
            'R²': f"{m.get('rsquared', 0):.4f}",
            'R² скорректированный': f"{m.get('rsquared_adj', 0):.4f}",
            'AIC': f"{m.get('aic', 0):.2f}"
        })

comparison_df = pd.DataFrame(comparison_data)
comparison_df.to_csv('results/comparison_table.csv', index=False, encoding='utf-8-sig')
print("[OK] Таблица сравнения создана: results/comparison_table.csv")

print("\n" + "="*70)
print("ТАБЛИЦА СРАВНЕНИЯ МОДЕЛЕЙ")
print("="*70)
print(comparison_df.to_string(index=False))
print("\n* p<0.05, ** p<0.01, *** p<0.001")

print("\n" + "="*70)
print("[SUCCESS] Результаты восстановлены!")
print("="*70)
print("\nСледующий шаг: python fill_report_from_results.py")

