# Константы для MPStats Analyzer

# Названия месяцев
MONTH_NAMES = {
    "ru": {
        1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
        5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
        9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
    },
    "en": {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    },
    "short_ru": {
        1: "Янв", 2: "Фев", 3: "Мар", 4: "Апр",
        5: "Май", 6: "Июн", 7: "Июл", 8: "Авг",
        9: "Сен", 10: "Окт", 11: "Ноя", 12: "Дек"
    }
}

# Сезонная группировка месяцев
SEASON_MAPPING = {
    "winter": [12, 1, 2],
    "spring": [3, 4, 5],
    "summer": [6, 7, 8],
    "autumn": [9, 10, 11]
}

SEASON_NAMES = {
    "ru": {
        "winter": "Зима",
        "spring": "Весна", 
        "summer": "Лето",
        "autumn": "Осень"
    },
    "en": {
        "winter": "Winter",
        "spring": "Spring",
        "summer": "Summer", 
        "autumn": "Autumn"
    }
}

# Цветовые схемы
DEFAULT_COLORS = [
    '#1f77b4',  # Синий
    '#ff7f0e',  # Оранжевый
    '#2ca02c',  # Зеленый
    '#d62728',  # Красный
    '#9467bd',  # Фиолетовый
    '#8c564b',  # Коричневый
    '#e377c2',  # Розовый
    '#7f7f7f',  # Серый
    '#bcbd22',  # Оливковый
    '#17becf'   # Бирюзовый
]

SCORE_COLORS = {
    "excellent": "#28a745",  # Зеленый
    "good": "#ffc107",       # Желтый
    "average": "#fd7e14",    # Оранжевый  
    "poor": "#dc3545",       # Красный
    "critical": "#6c757d"    # Серый
}

GRADIENT_COLORS = {
    "success": ["#56ab2f", "#a8e6cf"],
    "warning": ["#f093fb", "#f5576c"],
    "info": ["#4facfe", "#00f2fe"],
    "primary": ["#667eea", "#764ba2"],
    "dark": ["#2c3e50", "#34495e"]
}

# Конфигурации графиков
CHART_CONFIGS = {
    "default_height": 400,
    "default_width": None,
    "font_family": "Arial, sans-serif",
    "font_size": 12,
    "margin": {
        "l": 50,
        "r": 50, 
        "t": 60,
        "b": 50
    },
    "grid_color": "rgba(128,128,128,0.2)",
    "line_color": "rgba(128,128,128,0.5)"
}

CHART_THEMES = {
    "modern": {
        "bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font_color": "#333",
        "grid_color": "rgba(128,128,128,0.2)",
        "line_color": "rgba(128,128,128,0.5)"
    },
    "dark": {
        "bgcolor": "rgba(20,20,20,1)",
        "plot_bgcolor": "rgba(30,30,30,1)",
        "font_color": "#fff",
        "grid_color": "rgba(128,128,128,0.3)",
        "line_color": "rgba(128,128,128,0.5)"
    },
    "clean": {
        "bgcolor": "#ffffff",
        "plot_bgcolor": "#ffffff",
        "font_color": "#333",
        "grid_color": "rgba(0,0,0,0.1)",
        "line_color": "rgba(0,0,0,0.2)"
    }
}

# Иконки для модулей анализа
MODULE_ICONS = {
    "trends": "📈",
    "queries": "🔍", 
    "price": "💰",
    "stock": "📦",
    "ads": "🎯",
    "dashboard": "📊",
    "settings": "⚙️",
    "export": "📤"
}

# Статусы и их конфигурация
STATUS_CONFIG = {
    "excellent": {
        "icon": "🟢",
        "emoji": "🚀",
        "color": "#28a745",
        "title": "Отлично",
        "description": "Высокий потенциал"
    },
    "good": {
        "icon": "🟡", 
        "emoji": "👍",
        "color": "#ffc107",
        "title": "Хорошо",
        "description": "Умеренный потенциал"
    },
    "average": {
        "icon": "🟠",
        "emoji": "⚠️", 
        "color": "#fd7e14",
        "title": "Средне",
        "description": "Требует анализа"
    },
    "poor": {
        "icon": "🔴",
        "emoji": "👎",
        "color": "#dc3545", 
        "title": "Плохо",
        "description": "Высокие риски"
    }
}

# Пороговые значения для различных метрик
THRESHOLDS = {
    "trend": {
        "excellent": 10.0,   # Рост более 10%
        "good": 0.0,         # Рост 0-10%
        "stable": -5.0,      # Изменение от -5% до 0%
        "poor": -15.0        # Падение более 15%
    },
    "query": {
        "excellent": 5.0,    # Коэффициент > 5
        "good": 3.0,         # Коэффициент 3-5
        "average": 2.0,      # Коэффициент 2-3
        "poor": 1.0          # Коэффициент < 2
    },
    "ads": {
        "excellent": 4.0,    # Чек/Ставка > 4
        "good": 3.0,         # Чек/Ставка 3-4
        "average": 2.0,      # Чек/Ставка 2-3
        "poor": 1.0          # Чек/Ставка < 2
    },
    "price": {
        "high_efficiency": 80,    # Эффективность > 80%
        "medium_efficiency": 60,  # Эффективность 60-80%
        "low_efficiency": 40      # Эффективность < 60%
    },
    "stock": {
        "low_variation": 0.3,     # CV < 0.3
        "medium_variation": 0.5,  # CV 0.3-0.5
        "high_variation": 0.7,    # CV 0.5-0.7
        "stockout_critical": 30   # Дефициты > 30%
    }
}

