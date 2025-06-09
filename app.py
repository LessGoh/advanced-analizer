"""
MPStats Analyzer - Главное приложение
Анализатор ниш маркетплейса на основе данных MPStats

Автор: MPStats Analyzer Team
Версия: 1.0.0
"""

import streamlit as st

# ВАЖНО: st.set_page_config() должен быть первой командой Streamlit
st.set_page_config(
    page_title="MPStats Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/mpstats-analyzer/help',
        'Report a bug': 'https://github.com/mpstats-analyzer/issues',
        'About': "MPStats Analyzer v1.0.0"
    }
)

# Теперь импортируем остальные модули
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Optional
import sys
import os

# Добавляем пути для импорта модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Безопасные импорты с обработкой ошибок
try:
    from components.sidebar import Sidebar
    from components.file_uploader import FileUploader  
    from components.metrics_dashboard import MetricsDashboard
    
    from core.file_processor import FileProcessor
    from core.data_validator import DataValidator
    from core.scoring_engine import ScoringEngine
    
    from analyzers.trend_analyzer import TrendAnalyzer
    from analyzers.query_analyzer import QueryAnalyzer
    from analyzers.price_analyzer import PriceAnalyzer
    from analyzers.stock_analyzer import StockAnalyzer
    from analyzers.ads_analyzer import AdsAnalyzer
    
    from utils.formatters import ReportFormatter
    from utils.constants import VERSION_INFO
    from config import APP_TITLE, APP_ICON
    
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    st.error(f"Ошибка импорта: {e}")
    IMPORTS_SUCCESSFUL = False
    # Используем базовые значения
    APP_TITLE = "MPStats Analyzer"
    APP_ICON = "📊"
    VERSION_INFO = {"version": "1.0.0"}

# Инициализация компонентов
@st.cache_resource
def init_components():
    """Инициализация основных компонентов"""
    if not IMPORTS_SUCCESSFUL:
        return None
        
    return {
        'sidebar': Sidebar(),
        'file_uploader': FileUploader(),
        'metrics_dashboard': MetricsDashboard(),
        'scoring_engine': ScoringEngine(),
        'report_formatter': ReportFormatter()
    }

def initialize_session_state():
    """Инициализация состояния сессии"""
    if 'loaded_data' not in st.session_state:
        st.session_state.loaded_data = {}
    
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {}
    
    if 'scoring_results' not in st.session_state:
        st.session_state.scoring_results = {}
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Главный дашборд"
    
    if 'force_upload_page' not in st.session_state:
        st.session_state.force_upload_page = False

