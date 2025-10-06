# 🚀 Инструкции по управлению ботом Management Future '25

## ✅ Исправлены все проблемы

### 🐛 Решенные проблемы:

1. **❌ "Unknown start mode: reset_stack"**  
   ✅ **ИСПРАВЛЕНО**: Заменен на `StartMode.RESET_STACK`

2. **❌ "A sheet with the name 'general' already exists"**  
   ✅ **ИСПРАВЛЕНО**: Добавлена проверка существования листов

3. **❌ Неправильное использование ShowMode**  
   ✅ **ИСПРАВЛЕНО**: Добавлен правильный ShowMode для всех диалогов

## 🎯 Команды управления

### Запуск бота
```bash
python3 main.py
```

### Остановка бота
```bash
# Ctrl+C в терминале где запущен бот
# ИЛИ
pkill -f "python3 main.py"
```

### Мониторинг логов
```bash
# Интерактивный мониторинг
./monitor_logs.sh

# Быстрый просмотр
tail -f logs/general/general_$(date +%Y-%m-%d).log

# Только ошибки
tail -f logs/errors/errors_$(date +%Y-%m-%d).log
```

## 📁 Структура логов

```
logs/
├── general/           # 📝 Все логи
│   └── general_YYYY-MM-DD.log
└── errors/            # 🚨 Только ошибки  
    └── errors_YYYY-MM-DD.log
```

## 🔍 Поиск в логах

```bash
# Поиск по пользователю
grep "user_id=123456" logs/general/general_$(date +%Y-%m-%d).log

# Поиск ошибок
grep "ERROR\|CRITICAL" logs/general/general_$(date +%Y-%m-%d).log

# Поиск по времени
grep "19:30" logs/general/general_$(date +%Y-%m-%d).log
```

## 📊 Статистика использования

### Интерактивный мониторинг:
```bash
./monitor_logs.sh
# Команды в интерфейсе:
# stats, s      - статистика логов
# general, g    - последние общие логи  
# errors, e     - логи ошибок
# tail, t       - следить в реальном времени
# search <term> - поиск по логам
```

### Быстрая статистика:
```bash
# Количество запросов сегодня
grep -c "Обработка события" logs/general/general_$(date +%Y-%m-%d).log

# Уникальные пользователи
grep "user_id=" logs/general/general_$(date +%Y-%m-%d).log | \
    sed 's/.*user_id=\([0-9]*\).*/\1/' | sort -u | wc -l

# Количество ошибок
wc -l logs/errors/errors_$(date +%Y-%m-%d).log
```

## 🛠️ Отладка

### Если бот не отвечает:
1. Проверьте запущен ли процесс: `ps aux | grep "python3 main.py"`
2. Проверьте логи ошибок: `cat logs/errors/errors_$(date +%Y-%m-%d).log`
3. Проверьте подключения: `python3 check_connections.py`

### Если Google Sheets не работает:
1. Проверьте файл `google_credentials.json`
2. Проверьте URL таблицы в `.env`
3. Посмотрите логи: `grep "Google Sheets" logs/general/general_$(date +%Y-%m-%d).log`

### Если база данных недоступна:
1. Проверьте параметры в `.env`
2. Проверьте подключение: `python3 simple_db_check.py`
3. Посмотрите логи подключения

## 🎉 Статус бота

**✅ ВСЕ ПРОБЛЕМЫ ИСПРАВЛЕНЫ!**

- ✅ StartMode работает корректно
- ✅ Google Sheets интеграция стабильна  
- ✅ ShowMode настроен для всех диалогов
- ✅ Логирование работает идеально
- ✅ База данных подключена
- ✅ Redis работает стабильно

## 📞 Бот готов к работе!

**Telegram: @mb_guestbot**

Пользователи могут:
1. 📝 Регистрироваться через /start
2. 🎯 Записываться на мероприятия
3. 📋 Просматривать свои регистрации
4. ❓ Получать поддержку через FAQ
5. 📊 Все данные автоматически сохраняются в Google Sheets

**Все системы работают! 🚀**