#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт для автоматического заполнения доклада результатами анализа
"""

import json
import pandas as pd
import os
import re

def fill_report():
    """Заполняет доклад результатами из analysis_summary.json"""
    
    # Загрузка результатов
    if not os.path.exists('results/analysis_summary.json'):
        print("Файл results/analysis_summary.json не найден. Сначала выполните анализ.")
        return
    
    with open('results/analysis_summary.json', 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # Загрузка доклада
    if not os.path.exists('ДОКЛАД.md'):
        print("Файл ДОКЛАД.md не найден.")
        return
    
    with open('ДОКЛАД.md', 'r', encoding='utf-8') as f:
        report = f.read()
    
    # Заполнение данных
    data_info = results.get('data_info', {})
    models = results.get('models', {})
    diagnostics = results.get('diagnostics', {})
    
    # Размер выборки
    final_size = data_info.get('final_size', [0, 0])
    report = re.sub(
        r'Объём выборки: \[будет заполнено после выполнения анализа\]',
        f'Объём выборки: {final_size[0]:,} наблюдений',
        report
    )
    
    # Описательная статистика
    wage_by_gender = data_info.get('wage_by_gender', {})
    if wage_by_gender:
        desc_table = f"""
| Пол | Среднее ln(wage) | Стандартное отклонение | Количество |
|-----|------------------|------------------------|------------|
| Мужчины (0) | {wage_by_gender.get('mean', {}).get('0', 'N/A'):.4f} | {wage_by_gender.get('std', {}).get('0', 'N/A'):.4f} | {wage_by_gender.get('count', {}).get('0', 'N/A'):.0f} |
| Женщины (1) | {wage_by_gender.get('mean', {}).get('1', 'N/A'):.4f} | {wage_by_gender.get('std', {}).get('1', 'N/A'):.4f} | {wage_by_gender.get('count', {}).get('1', 'N/A'):.0f} |
"""
        report = re.sub(
            r'\[Таблица с описательной статистикой будет вставлена после выполнения анализа\]',
            desc_table,
            report
        )
    
    # Результаты моделей
    if models:
        comparison_rows = []
        for i, (model_name, model_data) in enumerate([
            ('model1', 'Модель 1'),
            ('model2', 'Модель 2'),
            ('model4', 'Модель 4'),
            ('model5', 'Модель 5'),
            ('model6', 'Модель 6')
        ], 1):
            if model_name in models:
                m = models[model_name]
                sig = '*' if m.get('female_pvalue', 1) < 0.05 else ''
                comparison_rows.append(
                    f"| {model_data} | {m.get('female_coef', 0):.4f}{sig} | {m.get('female_pvalue', 1):.4f} | "
                    f"{m.get('rsquared', 0):.4f} | {m.get('rsquared_adj', 0):.4f} | {m.get('aic', 0):.2f} |"
                )
        
        models_table = f"""
| Модель | Коэффициент female | p-value | R² | R² скорректированный | AIC |
|--------|-------------------|---------|----|---------------------|-----|
{chr(10).join(comparison_rows)}

*Примечание: * означает статистическую значимость на уровне 5%
"""
        report = re.sub(
            r'\[Таблицы с результатами оценки моделей будут вставлены после выполнения анализа\]',
            models_table,
            report
        )
    
    # Диагностика
    if diagnostics:
        diag_text = []
        
        bp = diagnostics.get('breusch_pagan', {})
        if bp:
            diag_text.append(f"**Тест Бройша-Пагана:** LM = {bp.get('lm_stat', 0):.4f}, p-value = {bp.get('pvalue', 1):.4f}")
            if bp.get('heteroscedastic', False):
                diag_text.append("Вывод: обнаружена гетероскедастичность. Рекомендуется использовать робастные стандартные ошибки.")
            else:
                diag_text.append("Вывод: гетероскедастичность не обнаружена.")
        
        vif = diagnostics.get('vif', {})
        if vif:
            diag_text.append(f"\n**VIF (мультиколлинеарность):** Максимальный VIF = {vif.get('max_vif', 0):.2f}")
            if vif.get('high_vif_vars'):
                diag_text.append(f"Предупреждение: высокий VIF у переменных: {', '.join(vif.get('high_vif_vars', []))}")
            else:
                diag_text.append("Проблем мультиколлинеарности не обнаружено (все VIF < 10).")
        
        norm = diagnostics.get('normality', {})
        if norm:
            diag_text.append(f"\n**Тест Жака-Бера (нормальность остатков):** Статистика = {norm.get('jarque_bera_stat', 0):.4f}, p-value = {norm.get('jarque_bera_pvalue', 1):.4f}")
            if norm.get('normal', True):
                diag_text.append("Вывод: остатки распределены нормально.")
            else:
                diag_text.append("Вывод: остатки не распределены нормально.")
        
        report = re.sub(
            r'\[Результаты тестов Бройша-Пагана и Уайта\]',
            '\n'.join(diag_text),
            report
        )
    
    # Выбор лучшей модели
    if models:
        best_model = None
        best_adj_r2 = -1
        for name, data in models.items():
            if data.get('rsquared_adj', 0) > best_adj_r2:
                best_adj_r2 = data.get('rsquared_adj', 0)
                best_model = (name, data)
        
        if best_model:
            name, data = best_model
            model_names = {'model1': 'Модель 1', 'model2': 'Модель 2', 'model4': 'Модель 4', 
                          'model5': 'Модель 5', 'model6': 'Модель 6'}
            best_text = f"""
**Лучшая модель:** {model_names.get(name, name)} (по скорректированному R²)

- R² скорректированный: {data.get('rsquared_adj', 0):.4f}
- Коэффициент female: {data.get('female_coef', 0):.4f}
- p-value: {data.get('female_pvalue', 1):.4f}
- AIC: {data.get('aic', 0):.2f}
"""
            report = re.sub(
                r'\[Обоснование выбора финальной модели на основе R², скорректированного R², AIC и соответствия предпосылкам\]',
                best_text,
                report
            )
    
    # Интерпретация результатов
    if models and 'model4' in models:
        m4 = models['model4']
        if m4.get('female_pvalue', 1) < 0.05:
            gap_pct = abs(m4.get('female_coef', 0)) * 100
            interp = f"""
Обнаружен статистически значимый гендерный разрыв в заработных платах (p < 0.05).

**Основной результат (Модель 4):**
- Коэффициент female: {m4.get('female_coef', 0):.4f}
- Статистическая значимость: p = {m4.get('female_pvalue', 1):.4f}
- **Интерпретация:** Заработные платы женщин на {gap_pct:.2f}% ниже заработных плат мужчин при прочих равных условиях (после учёта возраста, образования, опыта, семейного положения, региона и года).

Это "необъяснённый" разрыв, который может быть связан с ненаблюдаемыми характеристиками (способности, предпочтения, навыки переговоров) или потенциальной дискриминацией на рынке труда.
"""
        else:
            interp = """
Статистически значимого гендерного разрыва в заработных платах не обнаружено (p >= 0.05).

После учёта всех контрольных переменных (возраст, образование, опыт, семейное положение, регион, год) различия в заработных платах между мужчинами и женщинами не являются статистически значимыми.
"""
        report = re.sub(
            r'\[Интерпретация коэффициента female из лучшей модели\]',
            interp,
            report
        )
    
    # Сохранение заполненного доклада
    with open('ДОКЛАД.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("Доклад успешно заполнен результатами анализа!")
    print("Проверьте файл ДОКЛАД.md")

if __name__ == '__main__':
    fill_report()

