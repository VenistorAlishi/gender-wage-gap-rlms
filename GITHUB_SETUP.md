# ИНСТРУКЦИЯ ПО СОЗДАНИЮ РЕПОЗИТОРИЯ НА GITHUB

## 📋 Подготовка к загрузке на GitHub

### 1. Проверка структуры проекта

Убедитесь, что у вас есть:
- ✅ `.gitignore` — файл для игнорирования ненужных файлов
- ✅ `README.md` — описание проекта
- ✅ `LICENSE` — лицензия
- ✅ `requirements.txt` — зависимости
- ✅ Все необходимые файлы документации

### 2. Инициализация Git репозитория

```bash
# Инициализация репозитория
git init

# Добавление всех файлов
git add .

# Первый коммит
git commit -m "Initial commit: Проект по эконометрике - исследование гендерного разрыва в заработных платах"
```

### 3. Создание репозитория на GitHub

1. Перейдите на https://github.com
2. Нажмите "New repository"
3. Заполните форму:
   - **Repository name:** `gender-wage-gap-rlms` (или другое название)
   - **Description:** "Исследование гендерного разрыва в заработных платах на данных RLMS (2010-2020, Москва-Тула)"
   - **Visibility:** Public или Private (на ваше усмотрение)
   - **НЕ добавляйте** README, .gitignore или LICENSE (они уже есть)
4. Нажмите "Create repository"

### 4. Подключение локального репозитория к GitHub

```bash
# Добавьте remote репозиторий (замените YOUR_USERNAME на ваш GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/gender-wage-gap-rlms.git

# Переименуйте ветку в main (если нужно)
git branch -M main

# Отправьте код на GitHub
git push -u origin main
```

---

## 📁 Рекомендуемая структура для GitHub

Перед загрузкой рекомендуется переместить файлы в правильные папки:

```
ПроектЭконометрика/
│
├── README.md                    # Главный README
├── LICENSE                      # Лицензия
├── .gitignore                   # Игнорируемые файлы
├── requirements.txt             # Зависимости
├── CONTRIBUTING.md              # Руководство по участию
├── IMPROVEMENTS.md              # Предложения по улучшению
│
├── gender_wage_gap_analysis.ipynb  # Основной ноутбук
│
├── docs/                        # Документация
│   ├── README.md
│   ├── ТЕОРЕТИЧЕСКАЯ_ЧАСТЬ.md
│   ├── СТРУКТУРА_ДОКЛАДА.md
│   ├── ОПИСАНИЕ_ПЕРЕМЕННЫХ_И_МОДЕЛЕЙ.md
│   ├── ИНСТРУКЦИЯ.md
│   ├── ПЛАН_ДЕЙСТВИЙ.md
│   ├── КРАТКИЙ_ПЛАН.md
│   ├── СТАТУС_ПРОЕКТА.md
│   ├── НОВЫЕ_МАТЕРИАЛЫ.md
│   └── PROJECT_STRUCTURE.md
│
├── materials/                   # Учебные материалы
│   ├── README.md
│   ├── ПРОЕКТНАЯ_РАБОТА_ПО_КУРСУ_ЭКОНОМЕТРИКА_1_задание_2025 (1).pdf
│   ├── Econometrics-1-Practice.pdf
│   ├── Ликбез_7_Контрольные_и_инструментальные_переменные.pdf
│   ├── БД_2021_ind_codebook.pdf
│   └── к проекту.do
│
├── data/                        # Данные (не в Git)
│   └── .gitkeep
│
├── results/                     # Результаты (не в Git)
│   └── .gitkeep
│
└── figures/                     # Графики (не в Git)
    └── .gitkeep
```

---

## 🔧 Команды для перемещения файлов

Если файлы ещё не перемещены, выполните вручную:

### Перемещение документации в docs/

```bash
# В PowerShell (по одному файлу)
Move-Item "ТЕОРЕТИЧЕСКАЯ_ЧАСТЬ.md" "docs\"
Move-Item "СТРУКТУРА_ДОКЛАДА.md" "docs\"
Move-Item "ОПИСАНИЕ_ПЕРЕМЕННЫХ_И_МОДЕЛЕЙ.md" "docs\"
Move-Item "ИНСТРУКЦИЯ.md" "docs\"
Move-Item "ПЛАН_ДЕЙСТВИЙ.md" "docs\"
Move-Item "КРАТКИЙ_ПЛАН.md" "docs\"
Move-Item "СТАТУС_ПРОЕКТА.md" "docs\"
Move-Item "НОВЫЕ_МАТЕРИАЛЫ.md" "docs\"
Move-Item "PROJECT_STRUCTURE.md" "docs\"
```

### Перемещение материалов в materials/

```bash
Move-Item "ПРОЕКТНАЯ_РАБОТА_ПО_КУРСУ_ЭКОНОМЕТРИКА_1_задание_2025 (1).pdf" "materials\"
Move-Item "Econometrics-1-Practice.pdf" "materials\"
Move-Item "Ликбез_7_Контрольные_и_инструментальные_переменные.pdf" "materials\"
Move-Item "БД_2021_ind_codebook.pdf" "materials\"
Move-Item "к проекту.do" "materials\"
```

---

## ✅ Чеклист перед загрузкой на GitHub

- [ ] Все файлы перемещены в правильные папки
- [ ] `.gitignore` настроен правильно
- [ ] `README.md` обновлён и содержит актуальную информацию
- [ ] `LICENSE` добавлен
- [ ] Данные не включены в репозиторий (проверьте `.gitignore`)
- [ ] Результаты и графики не включены (или включены только примеры)
- [ ] Все файлы документации на месте
- [ ] Ноутбук работает и не содержит ошибок

---

## 🚀 Дополнительные настройки GitHub

### Topics (теги)

Добавьте теги к репозиторию:
- `econometrics`
- `gender-wage-gap`
- `rlms`
- `python`
- `jupyter-notebook`
- `regression-analysis`
- `russia`

### Описание репозитория

Используйте:
```
Исследование гендерного разрыва в заработных платах в России на данных RLMS (2010-2020, Москва-Тула). Эконометрический анализ с проверкой предпосылок Гаусса-Маркова.
```

### README badges

В README уже добавлены badges для:
- Python версии
- Jupyter Notebook
- Лицензии

---

## 📝 Дополнительные файлы для GitHub

### GitHub Actions (опционально)

Создайте `.github/workflows/ci.yml` для автоматической проверки:

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Check notebook
        run: jupyter nbconvert --to notebook --execute gender_wage_gap_analysis.ipynb
```

---

## 🔗 Полезные ссылки

- [GitHub Guides](https://guides.github.com/)
- [Git Handbook](https://guides.github.com/introduction/git-handbook/)
- [Markdown Guide](https://www.markdownguide.org/)

---

## ⚠️ Важные замечания

1. **Данные не загружаются** — файлы `.dta` и `.sav` исключены через `.gitignore`
2. **PDF файлы** — можно загрузить, но они могут быть большими
3. **Результаты** — лучше не загружать, они генерируются при запуске
4. **Графики** — можно загрузить примеры, но не все

---

**После выполнения этих шагов ваш проект будет готов для GitHub!** 🎉