def run_analysis(loaded_data: Dict) -> Dict:
    """Запуск полного анализа данных"""
    
    analysis_results = {}
    components = init_components()
    
    with st.spinner("🔄 Выполняется анализ данных..."):
        
        # Анализ трендов
        if 'trends' in loaded_data:
            try:
                trend_analyzer = TrendAnalyzer(loaded_data['trends'])
                
                analysis_results['trends'] = {
                    'peak_months_by_year': trend_analyzer.get_peak_months_analysis()['peak_months_by_year'],
                    'yoy_changes': trend_analyzer.get_yoy_dynamics_analysis()['metrics_analysis'],
                    'summary': trend_analyzer.get_summary_metrics(),
                    'charts': trend_analyzer.create_trends_charts()
                }
                st.success("✅ Анализ трендов завершен")
            except Exception as e:
                st.error(f"❌ Ошибка в анализе трендов: {str(e)}")
        
        # Анализ запросов
        if 'queries' in loaded_data:
            try:
                query_analyzer = QueryAnalyzer(loaded_data['queries'])
                
                efficiency_analysis = query_analyzer.get_efficiency_analysis()
                analysis_results['queries'] = {
                    'total_queries': efficiency_analysis['total_queries'],
                    'effective_queries': efficiency_analysis['effective_queries']['count'],
                    'efficiency_ratio': efficiency_analysis['effective_queries']['percentage'],
                    'top_opportunities': efficiency_analysis['top_opportunities'],
                    'summary': query_analyzer.get_summary_metrics(),
                    'charts': query_analyzer.create_queries_charts()
                }
                st.success("✅ Анализ запросов завершен")
            except Exception as e:
                st.error(f"❌ Ошибка в анализе запросов: {str(e)}")
        
        # Анализ ценовой сегментации
        if 'price' in loaded_data:
            try:
                price_analyzer = PriceAnalyzer(loaded_data['price'])
                
                segment_analysis = price_analyzer.get_segment_analysis()
                analysis_results['price'] = {
                    'best_segment': segment_analysis['best_segment'],
                    'segment_comparison': segment_analysis['segment_comparison'],
                    'summary': price_analyzer.get_summary_metrics(),
                    'charts': price_analyzer.create_price_charts()
                }
                st.success("✅ Анализ ценовой сегментации завершен")
            except Exception as e:
                st.error(f"❌ Ошибка в анализе цен: {str(e)}")
        
        # Анализ остатков
        if 'days' in loaded_data:
            try:
                stock_analyzer = StockAnalyzer(loaded_data['days'])
                
                seasonal_analysis = stock_analyzer.get_seasonal_analysis()
                analysis_results['stock'] = {
                    'peak_stock_months': seasonal_analysis['peak_stock_months'],
                    'seasonal_patterns': seasonal_analysis['monthly_patterns'],
                    'summary': stock_analyzer.get_summary_metrics(),
                    'charts': stock_analyzer.create_stock_charts()
                }
                st.success("✅ Анализ остатков завершен")
            except Exception as e:
                st.error(f"❌ Ошибка в анализе остатков: {str(e)}")
        
        # Рекламный анализ
        if 'products' in loaded_data:
            try:
                ads_analyzer = AdsAnalyzer(loaded_data['products'])
                
                top_segments = ads_analyzer.get_top_segments_analysis()
                analysis_results['ads'] = {
                    'top_10_analysis': top_segments['top_10_analysis'],
                    'top_100_analysis': top_segments['top_100_analysis'],
                    'niche_assessment': top_segments['niche_assessment'],
                    'summary': ads_analyzer.get_summary_metrics(),
                    'charts': ads_analyzer.create_ads_charts()
                }
                st.success("✅ Рекламный анализ завершен")
            except Exception as e:
                st.error(f"❌ Ошибка в рекламном анализе: {str(e)}")
    
    return analysis_results

def calculate_scoring(loaded_data: Dict) -> Dict:
    """Расчет итогового скоринга"""
    
    components = init_components()
    scoring_engine = components['scoring_engine']
    
    with st.spinner("🏆 Расчет итогового скоринга..."):
        try:
            scoring_results = scoring_engine.calculate_total_score(loaded_data)
            st.success("✅ Скоринг рассчитан")
            return scoring_results
        except Exception as e:
            st.error(f"❌ Ошибка при расчете скоринга: {str(e)}")
            return {}

def render_main_dashboard():
    """Рендер главного дашборда"""
    
    if not IMPORTS_SUCCESSFUL:
        st.error("❌ Ошибка загрузки модулей. Проверьте зависимости.")
        return
    
    components = init_components()
    
    st.markdown('<h1 class="main-header">📊 MPStats Analyzer</h1>', unsafe_allow_html=True)
    st.markdown("### Профессиональный анализ ниш маркетплейса")
    
    # Проверяем наличие данных
    if not st.session_state.loaded_data:
        # Если данных нет - показываем загрузчик
        st.markdown("---")
        st.markdown("### 📤 Загрузите файлы для начала анализа")
        
        uploaded_files = components['file_uploader'].render()
        
        if uploaded_files and st.session_state.loaded_data:
            # Если файлы загружены, показываем кнопку запуска анализа
            st.markdown("---")
            if st.button("🚀 Запустить анализ", type="primary", use_container_width=True):
                with st.spinner("🔄 Анализируем данные..."):
                    
                    # Запускаем анализ
                    analysis_results = run_analysis(st.session_state.loaded_data)
                    st.session_state.analysis_results = analysis_results
                    
                    # Рассчитываем скоринг
                    scoring_results = calculate_scoring(st.session_state.loaded_data)
                    st.session_state.scoring_results = scoring_results
                    
                    if scoring_results:
                        st.success("🎉 Анализ завершен успешно!")
                        st.rerun()
    else:
        # Если данные есть - показываем результаты
        if st.session_state.scoring_results:
            components['metrics_dashboard'].render_main_dashboard(
                st.session_state.scoring_results,
                st.session_state.analysis_results
            )
        else:
            # Если данные есть, но скоринг не рассчитан
            if st.button("🏆 Рассчитать скоринг", type="primary"):
                scoring_results = calculate_scoring(st.session_state.loaded_data)
                st.session_state.scoring_results = scoring_results
                
                if not st.session_state.analysis_results:
                    analysis_results = run_analysis(st.session_state.loaded_data)
                    st.session_state.analysis_results = analysis_results
                
                st.rerun()

