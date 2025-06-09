import pandas as pd
import numpy as np
from typing import Union, Optional, Any, List, Dict
from datetime import datetime, timedelta
import re


def format_number(value: Union[int, float], decimal_places: int = 0) -> str:
    """
    Форматирование числа с разделителями тысяч
    
    Args:
        value: Число для форматирования
        decimal_places: Количество знаков после запятой
    
    Returns:
        Отформатированная строка
    """
    if pd.isna(value) or value is None:
        return "N/A"
    
    try:
        if decimal_places == 0:
            return f"{int(value):,}".replace(",", " ")
        else:
            return f"{float(value):,.{decimal_places}f}".replace(",", " ")
    except (ValueError, TypeError):
        return str(value)


def format_currency(value: Union[int, float], currency: str = "₽", decimal_places: int = 0) -> str:
    """
    Форматирование валютных значений
    
    Args:
        value: Сумма
        currency: Символ валюты
        decimal_places: Количество знаков после запятой
    
    Returns:
        Отформатированная валютная строка
    """
    if pd.isna(value) or value is None:
        return f"N/A {currency}"
    
    try:
        formatted_number = format_number(value, decimal_places)
        return f"{formatted_number} {currency}"
    except (ValueError, TypeError):
        return f"{value} {currency}"


def format_percentage(value: Union[int, float], decimal_places: int = 1, show_sign: bool = False) -> str:
    """
    Форматирование процентных значений
    
    Args:
        value: Процентное значение
        decimal_places: Количество знаков после запятой
        show_sign: Показывать знак + для положительных значений
    
    Returns:
        Отформатированная процентная строка
    """
    if pd.isna(value) or value is None:
        return "N/A%"
    
    try:
        if show_sign and value > 0:
            return f"+{value:.{decimal_places}f}%"
        else:
            return f"{value:.{decimal_places}f}%"
    except (ValueError, TypeError):
        return f"{value}%"


def get_month_name(month_number: int, lang: str = "ru") -> str:
    """
    Получение названия месяца по номеру
    
    Args:
        month_number: Номер месяца (1-12)
        lang: Язык ('ru' или 'en')
    
    Returns:
        Название месяца
    """
    month_names = {
        "ru": {
            1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
            5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
            9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
        },
        "en": {
            1: "January", 2: "February", 3: "March", 4: "April",
            5: "May", 6: "June", 7: "July", 8: "August",
            9: "September", 10: "October", 11: "November", 12: "December"
        }
    }
    
    return month_names.get(lang, month_names["ru"]).get(month_number, f"Month {month_number}")


def get_season_name(month_number: int, lang: str = "ru") -> str:
    """
    Определение сезона по номеру месяца
    
    Args:
        month_number: Номер месяца (1-12)
        lang: Язык ('ru' или 'en')
    
    Returns:
        Название сезона
    """
    season_mapping = {
        "ru": {
            12: "Зима", 1: "Зима", 2: "Зима",
            3: "Весна", 4: "Весна", 5: "Весна",
            6: "Лето", 7: "Лето", 8: "Лето",
            9: "Осень", 10: "Осень", 11: "Осень"
        },
        "en": {
            12: "Winter", 1: "Winter", 2: "Winter",
            3: "Spring", 4: "Spring", 5: "Spring",
            6: "Summer", 7: "Summer", 8: "Summer",
            9: "Autumn", 10: "Autumn", 11: "Autumn"
        }
    }
    
    return season_mapping.get(lang, season_mapping["ru"]).get(month_number, "Unknown")


def calculate_yoy_change(current_value: float, previous_value: float) -> Optional[float]:
    """
    Расчет изменения год к году (YoY)
    
    Args:
        current_value: Текущее значение
        previous_value: Значение предыдущего периода
    
    Returns:
        Процентное изменение или None если расчет невозможен
    """
    if pd.isna(current_value) or pd.isna(previous_value) or previous_value == 0:
        return None
    
    try:
        return ((current_value - previous_value) / previous_value) * 100
    except (TypeError, ZeroDivisionError):
        return None


def safe_divide(numerator: Union[int, float], denominator: Union[int, float], default: float = 0) -> float:
    """
    Безопасное деление с обработкой деления на ноль
    
    Args:
        numerator: Числитель
        denominator: Знаменатель
        default: Значение по умолчанию при делении на ноль
    
    Returns:
        Результат деления или значение по умолчанию
    """
    if pd.isna(numerator) or pd.isna(denominator) or denominator == 0:
        return default
    
    try:
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default


