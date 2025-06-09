import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Tuple
import io
from core.file_processor import FileProcessor
from core.data_validator import DataValidator


class FileUploader:
    """Компонент загрузки и обработки файлов"""
    
    def __init__(self):
        self.file_processor = FileProcessor()
        self.data_validator = DataValidator()
        self.supported_formats = {
            '.xlsx': 'Excel файлы',
            '.csv': 'CSV файлы'
        }
        
    def render(self) -> Optional[Dict]:
        """Основной метод рендера компонента загрузки"""
        
        # Проверяем, есть ли уже загруженные данные
        if 'loaded_data' in st.session_state and st.session_state.loaded_data:
            return self._render_loaded_data_status()
        
        return self._render_upload_interface()
    
    def _render_upload_interface(self) -> Optional[Dict]:
        """Интерфейс загрузки файлов"""
        
        st.markdown("""
        <div style="padding: 2rem; border: 2px dashed #1f77b4; border-radius: 10px; text-align: center; background: #f8f9fa;">
            <h3 style="color: #1f77b4; margin-top: 0;">📤 Загрузка файлов MPStats</h3>
            <p style="color: #666; margin-bottom: 1.5rem;">
                Перетащите файлы сюда или используйте кнопку для выбора
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Информация о поддерживаемых файлах
        with st.expander("📋 Требования к файлам", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **📈 Обязательные отчеты:**
                - Отчет по трендам (.xlsx)
                - Отчет по товарам (.csv)
                """)
                
            with col2:
                st.markdown("""
                **📊 Дополнительные отчеты:**
                - Отчет по запросам (.xlsx)
                - Ценовая сегментация (.xlsx)
                - Отчет по дням (.xlsx)
                """)
            
            st.markdown("""
            **💡 Подсказки по именованию файлов:**
            - Файлы с 'тренд' или 'trend' → Отчет по трендам
            - Файлы с 'запрос' или 'queries' → Отчет по запросам  
            - Файлы с 'ценов' или 'price' → Ценовая сегментация
            - Файлы с 'дням' или 'days' → Отчет по дням
            - Файлы .csv → Отчет по товарам
            """)
        
        # Загрузчик файлов
        uploaded_files = st.file_uploader(
            "Выберите файлы отчетов MPStats",
            type=['xlsx', 'csv'],
            accept_multiple_files=True,
            help="Можно загрузить несколько файлов одновременно"
        )
        
        if uploaded_files:
            return self._process_uploaded_files(uploaded_files)
        
        # Пример загрузки (если нет файлов)
        self._render_sample_data_option()
        
        return None
    
    def _process_uploaded_files(self, uploaded_files: List) -> Optional[Dict]:
        """Обработка загруженных файлов"""
        
        with st.spinner("🔄 Обработка загруженных файлов..."):
            
            # Информация о загруженных файлах
            st.subheader("📁 Загруженные файлы")
            
            files_info = []
            for file in uploaded_files:
                file_size = len(file.getvalue()) / 1024 / 1024  # MB
                files_info.append({
                    "Название": file.name,
                    "Размер": f"{file_size:.2f} MB",
                    "Тип": file.type if file.type else "Неизвестно"
                })
            
            st.dataframe(pd.DataFrame(files_info), use_container_width=True)
            
            # Обработка файлов
            try:
                loaded_data = self.file_processor.process_uploaded_files(uploaded_files)
                
                if not loaded_data:
                    st.error("❌ Не удалось обработать файлы. Проверьте формат и структуру данных.")
                    return None
                
                # Валидация данных
                st.subheader("🔍 Валидация данных")
                validation_results = self.data_validator.validate_all_data(loaded_data)
                
                # Отображение результатов валидации
                self._display_validation_results(validation_results)
                
                # Сохранение в session_state
                st.session_state.loaded_data = loaded_data
                st.session_state.file_info = self.file_processor.get_file_info()
                st.session_state.validation_results = validation_results
                
                # Успешная загрузка
                st.success("✅ Файлы успешно загружены и проверены!")
                
                # Кнопка перехода к анализу
                if st.button("🚀 Начать анализ", type="primary", use_container_width=True):
                    st.switch_page("Итоговый скоринг")
                
                return loaded_data
                
            except Exception as e:
                st.error(f"❌ Ошибка при обработке файлов: {str(e)}")
                return None
    
    def _display_validation_results(self, validation_results: Dict):
        """Отображение результатов валидации"""
        
        # Общая статистика
        total_files = len(validation_results)
        valid_files = sum(1 for result in validation_results.values() if result.get("valid", False))
        total_errors = sum(len(result.get("errors", [])) for result in validation_results.values())
        total_warnings = sum(len(result.get("warnings", [])) for result in validation_results.values())
        
        # Метрики валидации
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Файлов загружено", total_files)
        
        with col2:
            st.metric("Файлов валидно", valid_files, delta=valid_files - total_files if valid_files != total_files else None)
        
        with col3:
            color = "normal" if total_errors == 0 else "inverse"
            st.metric("Ошибок", total_errors, delta_color=color)
        
        with col4:
            color = "normal" if total_warnings == 0 else "off"  
            st.metric("Предупреждений", total_warnings, delta_color=color)
        
        # Детальные результаты
        if total_errors > 0 or total_warnings > 0:
            with st.expander("📋 Детальные результаты валидации"):
                for file_type, result in validation_results.items():
                    
                    status_icon = "✅" if result.get("valid", False) else "❌"
                    st.markdown(f"**{status_icon} {file_type.title()}**")
                    
                    # Ошибки
                    if result.get("errors"):
                        for error in result["errors"]:
                            st.error(f"• {error}")
                    
                    # Предупреждения
                    if result.get("warnings"):
                        for warning in result["warnings"]:
                            st.warning(f"• {warning}")
                    
                    # Дополнительная информация
                    if "records_count" in result:
                        st.info(f"📊 Записей: {result['records_count']}")
                    
                    st.markdown("---")
    
    def _render_loaded_data_status(self) -> Dict:
        """Отображение статуса уже загруженных данных"""
        
        st.success("✅ Данные уже загружены")
        
        loaded_data = st.session_state.loaded_data
        file_info = st.session_state.get('file_info', {})
        
        # Сводка по загруженным файлам
        st.subheader("📊 Сводка по данным")
        
        summary_data = []
        for data_type, data in loaded_data.items():
            info = file_info.get(data_type, {})
            summary_data.append({
                "Тип отчета": data_type.title(),
                "Файл": info.get("filename", "Неизвестно"),
                "Записей": len(data),
                "Колонок": len(data.columns),
                "Статус": "✅ Загружен"
            })
        
        st.dataframe(pd.DataFrame(summary_data), use_container_width=True)
        
        # Предпросмотр данных
        self._render_data_preview(loaded_data)
        
        # Действия с данными
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Перезагрузить файлы", use_container_width=True):
                self._clear_loaded_data()
                st.rerun()
        
        with col2:
            if st.button("📊 Открыть анализ", use_container_width=True, type="primary"):
                st.switch_page("Итоговый скоринг")
        
        with col3:
            if st.button("📋 Показать валидацию", use_container_width=True):
                if 'validation_results' in st.session_state:
                    self._display_validation_results(st.session_state.validation_results)
        
        return loaded_data
    
    def _render_data_preview(self, loaded_data: Dict):
        """Предпросмотр загруженных данных"""
        
        st.subheader("👁️ Предпросмотр данных")
        
        # Выбор типа данных для предпросмотра
        data_types = list(loaded_data.keys())
        selected_type = st.selectbox("Выберите тип данных для предпросмотра:", data_types)
        
        if selected_type and selected_type in loaded_data:
            data = loaded_data[selected_type]
            
            # Базовая информация
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Строк", len(data))
            
            with col2:
                st.metric("Колонок", len(data.columns))
            
            with col3:
                # Определяем период данных
                date_columns = [col for col in data.columns if any(word in col.lower() for word in ['дата', 'месяц', 'date'])]
                if date_columns:
                    try:
                        date_col = date_columns[0]
                        date_range = pd.to_datetime(data[date_col])
                        period = f"{date_range.min().strftime('%Y-%m')} — {date_range.max().strftime('%Y-%m')}"
                        st.metric("Период", period)
                    except:
                        st.metric("Период", "Не определен")
                else:
                    st.metric("Период", "Не применимо")
            
            # Таблица с данными
            st.markdown("**Первые 10 записей:**")
            st.dataframe(data.head(10), use_container_width=True)
            
            # Информация о колонках
            with st.expander("📋 Информация о колонках"):
                column_info = []
                for col in data.columns:
                    non_null_count = data[col].count()
                    null_count = len(data) - non_null_count
                    dtype = str(data[col].dtype)
                    
                    column_info.append({
                        "Колонка": col,
                        "Тип данных": dtype,
                        "Заполненных": non_null_count,
                        "Пустых": null_count,
                        "% заполненности": f"{(non_null_count/len(data)*100):.1f}%"
                    })
                
                st.dataframe(pd.DataFrame(column_info), use_container_width=True)
    
    def _render_sample_data_option(self):
        """Опция загрузки примера данных"""
        
        st.markdown("---")
        
        with st.expander("🎯 Нет файлов? Попробуйте с примером данных"):
            st.markdown("""
            Если у вас нет файлов MPStats, вы можете воспользоваться примером данных 
            для ознакомления с функционалом анализатора.
            """)
            
            if st.button("📊 Загрузить пример данных", use_container_width=True):
                self._load_sample_data()
    
    def _load_sample_data(self):
        """Загрузка примера данных"""
        
        with st.spinner("🔄 Загрузка примера данных..."):
            try:
                # Создаем пример данных для демонстрации
                sample_data = self._generate_sample_data()
                
                # Валидация примера данных
                validation_results = self.data_validator.validate_all_data(sample_data)
                
                # Сохранение в session_state
                st.session_state.loaded_data = sample_data
                st.session_state.file_info = {
                    "trends": {"filename": "sample_trends.xlsx", "rows": len(sample_data["trends"]), "columns": len(sample_data["trends"].columns)},
                    "products": {"filename": "sample_products.csv", "rows": len(sample_data["products"]), "columns": len(sample_data["products"].columns)}
                }
                st.session_state.validation_results = validation_results
                
                st.success("✅ Пример данных загружен!")
                st.info("💡 Это демонстрационные данные для ознакомления с функционалом")
                
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Ошибка при загрузке примера: {str(e)}")
    
    def _generate_sample_data(self) -> Dict:
        """Генерация примера данных"""
        
        # Пример данных трендов
        import numpy as np
        from datetime import datetime, timedelta
        
        # Генерируем даты за последние 12 месяцев
        end_date = datetime.now()
        dates = [end_date - timedelta(days=30*i) for i in range(12)][::-1]
        
        trends_data = pd.DataFrame({
            'Месяц': dates,
            'Продажи': np.random.randint(1000, 5000, 12),
            'Выручка, ₽': np.random.randint(500000, 2000000, 12),
            'Товары': np.random.randint(100, 300, 12),
            'Товары с продажами': np.random.randint(50, 150, 12),
            'Бренды': np.random.randint(20, 50, 12),
            'Бренды с продажами': np.random.randint(15, 35, 12),
            'Продавцы': np.random.randint(30, 80, 12),
            'Продавцы с продажами': np.random.randint(20, 60, 12),
            'Средний чек, ₽': np.random.randint(800, 1500, 12)
        })
        
        # Пример данных товаров
        products_data = pd.DataFrame({
            'SKU': range(1000000, 1000100),
            'Name': [f'Тестовый товар {i}' for i in range(100)],
            'Category': ['Тестовая категория'] * 100,
            'Brand': [f'Бренд {i%10}' for i in range(100)],
            'Final price': np.random.randint(500, 3000, 100),
            'Sales': np.random.randint(0, 1000, 100),
            'Revenue': np.random.randint(0, 500000, 100),
            'Category position avg': np.random.randint(1, 200, 100),
            'Search cpm avg': np.random.randint(50, 800, 100),
            'Search words in ads': np.random.randint(0, 50, 100),
            'Search organic position avg': np.random.randint(1, 300, 100)
        })
        
        return {
            'trends': trends_data,
            'products': products_data
        }
    
    def _clear_loaded_data(self):
        """Очистка загруженных данных"""
        keys_to_clear = ['loaded_data', 'file_info', 'validation_results', 'analysis_results', 'scoring_results']
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
    
    def get_upload_requirements(self) -> Dict:
        """Получение требований к загружаемым файлам"""
        return {
            "trends": {
                "name": "Отчет по трендам",
                "format": ".xlsx",
                "required_columns": ["Месяц", "Продажи", "Выручка, ₽", "Товары", "Бренды"],
                "description": "Динамика продаж и основных метрик по месяцам"
            },
            "queries": {
                "name": "Отчет по запросам", 
                "format": ".xlsx",
                "required_columns": ["Ключевое слово", "Частота WB", "Товаров в запросе"],
                "description": "Поисковые запросы и их характеристики"
            },
            "price": {
                "name": "Ценовая сегментация",
                "format": ".xlsx", 
                "required_columns": ["От", "До", "Выручка на товар, ₽", "Товары", "Продавцы"],
                "description": "Анализ эффективности ценовых сегментов"
            },
            "days": {
                "name": "Отчет по дням",
                "format": ".xlsx",
                "required_columns": ["Дата", "Остаток", "Продажи, шт.", "Выручка, ₽"],
                "description": "Ежедневная статистика остатков и продаж"
            },
            "products": {
                "name": "Отчет по товарам",
                "format": ".csv",
                "required_columns": ["SKU", "Final price", "Category position avg", "Search cmp avg"],
                "description": "Детальная информация о товарах и их позициях"
            }
        }
    
    def validate_file_structure(self, file_type: str, data: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Валидация структуры конкретного файла"""
        requirements = self.get_upload_requirements()
        
        if file_type not in requirements:
            return False, [f"Неизвестный тип файла: {file_type}"]
        
        required_columns = requirements[file_type]["required_columns"]
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            return False, [f"Отсутствуют обязательные колонки: {', '.join(missing_columns)}"]
        
        return True, []