def render_trends_page():
    """Страница анализа трендов"""
    
    st.header("📈 Анализ трендов")
    
    if 'trends' not in st.session_state.loaded_data:
        st.warning("⚠️ Данные трендов не загружены")
        return
    
    try:
        trend_analyzer = TrendAnalyzer(st.session_state.loaded_data['trends'])
        
        # Основные метрики
        if st.session_state.scoring_results:
            trend_score = st.session_state.scoring_results.get('trend_score', 0)
            components = init_components()
            components['metrics_dashboard'].render_module_metrics("Анализ трендов", {}, trend_score)
        
        # Пиковые месяцы
        st.subheader("🔥 Пиковые месяцы продаж")
        peak_analysis = trend_analyzer.get_peak_months_analysis()
        
        if peak_analysis['peak_months_by_year']:
            peak_df = pd.DataFrame([
                {
                    'Год': year,
                    'Пиковый месяц': data['month_name'],
                    'Продажи': f"{data['sales']:,}",
                    'Выручка': f"{data['revenue']:,.0f} ₽"
                }
                for year, data in peak_analysis['peak_months_by_year'].items()
            ])
            st.dataframe(peak_df, use_container_width=True)
        
        # YoY динамика
        st.subheader("📊 Динамика год к году")
        yoy_analysis = trend_analyzer.get_yoy_dynamics_analysis()
        
        if yoy_analysis['metrics_analysis']:
            for metric_key, metric_data in yoy_analysis['metrics_analysis'].items():
                if 'error' not in metric_data:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            metric_data['display_name'],
                            f"{metric_data['avg_yoy_change']:+.1f}%",
                            delta=metric_data['overall_trend']
                        )
        
        # Графики
        st.subheader("📈 Графики трендов")
        charts = trend_analyzer.create_trends_charts()
        
        for chart_name, chart in charts.items():
            st.plotly_chart(chart, use_container_width=True)
        
        # Рекомендации
        if peak_analysis['recommendations']:
            st.subheader("💡 Рекомендации")
            for rec in peak_analysis['recommendations']:
                st.info(rec)
    
    except Exception as e:
        st.error(f"Ошибка при отображении анализа трендов: {str(e)}")

def render_queries_page():
    """Страница анализа запросов"""
    
    st.header("🔍 Анализ поисковых запросов")
    
    if 'queries' not in st.session_state.loaded_data:
        st.warning("⚠️ Данные запросов не загружены")
        return
    
    try:
        query_analyzer = QueryAnalyzer(st.session_state.loaded_data['queries'])
        
        # Основные метрики
        if st.session_state.scoring_results:
            query_score = st.session_state.scoring_results.get('query_score', 0)
            components = init_components()
            
            summary = query_analyzer.get_summary_metrics()
            components['metrics_dashboard'].render_module_metrics("Анализ запросов", summary, query_score)
        
        # Анализ эффективности
        st.subheader("⚡ Анализ эффективности запросов")
        efficiency_analysis = query_analyzer.get_efficiency_analysis()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Всего запросов", f"{efficiency_analysis['total_queries']:,}")
        
        with col2:
            st.metric("Эффективных", f"{efficiency_analysis['effective_queries']['count']:,}")
        
        with col3:
            st.metric("% эффективности", f"{efficiency_analysis['effective_queries']['percentage']:.1f}%")
        
        with col4:
            st.metric("Средняя частота", f"{efficiency_analysis['effective_queries']['avg_frequency']:,.0f}")
        
        # Топ возможности
        st.subheader("🎯 Топ возможности для продвижения")
        if efficiency_analysis['top_opportunities']:
            opportunities_df = pd.DataFrame(efficiency_analysis['top_opportunities'])
            st.dataframe(opportunities_df, use_container_width=True)
        
        # Графики
        st.subheader("📊 Визуализация запросов")
        charts = query_analyzer.create_queries_charts()
        
        for chart_name, chart in charts.items():
            st.plotly_chart(chart, use_container_width=True)
        
        # Рекомендации
        if efficiency_analysis['recommendations']:
            st.subheader("💡 Рекомендации")
            for rec in efficiency_analysis['recommendations']:
                st.info(rec)
    
    except Exception as e:
        st.error(f"Ошибка при отображении анализа запросов: {str(e)}")

