#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Проверка статуса анализа
"""

import os
import json
from datetime import datetime

print("="*70)
print("ПРОВЕРКА СТАТУСА АНАЛИЗА")
print("="*70)
print()

# Проверка файлов результатов
results_dir = 'results'
figures_dir = 'figures'

print("[1] Проверка папок результатов...")
if os.path.exists(results_dir):
        print(f"  [OK] Папка {results_dir} существует")
        files = os.listdir(results_dir)
        if files:
            print(f"  [OK] Найдено файлов: {len(files)}")
            for f in files:
                size = os.path.getsize(os.path.join(results_dir, f)) / 1024
                print(f"    - {f} ({size:.2f} KB)")
        else:
            print(f"  [EMPTY] Папка {results_dir} пуста")
else:
    print(f"  [MISSING] Папка {results_dir} не существует")

if os.path.exists(figures_dir):
    print(f"  [OK] Папка {figures_dir} существует")
    files = os.listdir(figures_dir)
    if files:
        print(f"  [OK] Найдено файлов: {len(files)}")
        for f in files:
            size = os.path.getsize(os.path.join(figures_dir, f)) / 1024
            print(f"    - {f} ({size:.2f} KB)")
    else:
        print(f"  [EMPTY] Папка {figures_dir} пуста")
else:
    print(f"  [MISSING] Папка {figures_dir} не существует")

print()

# Проверка ключевых файлов
print("[2] Проверка ключевых файлов результатов...")
key_files = {
    'analysis_summary.json': 'Основной файл с результатами',
    'comparison_table.csv': 'Таблица сравнения моделей',
    'model1_summary.txt': 'Результаты модели 1',
    'model4_summary.txt': 'Результаты модели 4',
}

all_exist = True
for filename, description in key_files.items():
    filepath = os.path.join(results_dir, filename)
    if os.path.exists(filepath):
        size = os.path.getsize(filepath) / 1024
        print(f"  [OK] {filename} ({description}) - {size:.2f} KB")
    else:
        print(f"  [MISSING] {filename} ({description}) - НЕ НАЙДЕН")
        all_exist = False

print()

# Если файл summary существует, показываем краткую информацию
summary_file = os.path.join(results_dir, 'analysis_summary.json')
if os.path.exists(summary_file):
    print("[3] Информация из analysis_summary.json:")
    try:
        with open(summary_file, 'r', encoding='utf-8') as f:
            summary = json.load(f)
        
        data_info = summary.get('data_info', {})
        models = summary.get('models', {})
        
        print(f"  [OK] Время выполнения: {summary.get('timestamp', 'N/A')}")
        print(f"  [OK] Размер выборки: {data_info.get('final_size', [0, 0])[0]:,} наблюдений")
        print(f"  [OK] Оценено моделей: {len(models)}")
        
        if models:
            print("\n  Краткие результаты моделей:")
            for name, data in models.items():
                female_coef = data.get('female_coef', 0)
                female_pval = data.get('female_pvalue', 1)
                sig = "***" if female_pval < 0.001 else "**" if female_pval < 0.01 else "*" if female_pval < 0.05 else ""
                print(f"    {name}: female = {female_coef:.4f}{sig} (p={female_pval:.4f})")
        
    except Exception as e:
        print(f"  [ERROR] Ошибка при чтении файла: {e}")
else:
    print("[3] Файл analysis_summary.json не найден - анализ не завершен")

print()

# Итоговый статус
print("="*70)
if all_exist:
    print("[SUCCESS] АНАЛИЗ ЗАВЕРШЕН УСПЕШНО!")
    print("\nСледующие шаги:")
    print("  1. Запустите: python fill_report_from_results.py")
    print("  2. Проверьте файл ДОКЛАД.md")
else:
    print("[WAITING] АНАЛИЗ НЕ ЗАВЕРШЕН")
    print("\nРекомендации:")
    print("  1. Запустите анализ: python execute_full_analysis.py")
    print("  2. Дождитесь завершения (может занять 10-30 минут)")
    print("  3. Проверьте статус снова: python check_analysis_status.py")
print("="*70)

