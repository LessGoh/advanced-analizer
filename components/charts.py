import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Optional, Any


class Charts:
    """Компонент для создания и отображения графиков"""
    
    def __init__(self):
        self.default_height = 400
        self.color_palette = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
    
    def render_trend_charts(self, data: pd.DataFrame) -> None:
        """Отображение графиков трендов"""
        
        if data.empty:
            st.warning("Нет данных для отображения")
            return
        
        # График продаж по времени
        if 'Месяц' in data.columns and 'Продажи' in data.columns:
            fig_sales = px.line(
                data,
                x='Месяц',
                y='Продажи',
                title='Динамика продаж по месяцам',
                labels={'Продажи': 'Количество продаж', 'Месяц': 'Период'}
            )
            fig_sales.update_layout(height=self.default_height)
            st.plotly_chart(fig_sales, use_container_width=True)
        
        # График выручки
        if 'Месяц' in data.columns and 'Выручка, ₽' in data.columns:
            fig_revenue = px.line(
                data,
                x='Месяц',
                y='Выручка, ₽',
                title='Динамика выручки по месяцам',
                labels={'Выручка, ₽': 'Выручка (₽)', 'Месяц': 'Период'}
            )
            fig_revenue.update_layout(height=self.default_height)
            st.plotly_chart(fig_revenue, use_container_width=True)
    
    def render_query_charts(self, data: pd.DataFrame) -> None:
        """Отображение графиков запросов"""
        
        if data.empty:
            st.warning("Нет данных для отображения")
            return
        
        # Scatter plot спрос vs предложение
        if all(col in data.columns for col in ['Товаров в запросе', 'Частота WB', 'Коэффициент_спрос_предложение']):
            fig_scatter = px.scatter(
                data.head(500),  # Ограничиваем для производительности
                x='Товаров в запросе',
                y='Частота WB',
                color='Коэффициент_спрос_предложение',
                title='Соотношение спроса и предложения',
                color_continuous_scale='RdYlGn'
            )
            fig_scatter.update_layout(height=self.default_height)
            st.plotly_chart(fig_scatter, use_container_width=True)
    
    def render_price_charts(self, data: pd.DataFrame) -> None:
        """Отображение графиков ценовой сегментации"""
        
        if data.empty:
            st.warning("Нет данных для отображения")
            return
        
        # График выручки на товар по сегментам
        if all(col in data.columns for col in ['От', 'До', 'Выручка на товар, ₽']):
            data['Ценовой_диапазон'] = data['От'].astype(str) + '-' + data['До'].astype(str) + ' ₽'
            
            fig_revenue = px.bar(
                data,
                x='Ценовой_диапазон',
                y='Выручка на товар, ₽',
                title='Выручка на товар по ценовым сегментам'
            )
            fig_revenue.update_layout(height=self.default_height)
            fig_revenue.update_xaxes(tickangle=45)
            st.plotly_chart(fig_revenue, use_container_width=True)
    
    def render_stock_charts(self, data: pd.DataFrame) -> None:
        """Отображение графиков остатков"""
        
        if data.empty:
            st.warning("Нет данных для отображения")
            return
        
        # График остатков по времени
        if 'Дата' in data.columns and 'Остаток' in data.columns:
            fig_stock = px.line(
                data,
                x='Дата',
                y='Остаток',
                title='Динамика остатков по дням'
            )
            fig_stock.update_layout(height=self.default_height)
            st.plotly_chart(fig_stock, use_container_width=True)
    
    def render_ads_charts(self, data: pd.DataFrame) -> None:
        """Отображение графиков рекламного анализа"""
        
        if data.empty:
            st.warning("Нет данных для отображения")
            return
        
        # Scatter plot цена vs ставка
        required_cols = ['Final price', 'Search cpm avg', 'Category position avg']
        if all(col in data.columns for col in required_cols):
            
            # Фильтруем данные с рекламой
            ads_data = data[data['Search cpm avg'] > 0]
            
            if not ads_data.empty:
                fig_ads = px.scatter(
                    ads_data.head(200),  # Ограничиваем для производительности
                    x='Search cpm avg',
                    y='Final price',
                    color='Category position avg',
                    title='Соотношение цены и рекламной ставки'
                )
                fig_ads.update_layout(height=self.default_height)
                st.plotly_chart(fig_ads, use_container_width=True)
    
    def render_scoring_radar(self, scores: Dict[str, int]) -> None:
        """Радарная диаграмма скоринга"""
        
        categories = list(scores.keys())
        values = list(scores.values())
        
        # Добавляем первое значение в конец для замыкания
        categories_closed = categories + [categories[0]]
        values_closed = values + [values[0]]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill='toself',
            name='Скоринг',
            line=dict(color='#1f77b4', width=2),
            fillcolor='rgba(31, 119, 180, 0.3)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 4],
                    tickvals=[1, 2, 3, 4]
                )
            ),
            showlegend=False,
            title="Радар скоринга",
            height=self.default_height
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_gauge_chart(self, value: int, max_value: int = 20, title: str = "Общий скоринг") -> None:
        """Gauge диаграмма"""
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title},
            delta={'reference': max_value // 2},
            gauge={
                'axis': {'range': [None, max_value]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, max_value * 0.25], 'color': "lightgray"},
                    {'range': [max_value * 0.25, max_value * 0.5], 'color': "yellow"},
                    {'range': [max_value * 0.5, max_value * 0.75], 'color': "orange"},
                    {'range': [max_value * 0.75, max_value], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': max_value * 0.75
                }
            }
        ))
        
        fig.update_layout(height=self.default_height)
        st.plotly_chart(fig, use_container_width=True)
    
    def render_comparison_chart(self, data: Dict[str, List], title: str = "Сравнение метрик") -> None:
        """График сравнения метрик"""
        
        df = pd.DataFrame(data)
        
        if df.empty:
            st.warning("Нет данных для сравнения")
            return
        
        fig = px.bar(
            df,
            x=df.columns[0],  # Первая колонка как x
            y=df.columns[1:],  # Остальные как y
            title=title,
            barmode='group'
        )
        
        fig.update_layout(height=self.default_height)
        st.plotly_chart(fig, use_container_width=True)
    
    def render_heatmap(self, data: pd.DataFrame, title: str = "Тепловая карта") -> None:
        """Тепловая карта"""
        
        if data.empty:
            st.warning("Нет данных для тепловой карты")
            return
        
        fig = px.imshow(
            data,
            title=title,
            color_continuous_scale='RdYlGn'
        )
        
        fig.update_layout(height=self.default_height)
        st.plotly_chart(fig, use_container_width=True)
    
    def render_distribution_chart(self, data: pd.Series, title: str = "Распределение") -> None:
        """График распределения"""
        
        if data.empty:
            st.warning("Нет данных для распределения")
            return
        
        fig = px.histogram(
            x=data,
            title=title,
            nbins=20
        )
        
        fig.update_layout(height=self.default_height)
        st.plotly_chart(fig, use_container_width=True)
