import pandas as pd
import streamlit as st
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from config import DATA_FIELDS


class DataValidator:
    """Класс для валидации загруженных данных MPStats"""
    
    def __init__(self):
        self.validation_results = {}
        self.warnings = []
        self.errors = []
    
    def validate_all_data(self, loaded_data: Dict[str, pd.DataFrame]) -> Dict[str, dict]:
        """Валидация всех загруженных данных"""
        validation_results = {}
        
        for data_type, df in loaded_data.items():
            validation_results[data_type] = self._validate_by_type(df, data_type)
        
        self.validation_results = validation_results
        return validation_results
    
    def _validate_by_type(self, df: pd.DataFrame, data_type: str) -> dict:
        """Валидация данных по типу"""
        
        if data_type == "trends":
            return self._validate_trends_data(df)
        elif data_type == "queries":
            return self._validate_queries_data(df)
        elif data_type == "price":
            return self._validate_price_data(df)
        elif data_type == "days":
            return self._validate_days_data(df)
        elif data_type == "products":
            return self._validate_products_data(df)
        else:
            return {"valid": True, "warnings": [], "errors": []}
    
    def _validate_trends_data(self, df: pd.DataFrame) -> dict:
        """Валидация данных трендов"""
        warnings = []
        errors = []
        
        try:
            # Проверяем обязательные колонки
            required_columns = DATA_FIELDS["trends"]
            missing_cols = []
            for field_key, col_name in required_columns.items():
                if col_name not in df.columns:
                    missing_cols.append(col_name)
            
            if missing_cols:
                errors.append(f"Отсутствуют обязательные колонки: {', '.join(missing_cols)}")
            
            # Проверяем даты
            if "Месяц" in df.columns:
                invalid_dates = df["Месяц"].isna().sum()
                if invalid_dates > 0:
                    warnings.append(f"Найдено {invalid_dates} записей с некорректными датами")
                
                # Проверяем диапазон дат
                if not df["Месяц"].isna().all():
                    min_date = df["Месяц"].min()
                    max_date = df["Месяц"].max()
                    date_range = (max_date - min_date).days
                    
                    if date_range < 30:
                        warnings.append("Период данных менее месяца - анализ может быть неточным")
                    elif date_range > 1095:  # 3 года
                        warnings.append("Период данных более 3 лет - рекомендуется анализировать более свежие данные")
            
            # Проверяем числовые значения
            numeric_columns = ["Продажи", "Выручка, ₽", "Товары", "Бренды"]
            for col in numeric_columns:
                if col in df.columns:
                    negative_values = (df[col] < 0).sum()
                    if negative_values > 0:
                        warnings.append(f"Найдено {negative_values} отрицательных значений в колонке '{col}'")
                    
                    zero_values = (df[col] == 0).sum()
                    if zero_values > len(df) * 0.5:  # Более 50% нулевых значений
                        warnings.append(f"Более 50% нулевых значений в колонке '{col}'")
            
            # Проверяем логическую согласованность
            if all(col in df.columns for col in ["Товары", "Товары с продажами"]):
                inconsistent = (df["Товары с продажами"] > df["Товары"]).sum()
                if inconsistent > 0:
                    errors.append(f"Найдено {inconsistent} записей, где товаров с продажами больше общего количества товаров")
            
        except Exception as e:
            errors.append(f"Ошибка при валидации данных трендов: {str(e)}")
        
        return {
            "valid": len(errors) == 0,
            "warnings": warnings,
            "errors": errors,
            "records_count": len(df),
            "date_range": self._get_date_range(df, "Месяц") if "Месяц" in df.columns else None
        }
    
    def _validate_queries_data(self, df: pd.DataFrame) -> dict:
        """Валидация данных запросов"""
        warnings = []
        errors = []
        
        try:
            # Проверяем обязательные колонки
            required_columns = ["Ключевое слово", "Частота WB", "Товаров в запросе"]
            missing_cols = [col for col in required_columns if col not in df.columns]
            
            if missing_cols:
                errors.append(f"Отсутствуют обязательные колонки: {', '.join(missing_cols)}")
            
            # Проверяем качество данных
            if "Ключевое слово" in df.columns:
                empty_keywords = df["Ключевое слово"].isna().sum()
                if empty_keywords > 0:
                    warnings.append(f"Найдено {empty_keywords} пустых ключевых слов")
                
                # Проверяем дубликаты
                duplicates = df["Ключевое слово"].duplicated().sum()
                if duplicates > 0:
                    warnings.append(f"Найдено {duplicates} дублирующихся ключевых слов")
            
            # Проверяем числовые значения
            if "Частота WB" in df.columns:
                zero_frequency = (df["Частота WB"] == 0).sum()
                if zero_frequency > 0:
                    warnings.append(f"Найдено {zero_frequency} запросов с нулевой частотой")
                
                negative_frequency = (df["Частота WB"] < 0).sum()
                if negative_frequency > 0:
                    errors.append(f"Найдено {negative_frequency} запросов с отрицательной частотой")
            
            if "Товаров в запросе" in df.columns:
                zero_products = (df["Товаров в запросе"] == 0).sum()
                if zero_products > 0:
                    warnings.append(f"Найдено {zero_products} запросов без товаров")
            
            # Проверяем эффективные запросы
            if all(col in df.columns for col in ["Частота WB", "Товаров в запросе"]):
                effective_queries = len(df[df["Коэффициент_спрос_предложение"] >= 2.0])
                if effective_queries == 0:
                    warnings.append("Не найдено эффективных запросов (коэффициент ≥ 2.0)")
                elif effective_queries < 10:
                    warnings.append(f"Найдено мало эффективных запросов: {effective_queries}")
        
        except Exception as e:
            errors.append(f"Ошибка при валидации данных запросов: {str(e)}")
        
        return {
            "valid": len(errors) == 0,
            "warnings": warnings,
            "errors": errors,
            "records_count": len(df),
            "effective_queries": len(df[df["Коэффициент_спрос_предложение"] >= 2.0]) if "Коэффициент_спрос_предложение" in df.columns else 0
        }
    
    def _validate_price_data(self, df: pd.DataFrame) -> dict:
        """Валидация данных ценовой сегментации"""
        warnings = []
        errors = []
        
        try:
            # Проверяем обязательные колонки
            required_columns = ["От", "До", "Выручка на товар, ₽"]
            missing_cols = [col for col in required_columns if col not in df.columns]
            
            if missing_cols:
                errors.append(f"Отсутствуют обязательные колонки: {', '.join(missing_cols)}")
                return {
                    "valid": False,
                    "warnings": warnings,
                    "errors": errors,
                    "records_count": len(df)
                }
            
            # Проверяем ценовые диапазоны
            if all(col in df.columns for col in ["От", "До"]):
                # Проверяем, что значения числовые
                non_numeric_from = df['От'].isna().sum()
                non_numeric_to = df['До'].isna().sum()
                
                if non_numeric_from > 0:
                    errors.append(f"Найдено {non_numeric_from} нечисловых значений в колонке 'От'")
                
                if non_numeric_to > 0:
                    errors.append(f"Найдено {non_numeric_to} нечисловых значений в колонке 'До'")
                
                # Проверяем корректность диапазонов только для числовых значений
                valid_rows = df.dropna(subset=['От', 'До'])
                if len(valid_rows) > 0:
                    invalid_ranges = (valid_rows["От"] >= valid_rows["До"]).sum()
                    if invalid_ranges > 0:
                        errors.append(f"Найдено {invalid_ranges} некорректных ценовых диапазонов (От >= До)")
                    
                    # Проверяем перекрытия диапазонов
                    df_sorted = valid_rows.sort_values("От")
                    overlaps = 0
                    for i in range(len(df_sorted) - 1):
                        if df_sorted.iloc[i]["До"] > df_sorted.iloc[i + 1]["От"]:
                            overlaps += 1
                    
                    if overlaps > 0:
                        warnings.append(f"Найдено {overlaps} перекрывающихся ценовых диапазонов")
            
            # Проверяем выручку на товар
            if "Выручка на товар, ₽" in df.columns:
                zero_revenue = (df["Выручка на товар, ₽"] == 0).sum()
                if zero_revenue > 0:
                    warnings.append(f"Найдено {zero_revenue} сегментов с нулевой выручкой на товар")
                
                negative_revenue = (df["Выручка на товар, ₽"] < 0).sum()
                if negative_revenue > 0:
                    errors.append(f"Найдено {negative_revenue} сегментов с отрицательной выручкой")
            
            # Проверяем логическую согласованность
            if all(col in df.columns for col in ["Товары", "Товары с продажами"]):
                valid_products_data = df.dropna(subset=["Товары", "Товары с продажами"])
                if len(valid_products_data) > 0:
                    inconsistent = (valid_products_data["Товары с продажами"] > valid_products_data["Товары"]).sum()
                    if inconsistent > 0:
                        errors.append(f"Найдено {inconsistent} сегментов с некорректным соотношением товаров")
        
        except Exception as e:
            errors.append(f"Ошибка при валидации данных ценовой сегментации: {str(e)}")
        
        return {
            "valid": len(errors) == 0,
            "warnings": warnings,
            "errors": errors,
            "records_count": len(df),
            "price_range": (df["От"].min(), df["До"].max()) if all(col in df.columns for col in ["От", "До"]) and len(df) > 0 else None
        }
    
    def _validate_days_data(self, df: pd.DataFrame) -> dict:
        """Валидация данных по дням"""
        warnings = []
        errors = []
        
        try:
            # Проверяем обязательные колонки
            required_columns = ["Дата", "Остаток"]
            missing_cols = [col for col in required_columns if col not in df.columns]
            
            if missing_cols:
                errors.append(f"Отсутствуют обязательные колонки: {', '.join(missing_cols)}")
            
            # Проверяем даты
            if "Дата" in df.columns:
                invalid_dates = df["Дата"].isna().sum()
                if invalid_dates > 0:
                    warnings.append(f"Найдено {invalid_dates} записей с некорректными датами")
                
                # Проверяем непрерывность дат
                if not df["Дата"].isna().all():
                    df_sorted = df.sort_values("Дата")
                    date_gaps = 0
                    for i in range(len(df_sorted) - 1):
                        diff = (df_sorted.iloc[i + 1]["Дата"] - df_sorted.iloc[i]["Дата"]).days
                        if diff > 1:
                            date_gaps += 1
                    
                    if date_gaps > 0:
                        warnings.append(f"Найдено {date_gaps} пропусков в датах")
            
            # Проверяем остатки
            if "Остаток" in df.columns:
                negative_stock = (df["Остаток"] < 0).sum()
                if negative_stock > 0:
                    warnings.append(f"Найдено {negative_stock} записей с отрицательными остатками")
                
                zero_stock_days = (df["Остаток"] == 0).sum()
                total_days = len(df)
                if zero_stock_days > total_days * 0.3:  # Более 30% дней без остатков
                    warnings.append(f"Более 30% дней без остатков на складе ({zero_stock_days} из {total_days})")
        
        except Exception as e:
            errors.append(f"Ошибка при валидации данных по дням: {str(e)}")
        
        return {
            "valid": len(errors) == 0,
            "warnings": warnings,
            "errors": errors,
            "records_count": len(df),
            "date_range": self._get_date_range(df, "Дата") if "Дата" in df.columns else None
        }
    
    def _validate_products_data(self, df: pd.DataFrame) -> dict:
        """Валидация данных товаров"""
        warnings = []
        errors = []
        
        try:
            # Проверяем обязательные колонки
            required_columns = ["SKU", "Final price", "Category position avg"]
            missing_cols = [col for col in required_columns if col not in df.columns]
            
            if missing_cols:
                errors.append(f"Отсутствуют обязательные колонки: {', '.join(missing_cols)}")
            
            # Проверяем SKU
            if "SKU" in df.columns:
                empty_sku = df["SKU"].isna().sum()
                if empty_sku > 0:
                    warnings.append(f"Найдено {empty_sku} товаров без SKU")
                
                duplicate_sku = df["SKU"].duplicated().sum()
                if duplicate_sku > 0:
                    warnings.append(f"Найдено {duplicate_sku} дублирующихся SKU")
            
            # Проверяем цены
            if "Final price" in df.columns:
                zero_price = (df["Final price"] == 0).sum()
                if zero_price > 0:
                    warnings.append(f"Найдено {zero_price} товаров с нулевой ценой")
                
                negative_price = (df["Final price"] < 0).sum()
                if negative_price > 0:
                    errors.append(f"Найдено {negative_price} товаров с отрицательной ценой")
            
            # Проверяем рекламные данные
            if "Search cpm avg" in df.columns:
                ads_products = (df["Search cpm avg"] > 0).sum()
                total_products = len(df)
                ads_percentage = (ads_products / total_products) * 100
                
                if ads_percentage < 10:
                    warnings.append(f"Мало товаров с рекламой: {ads_percentage:.1f}%")
                elif ads_percentage > 90:
                    warnings.append(f"Слишком много товаров с рекламой: {ads_percentage:.1f}% - возможна высокая конкуренция")
            
            # Проверяем позиции в категории
            if "Category position avg" in df.columns:
                top_10 = (df["Category position avg"] <= 10).sum()
                top_100 = (df["Category position avg"] <= 100).sum()
                
                if top_10 == 0:
                    warnings.append("Нет товаров в топ-10 категории")
                if top_100 < 10:
                    warnings.append(f"Мало товаров в топ-100: {top_100}")
        
        except Exception as e:
            errors.append(f"Ошибка при валидации данных товаров: {str(e)}")
        
        return {
            "valid": len(errors) == 0,
            "warnings": warnings,
            "errors": errors,
            "records_count": len(df),
            "top_10_count": (df["Category position avg"] <= 10).sum() if "Category position avg" in df.columns else 0,
            "top_100_count": (df["Category position avg"] <= 100).sum() if "Category position avg" in df.columns else 0
        }
    
    def _get_date_range(self, df: pd.DataFrame, date_column: str) -> Optional[Tuple[str, str]]:
        """Получение диапазона дат"""
        try:
            if date_column in df.columns and not df[date_column].isna().all():
                min_date = df[date_column].min()
                max_date = df[date_column].max()
                return (min_date.strftime("%Y-%m-%d"), max_date.strftime("%Y-%m-%d"))
        except:
            pass
        return None
    
    def get_validation_summary(self) -> dict:
        """Получение сводки по валидации"""
        total_errors = sum(len(result.get("errors", [])) for result in self.validation_results.values())
        total_warnings = sum(len(result.get("warnings", [])) for result in self.validation_results.values())
        
        return {
            "total_files": len(self.validation_results),
            "valid_files": sum(1 for result in self.validation_results.values() if result.get("valid", False)),
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "files_with_errors": [file_type for file_type, result in self.validation_results.items() if not result.get("valid", True)],
            "overall_valid": total_errors == 0
        }
    
    def display_validation_results(self):
        """Отображение результатов валидации в Streamlit"""
        if not self.validation_results:
            return
        
        summary = self.get_validation_summary()
        
        # Общая сводка
        if summary["overall_valid"]:
            st.success(f"✅ Все файлы прошли валидацию успешно ({summary['total_files']} файлов)")
        else:
            st.error(f"❌ Найдены ошибки в {len(summary['files_with_errors'])} файлах")
        
        if summary["total_warnings"] > 0:
            st.warning(f"⚠️ Общее количество предупреждений: {summary['total_warnings']}")
        
        # Детальные результаты по каждому файлу
        for file_type, result in self.validation_results.items():
            with st.expander(f"📄 Результаты валидации: {file_type}"):
                
                if result["valid"]:
                    st.success("✅ Файл прошел валидацию")
                else:
                    st.error("❌ Файл содержит ошибки")
                
                # Основная информация
                st.info(f"📊 Количество записей: {result['records_count']}")
                
                if "date_range" in result and result["date_range"]:
                    st.info(f"📅 Период данных: {result['date_range'][0]} — {result['date_range'][1]}")
                
                # Ошибки
                if result["errors"]:
                    st.error("**Ошибки:**")
                    for error in result["errors"]:
                        st.error(f"• {error}")
                
                # Предупреждения
                if result["warnings"]:
                    st.warning("**Предупреждения:**")
                    for warning in result["warnings"]:
                        st.warning(f"• {warning}")
