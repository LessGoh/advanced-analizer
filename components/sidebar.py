import streamlit as st
from streamlit_option_menu import option_menu
from typing import Dict, List, Optional
import pandas as pd


class Sidebar:
    """Компонент боковой панели навигации"""
    
    def __init__(self):
        self.menu_options = [
            {"name": "Главный дашборд", "icon": "house"},
            {"name": "Анализ трендов", "icon": "graph-up"},
            {"name": "Анализ запросов", "icon": "search"},
            {"name": "Ценовая сегментация", "icon": "currency-dollar"},
            {"name": "Анализ остатков", "icon": "boxes"},
            {"name": "Рекламный анализ", "icon": "bullseye"},
            {"name": "Итоговый скоринг", "icon": "award"},
            {"name": "Настройки", "icon": "gear"}
        ]
    
    def render(self) -> str:
        """Рендер боковой панели и возврат выбранного пункта меню"""
        
        with st.sidebar:
            # Заголовок приложения
            st.markdown("""
                <div style="text-align: center; padding: 1rem 0;">
                    <h1 style="color: #1f77b4; margin: 0;">📊 MPStats</h1>
                    <h3 style="color: #666; margin: 0;">Analyzer</h3>
                    <p style="color: #888; font-size: 0.9rem;">Анализ ниш маркетплейса</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Главное меню навигации
            selected = option_menu(
                menu_title="Навигация",
                options=[option["name"] for option in self.menu_options],
                icons=[option["icon"] for option in self.menu_options],
                menu_icon="list",
                default_index=0,
                orientation="vertical",
                styles={
                    "container": {"padding": "0!important", "background-color": "#fafafa"},
                    "icon": {"color": "#1f77b4", "font-size": "16px"},
                    "nav-link": {
                        "font-size": "14px",
                        "text-align": "left",
                        "margin": "0px",
                        "--hover-color": "#eee",
                        "padding": "0.5rem 0.75rem"
                    },
                    "nav-link-selected": {"background-color": "#1f77b4"},
                }
            )
            
            st.markdown("---")
            
            # Статус загруженных файлов
            self._render_file_status()
            
            st.markdown("---")
            
            # Быстрые действия
            self._render_quick_actions()
            
            st.markdown("---")
            
            # Информация о версии
            st.markdown("""
                <div style="text-align: center; padding: 1rem 0; color: #888; font-size: 0.8rem;">
                    MPStats Analyzer v1.0<br>
                    © 2024 Analysis Tool
                </div>
            """, unsafe_allow_html=True)
        
        return selected
    
    def _render_file_status(self):
        """Отображение статуса загруженных файлов"""
        st.subheader("📁 Загруженные файлы")
        
        # Проверяем наличие данных в session_state
        if 'loaded_data' not in st.session_state or not st.session_state.loaded_data:
            st.info("Файлы не загружены")
            if st.button("📤 Загрузить файлы", use_container_width=True):
                st.switch_page("Главный дашборд")
            return
        
        # Отображаем статус каждого типа файла
        file_types = {
            "trends": {"name": "Тренды", "icon": "📈"},
            "queries": {"name": "Запросы", "icon": "🔍"},
            "price": {"name": "Цены", "icon": "💰"},
            "days": {"name": "По дням", "icon": "📅"},
            "products": {"name": "Товары", "icon": "📦"}
        }
        
        for file_type, info in file_types.items():
            if file_type in st.session_state.loaded_data:
                data = st.session_state.loaded_data[file_type]
                st.success(f"{info['icon']} {info['name']} ({len(data)} записей)")
            else:
                st.error(f"{info['icon']} {info['name']} - не загружен")
    
    def _render_quick_actions(self):
        """Быстрые действия"""
        st.subheader("⚡ Быстрые действия")
        
        # Кнопка обновления анализа
        if st.button("🔄 Обновить анализ", use_container_width=True):
            # Очищаем кеш результатов
            if 'analysis_results' in st.session_state:
                del st.session_state.analysis_results
            if 'scoring_results' in st.session_state:
                del st.session_state.scoring_results
            st.rerun()
        
        # Кнопка экспорта результатов
        if st.button("📊 Экспорт отчета", use_container_width=True, disabled=('scoring_results' not in st.session_state)):
            st.session_state.show_export_modal = True
            st.rerun()
        
        # Кнопка очистки данных
        if st.button("🗑️ Очистить данные", use_container_width=True):
            self._clear_all_data()
            st.rerun()
    
    def _clear_all_data(self):
        """Очистка всех данных из session_state"""
        keys_to_clear = [
            'loaded_data', 
            'file_info', 
            'analysis_results', 
            'scoring_results',
            'validation_results'
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        st.success("Все данные очищены")
    
    def render_settings_panel(self):
        """Панель настроек (отображается при выборе раздела "Настройки")"""
        st.header("⚙️ Настройки анализа")
        
        # Настройки скоринга
        st.subheader("🏆 Настройки скоринга")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Пороговые значения для трендов (YoY %)**")
            trend_excellent = st.number_input("Отличный рост (≥)", value=10.0, step=1.0, key="trend_excellent")
            trend_good = st.number_input("Хороший рост (≥)", value=0.0, step=1.0, key="trend_good")
            trend_stable = st.number_input("Стабильность (≥)", value=-5.0, step=1.0, key="trend_stable")
        
        with col2:
            st.markdown("**Пороговые значения для запросов**")
            query_excellent = st.number_input("Отличный коэффициент (≥)", value=5.0, step=0.5, key="query_excellent")
            query_good = st.number_input("Хороший коэффициент (≥)", value=3.0, step=0.5, key="query_good")
            query_average = st.number_input("Средний коэффициент (≥)", value=2.0, step=0.5, key="query_average")
        
        st.markdown("**Пороговые значения для рекламы (Чек/Ставка)**")
        col3, col4 = st.columns(2)
        
        with col3:
            ads_excellent = st.number_input("Очень выгодная ниша (≥)", value=4.0, step=0.5, key="ads_excellent")
            ads_good = st.number_input("Хорошая ниша (≥)", value=3.0, step=0.5, key="ads_good")
        
        with col4:
            ads_average = st.number_input("Средняя конкуренция (≥)", value=2.0, step=0.5, key="ads_average")
            ads_poor = st.number_input("Высокая конкуренция (≥)", value=1.0, step=0.5, key="ads_poor")
        
        # Кнопки управления настройками
        col_reset, col_save = st.columns(2)
        
        with col_reset:
            if st.button("🔄 Сбросить к умолчанию", use_container_width=True):
                self._reset_settings()
                st.rerun()
        
        with col_save:
            if st.button("💾 Сохранить настройки", use_container_width=True):
                self._save_settings({
                    'trend_excellent': trend_excellent,
                    'trend_good': trend_good,
                    'trend_stable': trend_stable,
                    'query_excellent': query_excellent,
                    'query_good': query_good,
                    'query_average': query_average,
                    'ads_excellent': ads_excellent,
                    'ads_good': ads_good,
                    'ads_average': ads_average,
                    'ads_poor': ads_poor
                })
                st.success("Настройки сохранены!")
        
        # Дополнительные настройки
        st.subheader("🎨 Настройки отображения")
        
        col5, col6 = st.columns(2)
        
        with col5:
            show_charts = st.checkbox("Показывать графики", value=True, key="show_charts")
            show_recommendations = st.checkbox("Показывать рекомендации", value=True, key="show_recommendations")
        
        with col6:
            chart_height = st.selectbox("Высота графиков", options=[300, 400, 500, 600], index=1, key="chart_height")
            decimal_places = st.selectbox("Знаков после запятой", options=[0, 1, 2, 3], index=2, key="decimal_places")
        
        # Информация о данных
        st.subheader("📊 Информация о загруженных данных")
        
        if 'loaded_data' in st.session_state and st.session_state.loaded_data:
            for data_type, data in st.session_state.loaded_data.items():
                with st.expander(f"📁 {data_type.title()} ({len(data)} записей)"):
                    st.write("**Колонки:**")
                    st.write(", ".join(data.columns.tolist()))
                    
                    if len(data) > 0:
                        st.write("**Период данных:**")
                        date_columns = [col for col in data.columns if 'дата' in col.lower() or 'месяц' in col.lower()]
                        if date_columns:
                            date_col = date_columns[0]
                            try:
                                min_date = pd.to_datetime(data[date_col]).min()
                                max_date = pd.to_datetime(data[date_col]).max()
                                st.write(f"С {min_date.strftime('%Y-%m-%d')} по {max_date.strftime('%Y-%m-%d')}")
                            except:
                                st.write("Не удалось определить период")
                        
                        st.write("**Пример данных:**")
                        st.dataframe(data.head(3), use_container_width=True)
        else:
            st.info("Данные не загружены")
    
    def _reset_settings(self):
        """Сброс настроек к значениям по умолчанию"""
        default_settings = {
            'trend_excellent': 10.0,
            'trend_good': 0.0,
            'trend_stable': -5.0,
            'query_excellent': 5.0,
            'query_good': 3.0,
            'query_average': 2.0,
            'ads_excellent': 4.0,
            'ads_good': 3.0,
            'ads_average': 2.0,
            'ads_poor': 1.0,
            'show_charts': True,
            'show_recommendations': True,
            'chart_height': 400,
            'decimal_places': 2
        }
        
        for key, value in default_settings.items():
            st.session_state[key] = value
    
    def _save_settings(self, settings: Dict):
        """Сохранение настроек в session_state"""
        st.session_state.user_settings = settings
        
        # Также обновляем конфигурацию для текущей сессии
        if 'config_override' not in st.session_state:
            st.session_state.config_override = {}
        
        st.session_state.config_override.update(settings)
    
    def get_current_settings(self) -> Dict:
        """Получение текущих настроек"""
        if 'user_settings' in st.session_state:
            return st.session_state.user_settings
        else:
            # Возвращаем настройки по умолчанию
            return {
                'trend_excellent': 10.0,
                'trend_good': 0.0,
                'trend_stable': -5.0,
                'query_excellent': 5.0,
                'query_good': 3.0,
                'query_average': 2.0,
                'ads_excellent': 4.0,
                'ads_good': 3.0,
                'ads_average': 2.0,
                'ads_poor': 1.0,
                'show_charts': True,
                'show_recommendations': True,
                'chart_height': 400,
                'decimal_places': 2
            }
    
    def render_file_upload_section(self):
        """Секция загрузки файлов (для главного дашборда)"""
        st.subheader("📤 Загрузка файлов MPStats")
        
        st.markdown("""
        **Поддерживаемые типы файлов:**
        - 📈 **Отчет по трендам** (.xlsx) - динамика продаж по месяцам
        - 🔍 **Отчет по запросам** (.xlsx) - поисковые запросы и их эффективность  
        - 💰 **Ценовая сегментация** (.xlsx) - анализ по ценовым диапазонам
        - 📅 **Отчет по дням** (.xlsx) - ежедневная статистика остатков
        - 📦 **Отчет по товарам** (.csv) - детальная информация о товарах
        """)
        
        uploaded_files = st.file_uploader(
            "Выберите файлы отчетов",
            type=['xlsx', 'csv'],
            accept_multiple_files=True,
            help="Можно загрузить несколько файлов одновременно"
        )
        
        if uploaded_files:
            return uploaded_files
        
        return None
    
    def show_upload_tips(self):
        """Показать подсказки по загрузке файлов"""
        with st.expander("💡 Подсказки по загрузке файлов"):
            st.markdown("""
            **Для корректной работы анализатора:**
            
            1. **Названия файлов** должны содержать ключевые слова:
               - `тренд` или `trend` - для отчета по трендам
               - `запрос` или `queries` - для отчета по запросам
               - `ценов` или `price` - для ценовой сегментации
               - `дням` или `days` - для отчета по дням
               - `.csv` - для отчета по товарам
            
            2. **Структура данных** должна соответствовать стандарту MPStats
            
            3. **Рекомендуется загружать** все 5 типов отчетов для полного анализа
            
            4. **Период данных** - желательно не менее 3 месяцев для трендового анализа
            """)
    
    def render_progress_indicator(self, current_step: str, total_steps: int = 5):
        """Индикатор прогресса анализа"""
        steps = [
            "Загрузка файлов",
            "Валидация данных", 
            "Анализ трендов",
            "Расчет скоринга",
            "Генерация отчета"
        ]
        
        current_index = steps.index(current_step) if current_step in steps else 0
        progress = (current_index + 1) / len(steps)
        
        st.progress(progress)
        st.caption(f"Шаг {current_index + 1}/{len(steps)}: {current_step}")
        
        # Показываем статус каждого шага
        for i, step in enumerate(steps):
            if i < current_index:
                st.success(f"✅ {step}")
            elif i == current_index:
                st.info(f"🔄 {step}")
            else:
                st.text(f"⏳ {step}")
    
    def render_export_modal(self):
        """Модальное окно экспорта результатов"""
        if 'show_export_modal' not in st.session_state:
            return
        
        if st.session_state.show_export_modal:
            st.subheader("📊 Экспорт результатов анализа")
            
            col1, col2 = st.columns(2)
            
            with col1:
                export_format = st.selectbox(
                    "Формат экспорта",
                    options=["Excel (.xlsx)", "PDF отчет", "JSON данные"],
                    key="export_format"
                )
            
            with col2:
                include_charts = st.checkbox("Включить графики", value=True, key="include_charts")
            
            export_sections = st.multiselect(
                "Разделы для экспорта",
                options=[
                    "Итоговый скоринг",
                    "Анализ трендов", 
                    "Анализ запросов",
                    "Ценовая сегментация",
                    "Анализ остатков",
                    "Рекламный анализ"
                ],
                default=["Итоговый скоринг"],
                key="export_sections"
            )
            
            col_cancel, col_export = st.columns(2)
            
            with col_cancel:
                if st.button("❌ Отмена", use_container_width=True):
                    st.session_state.show_export_modal = False
                    st.rerun()
            
            with col_export:
                if st.button("📥 Экспортировать", use_container_width=True, type="primary"):
                    # Здесь будет логика экспорта
                    st.success("Экспорт начат! Файл будет готов через несколько секунд.")
                    st.session_state.show_export_modal = False
                    st.rerun()
