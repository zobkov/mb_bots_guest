#!/bin/bash

# Скрипт для мониторинга логов бота

CURRENT_DATE=$(date +%Y-%m-%d)
GENERAL_LOG="logs/general/general_${CURRENT_DATE}.log"
ERROR_LOG="logs/errors/errors_${CURRENT_DATE}.log"

echo "🤖 Мониторинг логов бота Management Future '25"
echo "📅 Дата: $CURRENT_DATE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Функция показа помощи
show_help() {
    echo "Доступные команды:"
    echo "  general, g     - показать общие логи"
    echo "  errors, e      - показать логи ошибок"
    echo "  tail, t        - следить за общими логами в реальном времени"
    echo "  tail-errors, te - следить за ошибками в реальном времени"
    echo "  stats, s       - показать статистику"
    echo "  search <term>  - поиск по логам"
    echo "  help, h        - показать эту справку"
    echo "  quit, q        - выход"
}

# Функция показа статистики
show_stats() {
    echo "📊 Статистика логов за $CURRENT_DATE:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [[ -f "$GENERAL_LOG" ]]; then
        echo "📝 Общие логи ($GENERAL_LOG):"
        echo "   Всего записей: $(wc -l < "$GENERAL_LOG")"
        echo "   INFO: $(grep -c "INFO" "$GENERAL_LOG" 2>/dev/null || echo 0)"
        echo "   WARNING: $(grep -c "WARNING" "$GENERAL_LOG" 2>/dev/null || echo 0)"
        echo "   ERROR: $(grep -c "ERROR" "$GENERAL_LOG" 2>/dev/null || echo 0)"
        echo "   CRITICAL: $(grep -c "CRITICAL" "$GENERAL_LOG" 2>/dev/null || echo 0)"
        echo ""
    else
        echo "❌ Файл общих логов не найден"
    fi
    
    if [[ -f "$ERROR_LOG" ]]; then
        echo "🚨 Логи ошибок ($ERROR_LOG):"
        echo "   Всего ошибок: $(wc -l < "$ERROR_LOG")"
        echo ""
    else
        echo "✅ Файл ошибок пуст или не существует"
    fi
}

# Основной цикл
show_help
echo ""

while true; do
    echo -n "📋 Введите команду: "
    read -r command args
    
    case $command in
        "general"|"g")
            if [[ -f "$GENERAL_LOG" ]]; then
                echo "📝 Последние 20 записей общих логов:"
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                tail -20 "$GENERAL_LOG"
            else
                echo "❌ Файл общих логов не найден: $GENERAL_LOG"
            fi
            ;;
        "errors"|"e")
            if [[ -f "$ERROR_LOG" && -s "$ERROR_LOG" ]]; then
                echo "🚨 Логи ошибок:"
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                cat "$ERROR_LOG"
            else
                echo "✅ Ошибок не найдено"
            fi
            ;;
        "tail"|"t")
            echo "👁️ Следим за общими логами в реальном времени (Ctrl+C для остановки):"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            tail -f "$GENERAL_LOG" 2>/dev/null || echo "❌ Файл не найден"
            ;;
        "tail-errors"|"te")
            echo "🚨 Следим за ошибками в реальном времени (Ctrl+C для остановки):"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            tail -f "$ERROR_LOG" 2>/dev/null || echo "❌ Файл не найден"
            ;;
        "stats"|"s")
            show_stats
            ;;
        "search")
            if [[ -n "$args" ]]; then
                echo "🔍 Поиск '$args' в общих логах:"
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                grep --color=always "$args" "$GENERAL_LOG" 2>/dev/null || echo "❌ Ничего не найдено"
            else
                echo "❌ Укажите поисковый запрос"
            fi
            ;;
        "help"|"h")
            show_help
            ;;
        "quit"|"q")
            echo "👋 До свидания!"
            break
            ;;
        "")
            # Пустая команда, игнорируем
            ;;
        *)
            echo "❌ Неизвестная команда: $command"
            echo "Введите 'help' для справки"
            ;;
    esac
    echo ""
done