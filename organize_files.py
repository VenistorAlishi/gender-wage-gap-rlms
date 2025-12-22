#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт для организации файлов проекта
Перемещает файлы документации в docs/ и материалы в materials/
"""

import os
import shutil

def move_files():
    """Перемещает файлы в правильные папки"""
    
    # Файлы документации для перемещения в docs/
    docs_files = [
        "ТЕОРЕТИЧЕСКАЯ_ЧАСТЬ.md",
        "СТРУКТУРА_ДОКЛАДА.md",
        "ОПИСАНИЕ_ПЕРЕМЕННЫХ_И_МОДЕЛЕЙ.md",
        "ИНСТРУКЦИЯ.md",
        "ПЛАН_ДЕЙСТВИЙ.md",
        "КРАТКИЙ_ПЛАН.md",
        "СТАТУС_ПРОЕКТА.md",
        "НОВЫЕ_МАТЕРИАЛЫ.md",
        "PROJECT_STRUCTURE.md"
    ]
    
    # Файлы материалов для перемещения в materials/
    materials_files = [
        "ПРОЕКТНАЯ_РАБОТА_ПО_КУРСУ_ЭКОНОМЕТРИКА_1_задание_2025 (1).pdf",
        "Econometrics-1-Practice.pdf",
        "Ликбез_7_Контрольные_и_инструментальные_переменные.pdf",
        "БД_2021_ind_codebook.pdf",
        "к проекту.do"
    ]
    
    print("Организация файлов проекта...")
    print("=" * 50)
    
    # Перемещение документации
    print("\nПеремещение документации в docs/...")
    moved_docs = 0
    for file in docs_files:
        if os.path.exists(file):
            try:
                shutil.move(file, os.path.join("docs", file))
                print(f"  OK Перемещен: {file}")
                moved_docs += 1
            except Exception as e:
                print(f"  ERROR Ошибка при перемещении {file}: {e}")
        else:
            print(f"  - Не найден: {file}")
    
    print(f"\nПеремещено файлов документации: {moved_docs}")
    
    # Перемещение материалов
    print("\nПеремещение материалов в materials/...")
    moved_materials = 0
    for file in materials_files:
        if os.path.exists(file):
            try:
                shutil.move(file, os.path.join("materials", file))
                print(f"  OK Перемещен: {file}")
                moved_materials += 1
            except Exception as e:
                print(f"  ERROR Ошибка при перемещении {file}: {e}")
        else:
            print(f"  - Не найден: {file}")
    
    print(f"\nПеремещено файлов материалов: {moved_materials}")
    print("\n" + "=" * 50)
    print("Готово! Файлы организованы.")
    print("Проверьте структуру папок docs/ и materials/")

if __name__ == "__main__":
    move_files()