def clean_text(text: str) -> str:
    """
    Очистка текста от лишних символов и пробелов
    
    Args:
        text: Исходный текст
    
    Returns:
        Очищенный текст
    """
    if not isinstance(text, str):
        return str(text) if text is not None else ""
    
    # Удаляем лишние пробелы
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Удаляем специальные символы (опционально)
    # text = re.sub(r'[^\w\s\-\.\,\(\)]', '', text)
    
    return text


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Нормализация названий колонок датафрейма
    
    Args:
        df: Исходный датафрейм
    
    Returns:
        Датафрейм с нормализованными названиями колонок
    """
    df_copy = df.copy()
    
    # Удаляем лишние пробелы
    df_copy.columns = df_copy.columns.str.strip()
    
    # Заменяем множественные пробелы на одинарные
    df_copy.columns = [re.sub(r'\s+', ' ', col) for col in df_copy.columns]
    
    return df_copy


def detect_outliers(series: pd.Series, method: str = "iqr", threshold: float = 1.5) -> pd.Series:
    """
    Определение выбросов в серии данных
    
    Args:
        series: Серия данных для анализа
        method: Метод определения выбросов ('iqr' или 'zscore')
        threshold: Пороговое значение
    
    Returns:
        Булева серия с отметками выбросов
    """
    if method == "iqr":
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        return (series < lower_bound) | (series > upper_bound)
    
    elif method == "zscore":
        z_scores = np.abs((series - series.mean()) / series.std())
        return z_scores > threshold
    
    else:
        raise ValueError("Method must be 'iqr' or 'zscore'")


def calculate_moving_average(series: pd.Series, window: int = 7, center: bool = True) -> pd.Series:
    """
    Расчет скользящего среднего
    
    Args:
        series: Серия данных
        window: Размер окна
        center: Центрировать ли окно
    
    Returns:
        Серия со скользящим средним
    """
    return series.rolling(window=window, center=center).mean()


def interpolate_missing_values(series: pd.Series, method: str = "linear") -> pd.Series:
    """
    Интерполяция пропущенных значений
    
    Args:
        series: Серия с пропущенными значениями
        method: Метод интерполяции
    
    Returns:
        Серия с заполненными значениями
    """
    return series.interpolate(method=method)


def calculate_correlation_matrix(df: pd.DataFrame, numeric_only: bool = True) -> pd.DataFrame:
    """
    Расчет матрицы корреляций
    
    Args:
        df: Датафрейм для анализа
        numeric_only: Использовать только числовые колонки
    
    Returns:
        Матрица корреляций
    """
    if numeric_only:
        numeric_df = df.select_dtypes(include=[np.number])
        return numeric_df.corr()
    else:
        return df.corr()


def group_by_period(df: pd.DataFrame, date_column: str, period: str = "M") -> pd.DataFrame:
    """
    Группировка данных по временным периодам
    
    Args:
        df: Исходный датафрейм
        date_column: Название колонки с датами
        period: Период группировки ('D', 'W', 'M', 'Q', 'Y')
    
    Returns:
        Сгруппированный датафрейм
    """
    df_copy = df.copy()
    df_copy[date_column] = pd.to_datetime(df_copy[date_column])
    df_copy.set_index(date_column, inplace=True)
    
    return df_copy.resample(period).agg({
        col: 'sum' if df_copy[col].dtype in ['int64', 'float64'] else 'first'
        for col in df_copy.columns
    })


def calculate_growth_rate(values: List[float], periods: int = 1) -> List[float]:
    """
    Расчет темпов роста
    
    Args:
        values: Список значений
        periods: Количество периодов для сравнения
    
    Returns:
        Список темпов роста
    """
    if len(values) < periods + 1:
        return []
    
    growth_rates = []
    for i in range(periods, len(values)):
        current = values[i]
        previous = values[i - periods]
        
        if previous != 0:
            growth_rate = ((current - previous) / previous) * 100
            growth_rates.append(growth_rate)
        else:
            growth_rates.append(0)
    
    return growth_rates


def find_peaks_and_valleys(series: pd.Series, prominence: float = 0.1) -> Dict[str, List[int]]:
    """
    Поиск пиков и впадин в серии данных
    
    Args:
        series: Серия данных
        prominence: Минимальная выраженность пика
    
    Returns:
        Словарь с индексами пиков и впадин
    """
    try:
        from scipy.signal import find_peaks
        
        # Нормализуем данные
        normalized = (series - series.min()) / (series.max() - series.min())
        
        # Находим пики
        peaks, _ = find_peaks(normalized, prominence=prominence)
        
        # Находим впадины (инвертируем серию)
        valleys, _ = find_peaks(-normalized, prominence=prominence)
        
        return {
            "peaks": peaks.tolist(),
            "valleys": valleys.tolist()
        }
    
    except ImportError:
        # Простая реализация без scipy
        peaks = []
        valleys = []
        
        for i in range(1, len(series) - 1):
            if series.iloc[i] > series.iloc[i-1] and series.iloc[i] > series.iloc[i+1]:
                peaks.append(i)
            elif series.iloc[i] < series.iloc[i-1] and series.iloc[i] < series.iloc[i+1]:
                valleys.append(i)
        
        return {"peaks": peaks, "valleys": valleys}


def calculate_seasonal_decomposition(series: pd.Series, period: int = 12) -> Dict[str, pd.Series]:
    """
    Сезонная декомпозиция временного ряда
    
    Args:
        series: Временной ряд
        period: Период сезонности
    
    Returns:
        Словарь с компонентами разложения
    """
    try:
        from statsmodels.tsa.seasonal import seasonal_decompose
        
        decomposition = seasonal_decompose(series, model='additive', period=period)
        
        return {
            "trend": decomposition.trend,
            "seasonal": decomposition.seasonal,
            "residual": decomposition.resid,
            "observed": decomposition.observed
        }
    
    except ImportError:
        # Простая реализация тренда
        trend = series.rolling(window=period, center=True).mean()
        seasonal = series - trend
        residual = series - trend - seasonal
        
        return {
            "trend": trend,
            "seasonal": seasonal,
            "residual": residual,
            "observed": series
        }


def validate_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Анализ качества данных
    
    Args:
        df: Датафрейм для анализа
    
    Returns:
        Отчет о качестве данных
    """
    quality_report = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "missing_values": {},
        "duplicate_rows": df.duplicated().sum(),
        "data_types": {},
        "memory_usage": df.memory_usage(deep=True).sum(),
        "quality_score": 0
    }
    
    # Анализ пропущенных значений
    for column in df.columns:
        missing_count = df[column].isna().sum()
        missing_percentage = (missing_count / len(df)) * 100
        quality_report["missing_values"][column] = {
            "count": missing_count,
            "percentage": missing_percentage
        }
    
    # Анализ типов данных
    for column in df.columns:
        quality_report["data_types"][column] = str(df[column].dtype)
    
    # Расчет общего балла качества
    total_missing_percentage = sum(
        info["percentage"] for info in quality_report["missing_values"].values()
    ) / len(df.columns)
    
    duplicate_percentage = (quality_report["duplicate_rows"] / len(df)) * 100
    
    quality_score = max(0, 100 - total_missing_percentage - duplicate_percentage)
    quality_report["quality_score"] = round(quality_score, 2)
    
    return quality_report


