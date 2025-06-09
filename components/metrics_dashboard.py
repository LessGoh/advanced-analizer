import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Optional, Any
from config import SCORE_COLORS, TOTAL_SCORE_RANGES


class MetricsDashboard:
    """Компонент дашборда с метриками и KPI"""
    
    def __init__(self):
        self.color_scheme = {
            "excellent": "#28a745",
            "good": "#ffc107", 
            "average": "#fd7e14",
            "poor": "#dc3545",
            "critical": "#6c757d"
        }
    
    def render_main_dashboard(self, scoring_results: Dict, analysis_results: Dict = None):
        """Основной дашборд с общими метриками"""
        
        st.header("📊 Общий дашборд анализа ниши")
        
        # Основные KPI
        self._render_main_kpis(scoring_results)
        
        st.markdown("---")
        
        # Детальный скоринг по модулям
        self._render_scoring_breakdown(scoring_results)
        
        st.markdown("---")
        
        # Графическое представление скоринга
        self._render_scoring_charts(scoring_results)
        
        if analysis_results:
            st.markdown("---")
            # Ключевые инсайты
            self._render_key_insights(analysis_results)
    
    def _render_main_kpis(self, scoring_results: Dict):
        """Основные KPI метрики"""
        
        total_score = scoring_results.get("total_score", 0)
        niche_rating = scoring_results.get("niche_rating", "poor")
        
        # Определяем цвет и эмодзи для общего рейтинга
        rating_config = self._get_rating_config(niche_rating)
        
        # Основные метрики в верхней части
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div style="
                background: linear-gradient(90deg, {rating_config['color']} 0%, {rating_config['color']}80 100%);
                padding: 1.5rem;
                border-radius: 10px;
                color: white;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            ">
                <h1 style="margin: 0; font-size: 3rem;">{total_score}</h1>
                <h3 style="margin: 0; opacity: 0.9;">из 20 баллов</h3>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">Общий скоринг</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="
                background: linear-gradient(90deg, {rating_config['color']} 0%, {rating_config['color']}80 100%);
                padding: 1.5rem;
                border-radius: 10px;
                color: white;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            ">
                <h1 style="margin: 0; font-size: 2.5rem;">{rating_config['emoji']}</h1>
                <h3 style="margin: 0.5rem 0 0 0; opacity: 0.9;">{rating_config['title']}</h3>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">Рейтинг ниши</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Процент от максимального скоринга
            percentage = round((total_score / 20) * 100, 1)
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                padding: 1.5rem;
                border-radius: 10px;
                color: white;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            ">
                <h1 style="margin: 0; font-size: 3rem;">{percentage}%</h1>
                <h3 style="margin: 0; opacity: 0.9;">эффективности</h3>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">От максимума</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            # Количество успешных модулей
            successful_modules = sum(1 for score in [
                scoring_results.get("trend_score", 0),
                scoring_results.get("query_score", 0), 
                scoring_results.get("price_score", 0),
                scoring_results.get("stock_score", 0),
                scoring_results.get("ads_score", 0)
            ] if score >= 3)
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
                padding: 1.5rem;
                border-radius: 10px;
                color: white;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            ">
                <h1 style="margin: 0; font-size: 3rem;">{successful_modules}</h1>
                <h3 style="margin: 0; opacity: 0.9;">из 5 модулей</h3>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">Успешных</p>
            </div>
            """, unsafe_allow_html=True)
    
    def _render_scoring_breakdown(self, scoring_results: Dict):
        """Детальная разбивка скоринга по модулям"""
        
        st.subheader("🏆 Скоринг по модулям")
        
        modules = [
            {"name": "Анализ трендов", "key": "trend_score", "icon": "📈", "max_score": 4},
            {"name": "Анализ запросов", "key": "query_score", "icon": "🔍", "max_score": 4},
            {"name": "Ценовая сегментация", "key": "price_score", "icon": "💰", "max_score": 4},
            {"name": "Анализ остатков", "key": "stock_score", "icon": "📦", "max_score": 4},
            {"name": "Рекламный анализ", "key": "ads_score", "icon": "🎯", "max_score": 4}
        ]
        
        for module in modules:
            score = scoring_results.get(module["key"], 0)
            percentage = (score / module["max_score"]) * 100
            
            # Определяем цвет прогресс-бара
            if percentage >= 75:
                color = self.color_scheme["excellent"]
            elif percentage >= 50:
                color = self.color_scheme["good"]
            elif percentage >= 25:
                color = self.color_scheme["average"]
            else:
                color = self.color_scheme["poor"]
            
            # Создаем строку с метрикой
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"""
                <div style="margin-bottom: 1rem;">
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.2rem; margin-right: 0.5rem;">{module['icon']}</span>
                        <strong>{module['name']}</strong>
                    </div>
                    <div style="background: #f0f0f0; border-radius: 10px; overflow: hidden; height: 20px;">
                        <div style="
                            background: {color};
                            width: {percentage}%;
                            height: 100%;
                            border-radius: 10px;
                            transition: width 0.3s ease;
                        "></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"<div style='text-align: center; font-weight: bold; font-size: 1.1rem;'>{score}/{module['max_score']}</div>", unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"<div style='text-align: center; color: {color}; font-weight: bold;'>{percentage:.0f}%</div>", unsafe_allow_html=True)
    
    def _render_scoring_charts(self, scoring_results: Dict):
        """Графическое представление скоринга"""
        
        st.subheader("📊 Визуализация скоринга")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Радарная диаграмма
            self._create_radar_chart(scoring_results)
        
        with col2:
            # Gauge chart для общего скоринга
            self._create_gauge_chart(scoring_results)
    
    def _create_radar_chart(self, scoring_results: Dict):
        """Создание радарной диаграммы скоринга"""
        
        categories = ['Тренды', 'Запросы', 'Цены', 'Остатки', 'Реклама']
        scores = [
            scoring_results.get("trend_score", 0),
            scoring_results.get("query_score", 0),
            scoring_results.get("price_score", 0),
            scoring_results.get("stock_score", 0),
            scoring_results.get("ads_score", 0)
        ]
        
        # Добавляем первое значение в конец для замыкания контура
        categories_closed = categories + [categories[0]]
        scores_closed = scores + [scores[0]]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=scores_closed,
            theta=categories_closed,
            fill='toself',
            name='Скоринг ниши',
            line=dict(color='#1f77b4', width=2),
            fillcolor='rgba(31, 119, 180, 0.3)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 4],
                    tickvals=[1, 2, 3, 4],
                    ticktext=['1', '2', '3', '4']
                )
            ),
            showlegend=False,
            title="Радар скоринга по модулям",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_gauge_chart(self, scoring_results: Dict):
        """Создание gauge диаграммы для общего скоринга"""
        
        total_score = scoring_results.get("total_score", 0)
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = total_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Общий скоринг ниши"},
            delta = {'reference': 10, 'position': "top"},
            gauge = {
                'axis': {'range': [None, 20], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "darkblue"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 5], 'color': self.color_scheme["poor"]},
                    {'range': [5, 10], 'color': self.color_scheme["average"]},
                    {'range': [10, 15], 'color': self.color_scheme["good"]},
                    {'range': [15, 20], 'color': self.color_scheme["excellent"]}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 15
                }
            }
        ))
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_key_insights(self, analysis_results: Dict):
        """Ключевые инсайты анализа"""
        
        st.subheader("💡 Ключевые инсайты")
        
        insights = []
        
        # Собираем инсайты из разных модулей
        if "trends" in analysis_results:
            trends_summary = analysis_results["trends"].get("summary", {})
            if "growing" in trends_summary:
                growing = trends_summary["growing"]
                declining = trends_summary["declining"]
                if growing > declining:
                    insights.append({"type": "positive", "text": f"📈 {growing} метрик показывают рост"})
                elif declining > growing:
                    insights.append({"type": "negative", "text": f"📉 {declining} метрик показывают спад"})
        
        if "queries" in analysis_results:
            query_data = analysis_results["queries"]
            effective_queries = query_data.get("effective_queries", 0)
            if effective_queries > 50:
                insights.append({"type": "positive", "text": f"🔍 {effective_queries} эффективных запросов найдено"})
            elif effective_queries < 10:
                insights.append({"type": "negative", "text": "🔍 Мало эффективных поисковых запросов"})
        
        if "ads" in analysis_results:
            ads_data = analysis_results["ads"]
            niche_assessment = ads_data.get("niche_assessment", {})
            heat_level = niche_assessment.get("heat_level", 3)
            if heat_level <= 2:
                insights.append({"type": "positive", "text": "🎯 Низкая конкуренция в рекламе"})
            elif heat_level >= 4:
                insights.append({"type": "negative", "text": "🎯 Высокая конкуренция в рекламе"})
        
        # Отображаем инсайты
        if insights:
            for insight in insights[:6]:  # Максимум 6 инсайтов
                if insight["type"] == "positive":
                    st.success(insight["text"])
                elif insight["type"] == "negative":
                    st.error(insight["text"])
                else:
                    st.info(insight["text"])
        else:
            st.info("Инсайты будут доступны после завершения всех модулей анализа")
    
    def render_module_metrics(self, module_name: str, module_data: Dict, module_score: int):
        """Рендер метрик для конкретного модуля"""
        
        st.subheader(f"📊 Метрики модуля: {module_name}")
        
        # Общий скор модуля
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            score_percentage = (module_score / 4) * 100
            color = self._get_score_color(score_percentage)
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(90deg, {color} 0%, {color}80 100%);
                padding: 2rem;
                border-radius: 15px;
                color: white;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-bottom: 2rem;
            ">
                <h1 style="margin: 0; font-size: 4rem;">{module_score}</h1>
                <h2 style="margin: 0; opacity: 0.9;">из 4 баллов</h2>
                <h3 style="margin: 0.5rem 0 0 0;">{module_name}</h3>
            </div>
            """, unsafe_allow_html=True)
        
        # Специфичные метрики для каждого модуля
        if module_name == "Анализ трендов":
            self._render_trends_metrics(module_data)
        elif module_name == "Анализ запросов":
            self._render_queries_metrics(module_data)
        elif module_name == "Ценовая сегментация":
            self._render_price_metrics(module_data)
        elif module_name == "Анализ остатков":
            self._render_stock_metrics(module_data)
        elif module_name == "Рекламный анализ":
            self._render_ads_metrics(module_data)
    
    def _render_trends_metrics(self, trends_data: Dict):
        """Метрики модуля трендов"""
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Пиковые месяцы
        peak_months = trends_data.get("peak_months_by_year", {})
        if peak_months:
            with col1:
                st.metric("Лет анализа", len(peak_months))
        
        # YoY изменения
        yoy_changes = trends_data.get("yoy_changes", {})
        if "brands_with_sales" in yoy_changes:
            change_data = yoy_changes["brands_with_sales"]
            with col2:
                avg_change = change_data.get("avg_yoy_change", 0)
                st.metric("Рост брендов", f"{avg_change:+.1f}%")
        
        if "avg_check" in yoy_changes:
            change_data = yoy_changes["avg_check"]
            with col3:
                avg_change = change_data.get("avg_yoy_change", 0)
                st.metric("Изменение чека", f"{avg_change:+.1f}%")
        
        # Общий тренд
        growing_metrics = sum(1 for metric_data in yoy_changes.values() 
                            if isinstance(metric_data, dict) and metric_data.get("avg_yoy_change", 0) > 0)
        
        with col4:
            st.metric("Растущих метрик", f"{growing_metrics}/5")
    
    def _render_queries_metrics(self, queries_data: Dict):
        """Метрики модуля запросов"""
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_queries = queries_data.get("total_queries", 0)
            st.metric("Всего запросов", total_queries)
        
        with col2:
            effective_queries = queries_data.get("effective_queries", 0)
            st.metric("Эффективных", effective_queries)
        
        with col3:
            efficiency_ratio = queries_data.get("efficiency_ratio", 0)
            st.metric("% эффективности", f"{efficiency_ratio:.1f}%")
        
        with col4:
            avg_frequency = queries_data.get("avg_frequency", 0)
            st.metric("Средняя частота", f"{avg_frequency:,.0f}")
    
    def _render_price_metrics(self, price_data: Dict):
        """Метрики модуля ценовой сегментации"""
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_segments = price_data.get("total_segments", 0)
            st.metric("Ценовых сегментов", total_segments)
        
        with col2:
            best_revenue = price_data.get("best_revenue_per_product", 0)
            st.metric("Лучшая выручка/товар", f"{best_revenue:,.0f} ₽")
        
        with col3:
            attractive_segments = price_data.get("attractive_segments", 0)
            st.metric("Привлекательных", attractive_segments)
        
        with col4:
            avg_competition = price_data.get("avg_competition", 0)
            st.metric("Средняя конкуренция", f"{avg_competition:.0f}")
    
    def _render_stock_metrics(self, stock_data: Dict):
        """Метрики модуля остатков"""
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_days = stock_data.get("total_days", 0)
            st.metric("Дней анализа", total_days)
        
        with col2:
            avg_stock = stock_data.get("avg_stock", 0)
            st.metric("Средний остаток", f"{avg_stock:,.0f}")
        
        with col3:
            stockout_percentage = stock_data.get("stockout_percentage", 0)
            st.metric("% дефицитов", f"{stockout_percentage:.1f}%")
        
        with col4:
            turnover_days = stock_data.get("turnover_days", "N/A")
            if turnover_days != "N/A":
                st.metric("Оборачиваемость", f"{turnover_days:.0f} дн.")
            else:
                st.metric("Оборачиваемость", "N/A")
    
    def _render_ads_metrics(self, ads_data: Dict):
        """Метрики модуля рекламы"""
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            top_10_count = ads_data.get("top_10_count", 0)
            st.metric("Товаров в ТОП-10", top_10_count)
        
        with col2:
            avg_cmp_top10 = ads_data.get("avg_cmp_top10", 0)
            st.metric("Ставка ТОП-10", f"{avg_cmp_top10:.0f} ₽")
        
        with col3:
            avg_ratio_top10 = ads_data.get("avg_ratio_top10", 0)
            st.metric("Коэффициент ТОП-10", f"{avg_ratio_top10:.1f}")
        
        with col4:
            organic_products = ads_data.get("organic_products", 0)
            st.metric("Органических", organic_products)
    
    def _get_rating_config(self, rating: str) -> Dict:
        """Получение конфигурации для рейтинга"""
        configs = {
            "excellent": {"color": "#28a745", "emoji": "🚀", "title": "Отличная ниша"},
            "good": {"color": "#ffc107", "emoji": "👍", "title": "Хорошая ниша"},
            "average": {"color": "#fd7e14", "emoji": "⚠️", "title": "Средняя ниша"},
            "poor": {"color": "#dc3545", "emoji": "👎", "title": "Сложная ниша"}
        }
        return configs.get(rating, configs["poor"])
    
    def _get_score_color(self, percentage: float) -> str:
        """Получение цвета на основе процента"""
        if percentage >= 75:
            return self.color_scheme["excellent"]
        elif percentage >= 50:
            return self.color_scheme["good"]
        elif percentage >= 25:
            return self.color_scheme["average"]
        else:
            return self.color_scheme["poor"]
    
    def render_comparison_dashboard(self, current_results: Dict, previous_results: Dict = None):
        """Дашборд сравнения с предыдущими результатами"""
        
        st.subheader("📈 Сравнение результатов")
        
        if not previous_results:
            st.info("Нет данных для сравнения. Результаты будут сохранены для следующего анализа.")
            return
        
        # Сравнение общих скоров
        col1, col2, col3 = st.columns(3)
        
        current_score = current_results.get("total_score", 0)
        previous_score = previous_results.get("total_score", 0)
        score_change = current_score - previous_score
        
        with col1:
            st.metric("Текущий скор", current_score, delta=score_change)
        
        with col2:
            current_rating = current_results.get("niche_rating", "poor")
            previous_rating = previous_results.get("niche_rating", "poor")
            st.metric("Рейтинг ниши", current_rating.title(), 
                     delta=f"Был: {previous_rating.title()}" if current_rating != previous_rating else None)
        
        with col3:
            improvement_percentage = ((current_score / previous_score - 1) * 100) if previous_score > 0 else 0
            st.metric("Улучшение", f"{improvement_percentage:+.1f}%")
        
        # Детальное сравнение по модулям
        modules = ["trend_score", "query_score", "price_score", "stock_score", "ads_score"]
        
        comparison_data = []
        for module in modules:
            current_val = current_results.get(module, 0)
            previous_val = previous_results.get(module, 0)
            change = current_val - previous_val
            
            comparison_data.append({
                "Модуль": module.replace("_score", "").title(),
                "Текущий": current_val,
                "Предыдущий": previous_val,
                "Изменение": change
            })
        
        st.dataframe(pd.DataFrame(comparison_data), use_container_width=True)