def render_ads_page():
    """Страница рекламного анализа"""
    
    st.header("🎯 Рекламный анализ")
    
    if 'products' not in st.session_state.loaded_data:
        st.warning("⚠️ Данные товаров не загружены")
        return
    
    try:
        ads_analyzer = AdsAnalyzer(st.session_state.loaded_data['products'])
        
        # Основные метрики
        if st.session_state.scoring_results:
            ads_score = st.session_state.scoring_results.get('ads_score', 0)
            components = init_components()
            
            summary = ads_analyzer.get_summary_metrics()
            components['metrics_dashboard'].render_module_metrics("Рекламный анализ", summary, ads_score)
        
        # Анализ ТОП сегментов
        st.subheader("🏆 Анализ ТОП-10 и ТОП-100")
        top_analysis = ads_analyzer.get_top_segments_analysis()
        
        if 'top_10_analysis' in top_analysis and 'top_100_analysis' in top_analysis:
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**ТОП-10 товары**")
                top10 = top_analysis['top_10_analysis']
                st.metric("Товаров", top10['products_count'])
                st.metric("Средняя ставка", f"{top10['avg_cpm']:.0f} ₽")
                st.metric("Средний чек", f"{top10['avg_price']:.0f} ₽")
                st.metric("Коэффициент Чек/Ставка", f"{top10['avg_ratio']:.1f}")
            
            with col2:
                st.markdown("**ТОП-100 товары**")
                top100 = top_analysis['top_100_analysis']
                st.metric("Товаров", top100['products_count'])
                st.metric("Средняя ставка", f"{top100['avg_cpm']:.0f} ₽")
                st.metric("Средний чек", f"{top100['avg_price']:.0f} ₽")
                st.metric("Коэффициент Чек/Ставка", f"{top100['avg_ratio']:.1f}")
        
        # Оценка ниши
        if 'niche_assessment' in top_analysis:
            assessment = top_analysis['niche_assessment']
            
            st.subheader("🌡️ Температура ниши")
            
            status = assessment.get('niche_status', 'Неизвестно')
            heat_level = assessment.get('heat_level', 3)
            
            if heat_level <= 2:
                st.success(f"🟢 {status} (уровень {heat_level}/5)")
            elif heat_level == 3:
                st.warning(f"🟡 {status} (уровень {heat_level}/5)")
            else:
                st.error(f"🔴 {status} (уровень {heat_level}/5)")
            
            # Обоснование
            reasoning = assessment.get('reasoning', [])
            for reason in reasoning:
                st.info(f"• {reason}")
        
        # Графики
        st.subheader("📊 Графики рекламного анализа")
        charts = ads_analyzer.create_ads_charts()
        
        for chart_name, chart in charts.items():
            st.plotly_chart(chart, use_container_width=True)
        
        # Рекомендации
        if 'recommendations' in top_analysis:
            st.subheader("💡 Рекомендации")
            for rec in top_analysis['recommendations']:
                st.info(rec)
    
    except Exception as e:
        st.error(f"Ошибка при отображении рекламного анализа: {str(e)}")

