import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import streamlit as st


class TrendAnalyzer:
    """Анализатор трендов и пиковых месяцев"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        self.prepare_data()
        
    def prepare_data(self):
        """Подготовка данных для анализа"""
        if 'Месяц' in self.data.columns:
            self.data['Месяц'] = pd.to_datetime(self.data['Месяц'])
            self.data['Год'] = self.data['Месяц'].dt.year
            self.data['Месяц_номер'] = self.data['Месяц'].dt.month
            self.data['Месяц_название'] = self.data['Месяц'].dt.strftime('%B')
    
    def get_peak_months_analysis(self) -> Dict:
        """Анализ пиковых месяцев продаж"""
        peak_analysis = {
            "peak_months_by_year": {},
            "overall_peak_months": {},
            "seasonal_pattern": {},
            "recommendations": []
        }
        
        try:
            # Пиковые месяцы по годам
            for year in sorted(self.data['Год'].unique()):
                year_data = self.data[self.data['Год'] == year]
                if not year_data.empty and 'Продажи' in year_data.columns:
                    max_sales_idx = year_data['Продажи'].idxmax()
                    peak_month = year_data.loc[max_sales_idx, 'Месяц_номер']
                    peak_sales = year_data.loc[max_sales_idx, 'Продажи']
                    
                    peak_analysis["peak_months_by_year"][year] = {
                        "month": peak_month,
                        "month_name": self._get_month_name(peak_month),
                        "sales": peak_sales,
                        "revenue": year_data.loc[max_sales_idx, 'Выручка, ₽'] if 'Выручка, ₽' in year_data.columns else 0
                    }
            
            # Общие пиковые месяцы (наиболее частые)
            if peak_analysis["peak_months_by_year"]:
                peak_months_list = [data["month"] for data in peak_analysis["peak_months_by_year"].values()]
                month_counts = pd.Series(peak_months_list).value_counts()
                
                for month, count in month_counts.head(3).items():
                    peak_analysis["overall_peak_months"][self._get_month_name(month)] = {
                        "month_number": month,
                        "years_count": count,
                        "frequency": f"{count}/{len(peak_analysis['peak_months_by_year'])} лет"
                    }
            
            # Сезонный паттерн (средние продажи по месяцам)
            if 'Продажи' in self.data.columns:
                monthly_avg = self.data.groupby('Месяц_номер')['Продажи'].mean().round(0)
                for month, avg_sales in monthly_avg.items():
                    peak_analysis["seasonal_pattern"][self._get_month_name(month)] = {
                        "month_number": month,
                        "avg_sales": avg_sales,
                        "relative_index": round(avg_sales / monthly_avg.mean(), 2)
                    }
            
            # Рекомендации
            peak_analysis["recommendations"] = self._generate_peak_recommendations(peak_analysis)
            
        except Exception as e:
            peak_analysis["error"] = str(e)
        
        return peak_analysis
    
    def get_yoy_dynamics_analysis(self) -> Dict:
        """Анализ YoY динамики всех метрик"""
        dynamics = {
            "metrics_analysis": {},
            "summary": {},
            "trends_direction": {},
            "recommendations": []
        }
        
        try:
            metrics = [
                ("brands_with_sales", "Бренды с продажами", "Бренды с продажами"),
                ("brands_total", "Бренды", "Общее количество брендов"),
                ("products_with_sales", "Товары с продажами", "Товары с продажами"),
                ("products_total", "Товары", "Общее количество товаров"),
                ("avg_check", "Средний чек, ₽", "Средний чек"),
                ("sellers_with_sales", "Продавцы с продажами", "Продавцы с продажами"),
                ("revenue_per_product", "Выручка на товар, ₽", "Выручка на товар")
            ]
            
            for metric_key, column_name, display_name in metrics:
                if column_name in self.data.columns:
                    analysis = self._analyze_metric_yoy(column_name, display_name)
                    dynamics["metrics_analysis"][metric_key] = analysis
            
            # Сводка по направлениям трендов
            trends_summary = {"growing": 0, "stable": 0, "declining": 0}
            for metric_data in dynamics["metrics_analysis"].values():
                trend = metric_data.get("overall_trend", "stable")
                if "рост" in trend.lower():
                    trends_summary["growing"] += 1
                elif "снижение" in trend.lower():
                    trends_summary["declining"] += 1
                else:
                    trends_summary["stable"] += 1
            
            dynamics["summary"] = trends_summary
            dynamics["recommendations"] = self._generate_dynamics_recommendations(dynamics)
            
        except Exception as e:
            dynamics["error"] = str(e)
        
        return dynamics
    
    def _analyze_metric_yoy(self, column_name: str, display_name: str) -> Dict:
        """Анализ YoY динамики для конкретной метрики"""
        try:
            # Группируем по годам
            yearly_data = self.data.groupby('Год')[column_name].mean().sort_index()
            
            if len(yearly_data) < 2:
                return {
                    "error": "Недостаточно данных для YoY анализа",
                    "yearly_values": yearly_data.to_dict()
                }
            
            # Рассчитываем YoY изменения
            yoy_changes = []
            for i in range(1, len(yearly_data)):
                prev_value = yearly_data.iloc[i-1]
                curr_value = yearly_data.iloc[i]
                
                if prev_value > 0:
                    change_percent = ((curr_value - prev_value) / prev_value) * 100
                    yoy_changes.append({
                        "year": yearly_data.index[i],
                        "prev_year": yearly_data.index[i-1],
                        "change_percent": round(change_percent, 2),
                        "prev_value": round(prev_value, 2),
                        "curr_value": round(curr_value, 2)
                    })
            
            # Средний YoY рост
            avg_yoy = np.mean([change["change_percent"] for change in yoy_changes])
            
            # Определяем тренд
            if avg_yoy >= 10:
                trend = "Отличный рост"
                trend_score = 4
            elif avg_yoy >= 0:
                trend = "Умеренный рост"
                trend_score = 3
            elif avg_yoy >= -5:
                trend = "Стабильность"
                trend_score = 2
            else:
                trend = "Снижение"
                trend_score = 1
            
            return {
                "display_name": display_name,
                "yearly_values": yearly_data.to_dict(),
                "yoy_changes": yoy_changes,
                "avg_yoy_change": round(avg_yoy, 2),
                "overall_trend": trend,
                "trend_score": trend_score,
                "latest_value": round(yearly_data.iloc[-1], 2),
                "total_change": round(((yearly_data.iloc[-1] - yearly_data.iloc[0]) / yearly_data.iloc[0]) * 100, 2) if yearly_data.iloc[0] > 0 else 0
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def create_trends_charts(self) -> Dict[str, go.Figure]:
        """Создание графиков трендов"""
        charts = {}
        
        try:
            # 1. График продаж по месяцам
            fig_sales = px.line(
                self.data, 
                x='Месяц', 
                y='Продажи',
                title='Динамика продаж по месяцам',
                labels={'Продажи': 'Количество продаж', 'Месяц': 'Период'}
            )
            fig_sales.update_layout(height=400)
            charts["sales_trend"] = fig_sales
            
            # 2. График выручки по месяцам
            if 'Выручка, ₽' in self.data.columns:
                fig_revenue = px.line(
                    self.data,
                    x='Месяц',
                    y='Выручка, ₽',
                    title='Динамика выручки по месяцам',
                    labels={'Выручка, ₽': 'Выручка (₽)', 'Месяц': 'Период'}
                )
                fig_revenue.update_layout(height=400)
                charts["revenue_trend"] = fig_revenue
            
            # 3. Сравнение брендов и товаров
            if all(col in self.data.columns for col in ['Бренды', 'Товары', 'Бренды с продажами', 'Товары с продажами']):
                fig_comparison = make_subplots(
                    rows=2, cols=1,
                    subplot_titles=['Динамика брендов', 'Динамика товаров'],
                    vertical_spacing=0.1
                )
                
                # Бренды
                fig_comparison.add_trace(
                    go.Scatter(x=self.data['Месяц'], y=self.data['Бренды'], 
                              name='Всего брендов', line=dict(color='blue')),
                    row=1, col=1
                )
                fig_comparison.add_trace(
                    go.Scatter(x=self.data['Месяц'], y=self.data['Бренды с продажами'], 
                              name='Бренды с продажами', line=dict(color='green')),
                    row=1, col=1
                )
                
                # Товары
                fig_comparison.add_trace(
                    go.Scatter(x=self.data['Месяц'], y=self.data['Товары'], 
                              name='Всего товаров', line=dict(color='red')),
                    row=2, col=1
                )
                fig_comparison.add_trace(
                    go.Scatter(x=self.data['Месяц'], y=self.data['Товары с продажами'], 
                              name='Товары с продажами', line=dict(color='orange')),
                    row=2, col=1
                )
                
                fig_comparison.update_layout(height=600, title_text="Сравнение динамики брендов и товаров")
                charts["brands_products_comparison"] = fig_comparison
            
            # 4. Сезонный график (средние значения по месяцам)
            seasonal_data = self.data.groupby('Месяц_номер').agg({
                'Продажи': 'mean',
                'Выручка, ₽': 'mean' if 'Выручка, ₽' in self.data.columns else lambda x: 0,
                'Средний чек, ₽': 'mean' if 'Средний чек, ₽' in self.data.columns else lambda x: 0
            }).reset_index()
            
            seasonal_data['Месяц_название'] = seasonal_data['Месяц_номер'].apply(self._get_month_name)
            
            fig_seasonal = px.bar(
                seasonal_data,
                x='Месяц_название',
                y='Продажи',
                title='Сезонность продаж (средние значения по месяцам)',
                labels={'Продажи': 'Среднее количество продаж', 'Месяц_название': 'Месяц'}
            )
            fig_seasonal.update_layout(height=400)
            charts["seasonal_pattern"] = fig_seasonal
            
            # 5. Heatmap сезонности
            if len(self.data['Год'].unique()) > 1:
                heatmap_data = self.data.pivot_table(
                    values='Продажи',
                    index='Год',
                    columns='Месяц_номер',
                    aggfunc='mean'
                ).fillna(0)
                
                # Переименовываем колонки в названия месяцев
                month_names = {i: self._get_month_name(i) for i in range(1, 13)}
                heatmap_data.columns = [month_names.get(col, str(col)) for col in heatmap_data.columns]
                
                fig_heatmap = px.imshow(
                    heatmap_data,
                    title='Тепловая карта продаж по годам и месяцам',
                    labels={'x': 'Месяц', 'y': 'Год', 'color': 'Продажи'},
                    aspect='auto'
                )
                fig_heatmap.update_layout(height=400)
                charts["sales_heatmap"] = fig_heatmap
            
        except Exception as e:
            st.error(f"Ошибка при создании графиков трендов: {e}")
        
        return charts
    
    def _get_month_name(self, month_number: int) -> str:
        """Получение названия месяца по номеру"""
        months = {
            1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
            5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
            9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
        }
        return months.get(month_number, f"Месяц {month_number}")
    
    def _generate_peak_recommendations(self, peak_analysis: Dict) -> List[str]:
        """Генерация рекомендаций по пиковым месяцам"""
        recommendations = []
        
        try:
            if peak_analysis["overall_peak_months"]:
                top_peak_month = list(peak_analysis["overall_peak_months"].keys())[0]
                recommendations.append(f"🔥 Основной пиковый месяц: {top_peak_month}")
                
                # Рекомендации по подготовке к сезону
                peak_month_num = peak_analysis["overall_peak_months"][top_peak_month]["month_number"]
                prep_month = peak_month_num - 2 if peak_month_num > 2 else peak_month_num + 10
                prep_month_name = self._get_month_name(prep_month)
                
                recommendations.append(f"📦 Рекомендуется начинать подготовку товаров в {prep_month_name}")
                
                # Анализ стабильности пиков
                years_count = len(peak_analysis["peak_months_by_year"])
                if years_count >= 3:
                    consistent_peaks = sum(1 for data in peak_analysis["overall_peak_months"].values() if data["years_count"] >= years_count * 0.6)
                    if consistent_peaks > 0:
                        recommendations.append("✅ Сезонность стабильная - можно планировать на основе исторических данных")
                    else:
                        recommendations.append("⚠️ Сезонность нестабильная - требуется более гибкое планирование")
            
        except Exception as e:
            recommendations.append(f"Ошибка в генерации рекомендаций: {e}")
        
        return recommendations
    
    def _generate_dynamics_recommendations(self, dynamics: Dict) -> List[str]:
        """Генерация рекомендаций по динамике"""
        recommendations = []
        
        try:
            summary = dynamics["summary"]
            total_metrics = summary["growing"] + summary["stable"] + summary["declining"]
            
            if summary["growing"] >= total_metrics * 0.6:
                recommendations.append("🚀 Ниша показывает уверенный рост - отличное время для входа")
            elif summary["declining"] >= total_metrics * 0.6:
                recommendations.append("⚠️ Ниша в стадии спада - высокие риски")
            else:
                recommendations.append("📊 Ниша в стабильном состоянии - умеренные риски")
            
            # Специфические рекомендации по метрикам
            for metric_key, metric_data in dynamics["metrics_analysis"].items():
                if "error" not in metric_data:
                    trend_score = metric_data.get("trend_score", 2)
                    if metric_key == "avg_check" and trend_score <= 2:
                        recommendations.append("💰 Средний чек снижается - возможен ценовой демпинг")
                    elif metric_key == "brands_with_sales" and trend_score >= 3:
                        recommendations.append("🏢 Количество брендов с продажами растет - ниша привлекательна")
                    elif metric_key == "products_total" and trend_score <= 2:
                        recommendations.append("📦 Количество товаров сокращается - возможна оптимизация ассортимента")
        
        except Exception as e:
            recommendations.append(f"Ошибка в анализе динамики: {e}")
        
        return recommendations
    
    def get_summary_metrics(self) -> Dict:
        """Получение сводных метрик для дашборда"""
        try:
            latest_data = self.data.iloc[-1] if not self.data.empty else {}
            earliest_data = self.data.iloc[0] if not self.data.empty else {}
            
            summary = {
                "period_start": earliest_data.get('Месяц', '').strftime('%Y-%m') if 'Месяц' in earliest_data else 'N/A',
                "period_end": latest_data.get('Месяц', '').strftime('%Y-%m') if 'Месяц' in latest_data else 'N/A',
                "total_months": len(self.data),
                "avg_monthly_sales": round(self.data['Продажи'].mean(), 0) if 'Продажи' in self.data.columns else 0,
                "total_sales": self.data['Продажи'].sum() if 'Продажи' in self.data.columns else 0,
                "peak_sales": self.data['Продажи'].max() if 'Продажи' in self.data.columns else 0,
                "avg_brands": round(self.data['Бренды'].mean(), 0) if 'Бренды' in self.data.columns else 0,
                "avg_products": round(self.data['Товары'].mean(), 0) if 'Товары' in self.data.columns else 0
            }
            
            return summary
            
        except Exception as e:
            return {"error": str(e)}
