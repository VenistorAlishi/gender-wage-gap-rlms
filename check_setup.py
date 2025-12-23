# -*- coding: utf-8 -*-
"""
Простой скрипт для проверки готовности к запуску анализа
"""
import sys
import os

print("="*70)
print("ПРОВЕРКА ГОТОВНОСТИ К ЗАПУСКУ АНАЛИЗА")
print("="*70)

# Проверка Python
print("\n[1] Python версия:", sys.version.split()[0])

# Проверка библиотек
print("\n[2] Проверка библиотек...")
libs = ['pandas', 'numpy', 'matplotlib', 'seaborn', 'statsmodels', 'scipy', 'jupyter']
missing = []
for lib in libs:
    try:
        __import__(lib)
        print(f"  [OK] {lib}")
    except ImportError:
        print(f"  [MISSING] {lib}")
        missing.append(lib)

if missing:
    print(f"\n[WARNING] Отсутствуют библиотеки: {', '.join(missing)}")
    print("  Установите: pip install -r requirements.txt")
else:
    print("\n[OK] Все библиотеки установлены")

# Проверка данных
print("\n[3] Проверка данных...")
data_file = 'data/RLMS_IND_1994_2024_v3_rus.dta'
if os.path.exists(data_file):
    size = os.path.getsize(data_file) / (1024*1024)  # MB
    print(f"  [OK] Файл данных найден: {data_file} ({size:.1f} MB)")
else:
    print(f"  [ERROR] Файл данных не найден: {data_file}")

# Проверка ноутбука
print("\n[4] Проверка ноутбука...")
notebook = 'gender_wage_gap_analysis.ipynb'
if os.path.exists(notebook):
    print(f"  [OK] Ноутбук найден: {notebook}")
else:
    print(f"  [ERROR] Ноутбук не найден: {notebook}")

print("\n" + "="*70)
if not missing and os.path.exists(data_file) and os.path.exists(notebook):
    print("[SUCCESS] Все готово к запуску!")
    print("\nСледующий шаг:")
    print("  jupyter notebook gender_wage_gap_analysis.ipynb")
else:
    print("[ACTION REQUIRED] Нужно исправить проблемы выше")
print("="*70)