def render_scoring_page():
    """Страница итогового скоринга"""
    
    st.header("🏆 Итоговый скоринг ниши")
    
    if not st.session_state.scoring_results:
        st.warning("⚠️ Скоринг не рассчитан. Загрузите данные и запустите анализ.")
        
        if st.session_state.loaded_data:
            if st.button("🏆 Рассчитать скоринг", type="primary"):
                scoring_results = calculate_scoring(st.session_state.loaded_data)
                st.session_state.scoring_results = scoring_results
                st.rerun()
        return
    
    components = init_components()
    
    # Основной дашборд
    components['metrics_dashboard'].render_main_dashboard(
        st.session_state.scoring_results,
        st.session_state.analysis_results
    )
    
    # Детальные результаты
    st.markdown("---")
    st.subheader("📋 Детальные результаты анализа")
    
    detailed_analysis = st.session_state.scoring_results.get('detailed_analysis', {})
    
    for module_name, module_data in detailed_analysis.items():
        with st.expander(f"📊 {module_name.title()}"):
            
            if isinstance(module_data, dict):
                # Основные метрики модуля
                if 'total_score' in module_data:
                    st.metric("Балл модуля", f"{module_data['total_score']}/4")
                
                # Подробности
                for key, value in module_data.items():
                    if key not in ['total_score', 'error']:
                        if isinstance(value, dict):
                            st.json(value)
                        else:
                            st.write(f"**{key}:** {value}")
                
                # Ошибки
                if 'error' in module_data:
                    st.error(f"Ошибка: {module_data['error']}")
    
    # Экспорт отчета
    st.markdown("---")
    st.subheader("📤 Экспорт результатов")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Скачать Excel отчет", use_container_width=True):
            try:
                report_formatter = components['report_formatter']
                filename = report_formatter.export_to_excel(
                    st.session_state.scoring_results,
                    st.session_state.analysis_results
                )
                st.success(f"✅ Отчет сохранен: {filename}")
            except Exception as e:
                st.error(f"❌ Ошибка при экспорте: {str(e)}")
    
    with col2:
        if st.button("📄 Создать текстовый отчет", use_container_width=True):
            try:
                report_formatter = components['report_formatter']
                report_text = report_formatter.create_detailed_report(
                    st.session_state.scoring_results,
                    st.session_state.analysis_results
                )
                
                st.download_button(
                    label="📥 Скачать отчет",
                    data=report_text,
                    file_name=f"mpstats_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
            except Exception as e:
                st.error(f"❌ Ошибка при создании отчета: {str(e)}")

def render_settings_page():
    """Страница настроек"""
    components = init_components()
    components['sidebar'].render_settings_panel()

def main():
    """Главная функция приложения"""
    
    # Инициализация
    initialize_session_state()
    
    # Проверяем принудительный переход к загрузке
    if st.session_state.get('force_upload_page', False):
        selected_page = "Главный дашборд"  # Покажем загрузчик на главной странице
        st.session_state.force_upload_page = False
    else:
        components = init_components()
        if components:
            # Боковая панель
            selected_page = components['sidebar'].render()
            st.session_state.current_page = selected_page
        else:
            st.error("❌ Ошибка инициализации компонентов")
            return
    
    # Роутинг страниц
    if selected_page == "Главный дашборд":
        render_main_dashboard()
    
    elif selected_page == "Анализ трендов":
        render_trends_page()
    
    elif selected_page == "Анализ запросов":
        render_queries_page()
    
    elif selected_page == "Ценовая сегментация":
        if 'price' not in st.session_state.loaded_data:
            st.warning("⚠️ Данные ценовой сегментации не загружены")
        else:
            st.header("💰 Ценовая сегментация")
            st.info("Модуль ценовой сегментации в разработке")
    
    elif selected_page == "Анализ остатков":
        if 'days' not in st.session_state.loaded_data:
            st.warning("⚠️ Данные по дням не загружены")
        else:
            st.header("📦 Анализ остатков")
            st.info("Модуль анализа остатков в разработке")
    
    elif selected_page == "Рекламный анализ":
        render_ads_page()
    
    elif selected_page == "Итоговый скоринг":
        render_scoring_page()
    
    elif selected_page == "Настройки":
        render_settings_page()
    
    # Футер
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #666; font-size: 0.8rem;">
        MPStats Analyzer v{VERSION_INFO['version'] if IMPORTS_SUCCESSFUL else '1.0.0'} | 
        Made with ❤️ for marketplace analytics
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
