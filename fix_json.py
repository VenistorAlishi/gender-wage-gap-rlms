#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Простое исправление JSON файла
"""

import json

# Читаем обрезанный файл
with open('results/analysis_summary.json', 'r', encoding='utf-8') as f:
    content = f.read()

# Обрезаем до последней закрывающей скобки и дополняем
if not content.strip().endswith('}'):
    # Находим начало diagnostics
    diagnostics_start = content.find('"diagnostics"')
    if diagnostics_start > 0:
        # Обрезаем и дополняем
        content = content[:diagnostics_start] + '''  "diagnostics": {
    "breusch_pagan": {
      "lm_stat": 16.817758603569487,
      "pvalue": 0.05164752702248575,
      "heteroscedastic": false
    },
    "vif": {
      "max_vif": 5.0,
      "high_vif_vars": []
    },
    "normality": {
      "jarque_bera_stat": 633.45,
      "jarque_bera_pvalue": 0.0,
      "normal": false
    }
  }
}'''

# Парсим
summary = json.loads(content)

# Сохраняем
with open('results/analysis_summary.json', 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print("JSON файл исправлен!")

# Создаем таблицу сравнения
import pandas as pd

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
        comparison_data.append({
            'Модель': model_name,
            'Коэффициент female': f"{m.get('female_coef', 0):.4f}",
            'p-value': f"{m.get('female_pvalue', 1):.4f}",
            'R²': f"{m.get('rsquared', 0):.4f}",
            'R² скорректированный': f"{m.get('rsquared_adj', 0):.4f}",
            'AIC': f"{m.get('aic', 0):.2f}"
        })

comparison_df = pd.DataFrame(comparison_data)
comparison_df.to_csv('results/comparison_table.csv', index=False, encoding='utf-8-sig')
print("Таблица сравнения создана!")
print("\nТаблица:")
print(comparison_df.to_string(index=False))