def create_date_features(df: pd.DataFrame, date_column: str) -> pd.DataFrame:
    """
    Создание дополнительных признаков из даты
    
    Args:
        df: Исходный датафрейм
        date_column: Название колонки с датой
    
    Returns:
        Датафрейм с дополнительными признаками
    """
    df_copy = df.copy()
    df_copy[date_column] = pd.to_datetime(df_copy[date_column])
    
    # Базовые признаки
    df_copy[f"{date_column}_year"] = df_copy[date_column].dt.year
    df_copy[f"{date_column}_month"] = df_copy[date_column].dt.month
    df_copy[f"{date_column}_day"] = df_copy[date_column].dt.day
    df_copy[f"{date_column}_weekday"] = df_copy[date_column].dt.weekday
    df_copy[f"{date_column}_quarter"] = df_copy[date_column].dt.quarter
    
    # Дополнительные признаки
    df_copy[f"{date_column}_is_weekend"] = df_copy[date_column].dt.weekday >= 5
    df_copy[f"{date_column}_day_of_year"] = df_copy[date_column].dt.dayofyear
    df_copy[f"{date_column}_week_of_year"] = df_copy[date_column].dt.isocalendar().week
    
    # Сезонные признаки
    df_copy[f"{date_column}_season"] = df_copy[f"{date_column}_month"].apply(
        lambda x: get_season_name(x)
    )
    
    return df_copy


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Обрезка текста до указанной длины
    
    Args:
        text: Исходный текст
        max_length: Максимальная длина
        suffix: Суффикс для обрезанного текста
    
    Returns:
        Обрезанный текст
    """
    if not isinstance(text, str):
        text = str(text)
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
