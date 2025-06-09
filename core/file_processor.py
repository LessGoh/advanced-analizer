import pandas as pd
import streamlit as st
from typing import Dict, List, Optional, Tuple
import io
from config import FILE_PATTERNS, DATA_FIELDS


class FileProcessor:
    """Класс для загрузки и обработки файлов MPStats"""
    
    def __init__(self):
        self.loaded_data = {}
        self.file_info = {}
    
    def detect_file_type(self, filename: str) -> Optional[str]:
        """Определение типа файла по названию"""
        filename_lower = filename.lower()
        
        for file_type, patterns in FILE_PATTERNS.items():
            for pattern in patterns:
                if pattern in filename_lower:
                    return file_type
        return None
    
    def process_uploaded_files(self, uploaded_files: List) -> Dict[str, pd.DataFrame]:
        """Обработка загруженных файлов"""
        processed_data = {}
        
        for uploaded_file in uploaded_files:
            try:
                file_type = self.detect_file_type(uploaded_file.name)
                
                if file_type is None:
                    st.warning(f"⚠️ Не удалось определить тип файла: {uploaded_file.name}")
                    continue
                
                # Загрузка данных в зависимости от типа файла
                if uploaded_file.name.endswith('.csv'):
                    df = self._load_csv_file(uploaded_file)
                elif uploaded_file.name.endswith('.xlsx'):
                    df = self._load_excel_file(uploaded_file)
                else:
                    st.error(f"❌ Неподдерживаемый формат файла: {uploaded_file.name}")
                    continue
                
                # Обработка данных в зависимости от типа отчета
                processed_df = self._process_by_type(df, file_type)
                
                if processed_df is not None:
                    processed_data[file_type] = processed_df
                    self.file_info[file_type] = {
                        'filename': uploaded_file.name,
                        'rows': len(processed_df),
                        'columns': len(processed_df.columns)
                    }
                    st.success(f"✅ Загружен {file_type}: {uploaded_file.name} ({len(processed_df)} записей)")
                
            except Exception as e:
                st.error(f"❌ Ошибка при обработке {uploaded_file.name}: {str(e)}")
        
        self.loaded_data = processed_data
        return processed_data
    
    def _load_csv_file(self, uploaded_file) -> pd.DataFrame:
        """Загрузка CSV файла"""
        # Пробуем разные кодировки и разделители
        encodings = ['utf-8', 'cp1251', 'iso-8859-1']
        separators = [';', ',', '\t']
        
        for encoding in encodings:
            for separator in separators:
                try:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, sep=separator, encoding=encoding)
                    if len(df.columns) > 1:  # Проверяем, что разделитель правильный
                        return df
                except:
                    continue
        
        raise ValueError("Не удалось загрузить CSV файл с доступными кодировками и разделителями")
    
    def _load_excel_file(self, uploaded_file) -> pd.DataFrame:
        """Загрузка Excel файла"""
        try:
            # Сначала пробуем загрузить как обычный Excel
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            return df
        except Exception as e:
            # Если не получилось, пробуем указать конкретный лист
            try:
                uploaded_file.seek(0)
                df = pd.read_excel(uploaded_file, sheet_name=0, engine='openpyxl')
                return df
            except:
                raise ValueError(f"Не удалось загрузить Excel файл: {str(e)}")
    
    def _process_by_type(self, df: pd.DataFrame, file_type: str) -> Optional[pd.DataFrame]:
        """Обработка данных в зависимости от типа файла"""
        
        if file_type == "trends":
            return self._process_trends_data(df)
        elif file_type == "queries":
            return self._process_queries_data(df)
        elif file_type == "price":
            return self._process_price_data(df)
        elif file_type == "days":
            return self._process_days_data(df)
        elif file_type == "products":
            return self._process_products_data(df)
        else:
            return df
    
    def _process_trends_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Обработка данных трендов"""
        try:
            # Проверяем наличие ключевых колонок
            required_cols = ["Месяц", "Продажи", "Выручка, ₽"]
            if not all(col in df.columns for col in required_cols):
                st.warning("⚠️ В файле трендов отсутствуют необходимые колонки")
                return None
            
            # Преобразуем дату
            df['Месяц'] = pd.to_datetime(df['Месяц'], errors='coerce')
            
            # Добавляем год и месяц для анализа
            df['Год'] = df['Месяц'].dt.year
            df['Месяц_номер'] = df['Месяц'].dt.month
            
            # Очищаем данные от пустых строк
            df = df.dropna(subset=['Месяц'])
            
            return df
            
        except Exception as e:
            st.error(f"Ошибка при обработке данных трендов: {str(e)}")
            return None
    
    def _process_queries_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Обработка данных запросов"""
        try:
            # Проверяем наличие ключевых колонок
            required_cols = ["Ключевое слово", "Частота WB", "Товаров в запросе"]
            if not all(col in df.columns for col in required_cols):
                st.warning("⚠️ В файле запросов отсутствуют необходимые колонки")
                return None
            
            # Удаляем строки с пустыми значениями
            df = df.dropna(subset=required_cols)
            
            # Преобразуем числовые колонки
            df['Частота WB'] = pd.to_numeric(df['Частота WB'], errors='coerce')
            df['Товаров в запросе'] = pd.to_numeric(df['Товаров в запросе'], errors='coerce')
            
            # Рассчитываем коэффициент спрос/предложение
            df['Коэффициент_спрос_предложение'] = df['Частота WB'] / df['Товаров в запросе'].replace(0, 1)
            
            return df
            
        except Exception as e:
            st.error(f"Ошибка при обработке данных запросов: {str(e)}")
            return None
    
    def _process_price_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Обработка данных ценовой сегментации"""
        try:
            # Специальная обработка для файлов ценовой сегментации
            # В этих файлах первая строка содержит объединенные заголовки
            
            # Проверяем, есть ли объединенные заголовки в первой строке
            if len(df.columns) > 10 and (df.iloc[0].isna().any() or df.iloc[0, 0] == "Диапазон цен"):
                # Пропускаем первую строку с объединенными заголовками
                # Используем вторую строку как заголовки
                if len(df) > 1:
                    new_headers = df.iloc[1].tolist()
                    df = df.iloc[2:].reset_index(drop=True)  # Берем данные начиная с 3-й строки
                    df.columns = new_headers
                else:
                    st.warning("⚠️ Файл ценовой сегментации пустой или содержит только заголовки")
                    return None
            
            # Если структура не соответствует ожидаемой, пробуем альтернативный подход
            if 'От' not in df.columns or 'До' not in df.columns:
                # Возможно данные начинаются с другой строки
                for i in range(min(5, len(df))):
                    if 'От' in str(df.iloc[i].tolist()) or any('От' in str(cell) for cell in df.iloc[i] if pd.notna(cell)):
                        # Нашли строку с заголовками
                        headers = df.iloc[i].tolist()
                        df = df.iloc[i+1:].reset_index(drop=True)
                        df.columns = headers
                        break
                
                # Если все еще не нашли правильные заголовки
                if 'От' not in df.columns:
                    # Используем стандартные заголовки для ценовой сегментации
                    expected_columns = [
                        'От', 'До', 'Продажи', 'Выручка, ₽', 'Потенциал, ₽', 
                        'Упущенная выручка, ₽', 'Упущенная выручка %', 'Товары', 
                        'Товары с продажами', 'Бренды', 'Бренды с продажами', 
                        'Продавцы', 'Продавцы с продажами', 'Выручка на товар, ₽'
                    ]
                    
                    if len(df.columns) >= len(expected_columns):
                        df.columns = expected_columns + list(df.columns[len(expected_columns):])
                    else:
                        st.error("❌ Не удалось определить структуру файла ценовой сегментации")
                        return None
            
            # Удаляем строки с пустыми значениями в ключевых колонках
            df = df.dropna(subset=['От', 'До'])
            
            # Преобразуем числовые колонки
            numeric_cols = ['От', 'До', 'Продажи', 'Выручка, ₽', 'Товары', 'Товары с продажами']
            if 'Выручка на товар, ₽' in df.columns:
                numeric_cols.append('Выручка на товар, ₽')
            
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Удаляем строки где не удалось преобразовать ключевые колонки
            df = df.dropna(subset=['От', 'До'])
            
            if len(df) == 0:
                st.warning("⚠️ После обработки файл ценовой сегментации оказался пустым")
                return None
            
            return df
            
        except Exception as e:
            st.error(f"Ошибка при обработке данных ценовой сегментации: {str(e)}")
            return None
    
    def _process_days_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Обработка данных по дням"""
        try:
            # Проверяем наличие ключевых колонок
            if 'Дата' not in df.columns:
                st.warning("⚠️ В файле по дням отсутствует колонка 'Дата'")
                return None
            
            # Преобразуем дату
            df['Дата'] = pd.to_datetime(df['Дата'], errors='coerce')
            
            # Добавляем дополнительные временные колонки
            df['Год'] = df['Дата'].dt.year
            df['Месяц'] = df['Дата'].dt.month
            df['День_недели'] = df['Дата'].dt.dayofweek
            
            # Удаляем строки с некорректными датами
            df = df.dropna(subset=['Дата'])
            
            # Преобразуем числовые колонки
            numeric_cols = ['Товары', 'Товары с продажами', 'Продажи, шт.', 'Выручка, ₽', 'Остаток']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df
            
        except Exception as e:
            st.error(f"Ошибка при обработке данных по дням: {str(e)}")
            return None
    
    def _process_products_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Обработка данных товаров"""
        try:
            # Проверяем наличие ключевых колонок
            required_cols = ["SKU", "Name", "Final price"]
            if not all(col in df.columns for col in required_cols):
                st.warning("⚠️ В файле товаров отсутствуют необходимые колонки")
                return None
            
            # Удаляем строки с пустыми SKU
            df = df.dropna(subset=['SKU'])
            
            # Преобразуем числовые колонки
            numeric_cols = ['Final price', 'Sales', 'Revenue', 'Category position avg', 
                           'Search cpm avg', 'Search words in ads', 'Search organic position avg']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Заполняем пустые значения в рекламных полях нулями
            ads_cols = ['Search words in ads', 'Search cpm avg']
            for col in ads_cols:
                if col in df.columns:
                    df[col] = df[col].fillna(0)
            
            return df
            
        except Exception as e:
            st.error(f"Ошибка при обработке данных товаров: {str(e)}")
            return None
    
    def get_loaded_data(self) -> Dict[str, pd.DataFrame]:
        """Получение загруженных данных"""
        return self.loaded_data
    
    def get_file_info(self) -> Dict[str, dict]:
        """Получение информации о загруженных файлах"""
        return self.file_info
    
    def is_data_loaded(self, data_type: str) -> bool:
        """Проверка, загружены ли данные определенного типа"""
        return data_type in self.loaded_data and not self.loaded_data[data_type].empty
