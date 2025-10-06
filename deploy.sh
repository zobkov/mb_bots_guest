#!/bin/bash

# Скрипт быстрого развертывания бота

echo "🚀 Начинаем развертывание бота для конференции 'Менеджмент Будущего '25'..."

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python 3.11 или выше."
    exit 1
fi

# Проверяем наличие pip
if ! command -v pip &> /dev/null; then
    echo "❌ pip не найден. Установите pip."
    exit 1
fi

# Устанавливаем зависимости
echo "📦 Установка зависимостей..."
pip install -r requirements.txt

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден!"
    echo "Создайте файл .env с необходимыми настройками."
    echo "Пример см. в README.md"
    exit 1
fi

# Проверяем наличие Google credentials
if [ ! -f app/config/google_credentials.json ]; then
    echo "❌ Файл google_credentials.json не найден в app/config/"
    echo "Поместите файл с учетными данными Google Sheets API в app/config/"
    exit 1
fi

# Проверяем подключения
echo "🔍 Проверка подключений к инфраструктуре..."
python3 check_connections.py

if [ $? -ne 0 ]; then
    echo "❌ Есть проблемы с подключениями. Проверьте настройки."
    exit 1
fi

# Создаем таблицы в базе данных
echo "🗄️  Создание таблиц в базе данных..."
python3 create_migrations.py --create

if [ $? -ne 0 ]; then
    echo "❌ Ошибка создания таблиц."
    exit 1
fi

# Добавляем тестовые мероприятия
echo "📅 Добавление мероприятий в базу данных..."
python3 add_events.py

if [ $? -ne 0 ]; then
    echo "❌ Ошибка добавления мероприятий."
    exit 1
fi

echo "✅ Развертывание завершено успешно!"
echo ""
echo "🎉 Бот готов к запуску!"
echo "Для запуска выполните: python3 main.py"
echo ""
echo "📱 Команды бота:"
echo "  /start - начать работу с ботом"
echo ""
echo "📊 Полезные команды:"
echo "  python3 check_connections.py - проверить подключения"
echo "  python3 add_events.py - добавить мероприятия"
echo ""
echo "📖 Подробную документацию см. в README.md"