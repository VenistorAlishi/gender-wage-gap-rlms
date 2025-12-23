#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Запуск анализа с логированием в файл
"""

import subprocess
import sys
import os
from datetime import datetime

print("Запуск анализа с логированием...")
print(f"Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Создаем файл лога
log_file = 'analysis.log'
with open(log_file, 'w', encoding='utf-8') as f:
    f.write(f"Анализ начат: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("="*70 + "\n\n")

# Запускаем анализ с перенаправлением вывода
print("Запуск execute_full_analysis.py...")
print(f"Лог сохраняется в файл: {log_file}")
print("Анализ выполняется в фоновом режиме...")
print()

try:
    # Запускаем в фоновом режиме с логированием
    process = subprocess.Popen(
        [sys.executable, 'execute_full_analysis.py'],
        stdout=open(log_file, 'a', encoding='utf-8'),
        stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
    )
    
    print(f"Процесс запущен с PID: {process.pid}")
    print(f"Проверяйте прогресс в файле: {log_file}")
    print()
    print("Для проверки статуса выполните:")
    print("  python check_analysis_status.py")
    print()
    print("Или проверьте последние строки лога:")
    print(f"  Get-Content {log_file} -Tail 20")
    
except Exception as e:
    print(f"Ошибка при запуске: {e}")
    sys.exit(1)



