# Скрипт для организации файлов проекта
# Запустите этот скрипт в PowerShell для перемещения файлов в правильные папки

Write-Host "Организация файлов проекта..." -ForegroundColor Green

# Перемещение документации в docs/
Write-Host "`nПеремещение документации в docs/..." -ForegroundColor Yellow
$docsFiles = @(
    "ТЕОРЕТИЧЕСКАЯ_ЧАСТЬ.md",
    "СТРУКТУРА_ДОКЛАДА.md",
    "ОПИСАНИЕ_ПЕРЕМЕННЫХ_И_МОДЕЛЕЙ.md",
    "ИНСТРУКЦИЯ.md",
    "ПЛАН_ДЕЙСТВИЙ.md",
    "КРАТКИЙ_ПЛАН.md",
    "СТАТУС_ПРОЕКТА.md",
    "НОВЫЕ_МАТЕРИАЛЫ.md",
    "PROJECT_STRUCTURE.md"
)

foreach ($file in $docsFiles) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "docs\" -Force -ErrorAction SilentlyContinue
        Write-Host "  Перемещён: $file" -ForegroundColor Gray
    }
}

# Перемещение материалов в materials/
Write-Host "`nПеремещение материалов в materials/..." -ForegroundColor Yellow
$materialsFiles = @(
    "ПРОЕКТНАЯ_РАБОТА_ПО_КУРСУ_ЭКОНОМЕТРИКА_1_задание_2025 (1).pdf",
    "Econometrics-1-Practice.pdf",
    "Ликбез_7_Контрольные_и_инструментальные_переменные.pdf",
    "БД_2021_ind_codebook.pdf",
    "к проекту.do"
)

foreach ($file in $materialsFiles) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "materials\" -Force -ErrorAction SilentlyContinue
        Write-Host "  Перемещён: $file" -ForegroundColor Gray
    }
}

Write-Host "`nГотово! Файлы организованы." -ForegroundColor Green
Write-Host "Проверьте структуру папок docs/ и materials/" -ForegroundColor Cyan