# Единицы измерения
UNITS = {
    "currency": "₽",
    "percentage": "%",
    "pieces": "шт.",
    "days": "дн.",
    "hours": "ч.",
    "count": "",
    "ratio": "x"
}

# Форматы чисел
NUMBER_FORMATS = {
    "integer": "{:,.0f}",
    "decimal_1": "{:,.1f}",
    "decimal_2": "{:,.2f}",
    "percentage_0": "{:.0f}%",
    "percentage_1": "{:.1f}%",
    "percentage_2": "{:.2f}%",
    "currency_0": "{:,.0f} ₽",
    "currency_2": "{:,.2f} ₽",
    "large_number": "{:,.0f}",
    "compact": "{:.1f}K" # Для больших чисел
}

# Сообщения об ошибках
ERROR_MESSAGES = {
    "file_not_found": "Файл не найден или поврежден",
    "invalid_format": "Неверный формат файла",
    "missing_columns": "Отсутствуют обязательные колонки",
    "no_data": "Нет данных для анализа",
    "calculation_error": "Ошибка в расчетах",
    "validation_failed": "Валидация данных не пройдена",
    "export_failed": "Ошибка при экспорте данных"
}

# Предупреждения
WARNING_MESSAGES = {
    "insufficient_data": "Недостаточно данных для точного анализа",
    "old_data": "Данные устарели, рекомендуется обновить",
    "missing_optional": "Отсутствуют опциональные данные",
    "low_quality": "Низкое качество данных",
    "outliers_detected": "Обнаружены выбросы в данных"
}

# Информационные сообщения
INFO_MESSAGES = {
    "analysis_complete": "Анализ успешно завершен",
    "data_loaded": "Данные успешно загружены",
    "validation_passed": "Валидация пройдена успешно",
    "export_ready": "Отчет готов к экспорту",
    "cache_cleared": "Кеш очищен"
}

# Рекомендации по действиям
ACTION_RECOMMENDATIONS = {
    "enter_niche": {
        "title": "Входить в нишу",
        "icon": "🟢",
        "description": "Ниша показывает высокий потенциал для входа"
    },
    "enter_cautiously": {
        "title": "Входить осторожно", 
        "icon": "🟡",
        "description": "Ниша имеет потенциал, но требует внимательного планирования"
    },
    "detailed_analysis": {
        "title": "Детальный анализ",
        "icon": "🟠", 
        "description": "Требуется дополнительное исследование конкурентов"
    },
    "avoid_niche": {
        "title": "Избегать ниши",
        "icon": "🔴",
        "description": "Ниша показывает высокие риски"
    }
}

# Конфигурация экспорта
EXPORT_CONFIG = {
    "excel": {
        "engine": "openpyxl",
        "sheet_names": {
            "summary": "Общая сводка",
            "trends": "Анализ трендов", 
            "queries": "Анализ запросов",
            "price": "Ценовая сегментация",
            "stock": "Анализ остатков",
            "ads": "Рекламный анализ",
            "recommendations": "Рекомендации"
        }
    },
    "pdf": {
        "page_size": "A4",
        "margins": {"top": 2, "bottom": 2, "left": 2, "right": 2},
        "font_size": 10
    }
}

# Настройки валидации данных
VALIDATION_CONFIG = {
    "min_records": {
        "trends": 3,     # Минимум 3 месяца
        "queries": 10,   # Минимум 10 запросов
        "price": 3,      # Минимум 3 сегмента
        "days": 30,      # Минимум 30 дней
        "products": 50   # Минимум 50 товаров
    },
    "max_missing_percentage": 20,  # Максимум 20% пропущенных значений
    "outlier_threshold": 3,        # Z-score для выбросов
    "date_range_days": 365         # Максимум год данных
}

# Метаданные для полей
FIELD_METADATA = {
    "trends": {
        "required": ["Месяц", "Продажи", "Выручка, ₽"],
        "numeric": ["Продажи", "Выручка, ₽", "Товары", "Бренды"],
        "date": ["Месяц"],
        "descriptions": {
            "Продажи": "Количество проданных единиц товара",
            "Выручка, ₽": "Общая выручка от продаж в рублях"
        }
    },
    "queries": {
        "required": ["Ключевое слово", "Частота WB", "Товаров в запросе"],
        "numeric": ["Частота WB", "Товаров в запросе"],
        "text": ["Ключевое слово"],
        "descriptions": {
            "Частота WB": "Количество поисков по запросу на WB",
            "Товаров в запросе": "Количество товаров в выдаче"
        }
    },
    "products": {
        "required": ["SKU", "Final price", "Category position avg"],
        "numeric": ["Final price", "Sales", "Revenue", "Category position avg", "Search cpm avg"],
        "text": ["Name", "Brand", "Category"],
        "descriptions": {
            "Final price": "Итоговая цена товара",
            "Category position avg": "Средняя позиция в категории"
        }
    }
}

# Справочная информация
HELP_TEXT = {
    "scoring": "Скоринг рассчитывается по 5 модулям, каждый дает от 0 до 4 баллов",
    "trends": "Анализирует динамику ключевых метрик ниши год к году",
    "queries": "Оценивает эффективность поисковых запросов через соотношение спрос/предложение",
    "price": "Определяет наиболее эффективные ценовые сегменты", 
    "stock": "Анализирует сезонность и управление запасами",
    "ads": "Оценивает конкуренцию в рекламе через коэффициент Чек/Ставка"
}

# Версионирование
VERSION_INFO = {
    "version": "1.0.0",
    "release_date": "2024-12-10",
    "author": "MPStats Analyzer Team",
    "description": "Инструмент для анализа ниш маркетплейса"
}
