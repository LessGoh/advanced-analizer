# Конфигурация MPStats Analyzer

# Настройки приложения
APP_TITLE = "MPStats Analyzer"
APP_ICON = "📊"
LAYOUT = "wide"

# Настройки скоринга
SCORING_CONFIG = {
    "trend_weight": 4,      # Максимальный балл за тренды
    "query_weight": 4,      # Максимальный балл за запросы  
    "price_weight": 4,      # Максимальный балл за ценовую сегментацию
    "stock_weight": 4,      # Максимальный балл за остатки
    "ads_weight": 4,        # Максимальный балл за рекламу
    "max_total_score": 20   # Максимальный общий балл
}

# Пороговые значения для трендов (YoY изменения в %)
TREND_THRESHOLDS = {
    "excellent": 10,    # Рост более 10% = 4 балла
    "good": 0,          # Рост 0-10% = 3 балла
    "stable": -5,       # Изменение от -5% до 0% = 2 балла
    "poor": -15         # Падение более 15% = 1 балл
}

# Пороговые значения для запросов (соотношение Частота WB / Товары в запросе)
QUERY_THRESHOLDS = {
    "excellent": 5.0,   # Коэффициент > 5 = 4 балла
    "good": 3.0,        # Коэффициент 3-5 = 3 балла
    "average": 2.0,     # Коэффициент 2-3 = 2 балла
    "poor": 1.0         # Коэффициент < 2 = 1 балл
}

# Пороговые значения для рекламы (коэффициент Чек/Ставка)
ADS_THRESHOLDS = {
    "excellent": 4.0,   # Коэффициент > 4 = 4 балла
    "good": 3.0,        # Коэффициент 3-4 = 3 балла
    "average": 2.0,     # Коэффициент 2-3 = 2 балла
    "poor": 1.0         # Коэффициент < 2 = 1 балл
}

# Названия файлов для автоматического распознавания
FILE_PATTERNS = {
    "trends": ["тренд", "trend"],
    "queries": ["запрос", "queries", "запросы"],
    "price": ["ценов", "price", "сегментац"],
    "days": ["дням", "days", "день"],
    "products": [".csv"]
}

# Ключевые поля в данных
DATA_FIELDS = {
    "trends": {
        "date": "Месяц",
        "sales": "Продажи", 
        "revenue": "Выручка, ₽",
        "products": "Товары",
        "products_with_sales": "Товары с продажами",
        "brands": "Бренды",
        "brands_with_sales": "Бренды с продажами",
        "sellers": "Продавцы",
        "sellers_with_sales": "Продавцы с продажами",
        "revenue_per_product": "Выручка на товар, ₽",
        "avg_check": "Средний чек, ₽"
    },
    "queries": {
        "keyword": "Ключевое слово",
        "cluster": "Кластер WB", 
        "frequency": "Частота WB",
        "products_in_query": "Товаров в запросе"
    },
    "price": {
        "price_from": "От",
        "price_to": "До",
        "sales": "Продажи",
        "revenue": "Выручка, ₽",
        "potential": "Потенциал, ₽",
        "lost_revenue": "Упущенная выручка, ₽",
        "lost_revenue_percent": "Упущенная выручка %",
        "products": "Товары",
        "products_with_sales": "Товары с продажами",
        "brands": "Бренды",
        "brands_with_sales": "Бренды с продажами",
        "sellers": "Продавцы",
        "sellers_with_sales": "Продавцы с продажами",
        "revenue_per_product": "Выручка на товар, ₽"
    },
    "days": {
        "date": "Дата",
        "products": "Товары",
        "products_with_sales": "Товары с продажами", 
        "sales": "Продажи, шт.",
        "revenue": "Выручка, ₽",
        "stock": "Остаток",
        "stock_price": "Цена остатка, ₽",
        "avg_price": "Средняя цена, ₽",
        "avg_sale_price": "Ср. цена продажи, ₽",
        "reviews": "Отзывы",
        "rating": "Рейтинг"
    },
    "products": {
        "sku": "SKU",
        "name": "Name",
        "category": "Category",
        "brand": "Brand",
        "seller": "Seller",
        "final_price": "Final price",
        "sales": "Sales",
        "revenue": "Revenue",
        "category_position": "Category position avg",
        "search_cpm": "Search cpm avg",
        "search_words_in_ads": "Search words in ads",
        "search_organic_position": "Search organic position avg",
        "search_position": "Search position avg",
        "search_words_count": "Search words count"
    }
}

# Цветовая схема для скоринга
SCORE_COLORS = {
    "excellent": "#28a745",  # Зеленый
    "good": "#ffc107",       # Желтый
    "average": "#fd7e14",    # Оранжевый  
    "poor": "#dc3545",       # Красный
    "critical": "#6c757d"    # Серый
}

# Границы скоринга для общей оценки
TOTAL_SCORE_RANGES = {
    "excellent": (16, 20),   # 16-20 баллов
    "good": (11, 15),        # 11-15 баллов  
    "average": (6, 10),      # 6-10 баллов
    "poor": (1, 5)           # 1-5 баллов
}
