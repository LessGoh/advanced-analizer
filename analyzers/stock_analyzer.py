import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import streamlit as st


class StockAnalyzer:
    """Анализатор остатков и сезонности"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        self.prepare_data()
        
    def prepare_data(self):
        """Подготовка данных для анализа"""
        # Преобразуем дату
        if 'Дата' in self.data.columns:
            self.data['Дата'] = pd.to_datetime(self.data['Дата'])
            self.data['Год'] = self.data['Дата'].dt.year
            self.data['Месяц'] = self.data['Дата'].dt.month
            self.data['Месяц_название'] = self.data['Дата'].dt.strftime('%B')
            self.data['День_года'] = self.data['Дата'].dt.dayofyear
            self.data['Неделя'] = self.data['Дата'].dt.isocalendar().week
            self.data['Квартал'] = self.data['Дата'].dt.quarter
        
        # Убираем записи с отрицательными остатками (если есть)
        if 'Остаток' in self.data.columns:
            self.data = self.data[self.data['Остаток'] >= 0]
            
            # Добавляем производные метрики
            self.data['Остаток_категория'] = self.data['Остаток'].apply(self._categorize_stock_level)
            self.data['Скользящее_среднее_7д'] = self.data['Остаток'].rolling(window=7, center=True).mean()
            self.data['Скользящее_среднее_30д'] = self.data['Остаток'].rolling(window=30, center=True).mean()
            
            # Рассчитываем изменения остатков
            self.data['Изменение_остатка'] = self.data['Остаток'].diff()
            self.data['Изменение_остатка_процент'] = self.data['Остаток'].pct_change() * 100
    
    def _categorize_stock_level(self, stock: float) -> str:
        """Категоризация уровня остатков"""
        if pd.isna(stock) or stock == 0:
            return "Нет остатков"
        elif stock <= 1000:
            return "Низкий уровень"
        elif stock <= 10000:
            return "Средний уровень"
        elif stock <= 50000:
            return "Высокий уровень"
        else:
            return "Очень высокий уровень"
    
    def get_seasonal_analysis(self) -> Dict:
        """Анализ сезонности остатков"""
        analysis = {
            "monthly_patterns": {},
            "peak_stock_months": {},
            "seasonal_insights": {},
            "recommendations": []
        }
        
        try:
            # Анализ по месяцам
            monthly_stats = self.data.groupby('Месяц').agg({
                'Остаток': ['mean', 'max', 'min', 'std'],
                'Дата': 'count'
            }).round(0)
            
            # Упрощаем структуру колонок
            monthly_stats.columns = ['Средний_остаток', 'Максимальный_остаток', 'Минимальный_остаток', 'Стандартное_отклонение', 'Количество_дней']
            
            for month in range(1, 13):
                if month in monthly_stats.index:
                    stats = monthly_stats.loc[month]
                    analysis["monthly_patterns"][self._get_month_name(month)] = {
                        "month_number": month,
                        "avg_stock": int(stats['Средний_остаток']),
                        "max_stock": int(stats['Максимальный_остаток']),
                        "min_stock": int(stats['Минимальный_остаток']),
                        "volatility": int(stats['Стандартное_отклонение']),
                        "days_count": int(stats['Количество_дней'])
                    }
            
            # Пиковые месяцы по годам
            for year in sorted(self.data['Год'].unique()):
                year_data = self.data[self.data['Год'] == year]
                if not year_data.empty:
                    monthly_avg = year_data.groupby('Месяц')['Остаток'].mean()
                    if not monthly_avg.empty:
                        peak_month = monthly_avg.idxmax()
                        peak_stock = monthly_avg[peak_month]
                        
                        analysis["peak_stock_months"][year] = {
                            "month": peak_month,
                            "month_name": self._get_month_name(peak_month),
                            "avg_stock": round(peak_stock, 0),
                            "relative_peak": round((peak_stock / monthly_avg.mean()) * 100, 1)
                        }
            
            # Сезонные инсайты
            if len(analysis["monthly_patterns"]) >= 6:  # Минимум полгода данных
                analysis["seasonal_insights"] = self._calculate_seasonal_insights()
            
            analysis["recommendations"] = self._generate_seasonal_recommendations(analysis)
            
        except Exception as e:
            analysis["error"] = str(e)
        
        return analysis
    
    def _calculate_seasonal_insights(self) -> Dict:
        """Расчет сезонных инсайтов"""
        insights = {}
        
        try:
            # Определяем сезоны
            seasons = {
                "Зима": [12, 1, 2],
                "Весна": [3, 4, 5], 
                "Лето": [6, 7, 8],
                "Осень": [9, 10, 11]
            }
            
            seasonal_stats = {}
            for season, months in seasons.items():
                season_data = self.data[self.data['Месяц'].isin(months)]
                if not season_data.empty:
                    seasonal_stats[season] = {
                        "avg_stock": round(season_data['Остаток'].mean(), 0),
                        "max_stock": round(season_data['Остаток'].max(), 0),
                        "volatility": round(season_data['Остаток'].std(), 0),
                        "days_without_stock": len(season_data[season_data['Остаток'] == 0])
                    }
            
            insights["seasonal_breakdown"] = seasonal_stats
            
            # Определяем самый и наименее стабильные сезоны
            if seasonal_stats:
                most_volatile = max(seasonal_stats.items(), key=lambda x: x[1]["volatility"])
                least_volatile = min(seasonal_stats.items(), key=lambda x: x[1]["volatility"])
                
                insights["volatility_analysis"] = {
                    "most_volatile_season": most_volatile[0],
                    "most_volatile_value": most_volatile[1]["volatility"],
                    "least_volatile_season": least_volatile[0],
                    "least_volatile_value": least_volatile[1]["volatility"]
                }
                
                # Сезон с максимальными остатками
                highest_stock = max(seasonal_stats.items(), key=lambda x: x[1]["avg_stock"])
                lowest_stock = min(seasonal_stats.items(), key=lambda x: x[1]["avg_stock"])
                
                insights["stock_level_analysis"] = {
                    "highest_stock_season": highest_stock[0],
                    "highest_stock_value": highest_stock[1]["avg_stock"],
                    "lowest_stock_season": lowest_stock[0],
                    "lowest_stock_value": lowest_stock[1]["avg_stock"]
                }
            
        except Exception as e:
            insights["error"] = str(e)
        
        return insights
    
    def get_supply_chain_analysis(self) -> Dict:
        """Анализ цепочки поставок"""
        analysis = {
            "restocking_patterns": {},
            "stockout_analysis": {},
            "inventory_turnover": {},
            "recommendations": []
        }
        
        try:
            # Анализ пополнений (резкие увеличения остатков)
            self.data['Пополнение'] = (self.data['Изменение_остатка'] > self.data['Изменение_остатка'].quantile(0.9)) & (self.data['Изменение_остатка'] > 0)
            
            restocking_events = self.data[self.data['Пополнение'] == True]
            if not restocking_events.empty:
                restocking_by_month = restocking_events.groupby('Месяц').agg({
                    'Дата': 'count',
                    'Изменение_остатка': 'mean'
                }).round(0)
                
                analysis["restocking_patterns"] = {
                    "total_restocking_events": len(restocking_events),
                    "avg_restocking_size": round(restocking_events['Изменение_остатка'].mean(), 0),
                    "restocking_by_month": {
                        self._get_month_name(month): {
                            "events": int(row['Дата']),
                            "avg_size": int(row['Изменение_остатка'])
                        }
                        for month, row in restocking_by_month.iterrows()
                    }
                }
            
            # Анализ дефицитов (дни с нулевыми остатками)
            stockout_days = self.data[self.data['Остаток'] == 0]
            total_days = len(self.data)
            
            if not stockout_days.empty:
                stockout_by_month = stockout_days.groupby('Месяц')['Дата'].count()
                
                analysis["stockout_analysis"] = {
                    "total_stockout_days": len(stockout_days),
                    "stockout_percentage": round((len(stockout_days) / total_days) * 100, 2),
                    "stockout_by_month": {
                        self._get_month_name(month): count
                        for month, count in stockout_by_month.items()
                    },
                    "avg_stockout_duration": self._calculate_avg_stockout_duration(stockout_days)
                }
            else:
                analysis["stockout_analysis"] = {
                    "total_stockout_days": 0,
                    "stockout_percentage": 0,
                    "message": "Дефицитов не обнаружено"
                }
            
            # Анализ оборачиваемости запасов
            if all(col in self.data.columns for col in ['Остаток', 'Продажи, шт.']):
                analysis["inventory_turnover"] = self._calculate_inventory_turnover()
            
            analysis["recommendations"] = self._generate_supply_chain_recommendations(analysis)
            
        except Exception as e:
            analysis["error"] = str(e)
        
        return analysis
    
    def _calculate_avg_stockout_duration(self, stockout_days: pd.DataFrame) -> float:
        """Расчет средней продолжительности дефицитов"""
        try:
            # Группируем последовательные дни дефицита
            stockout_days_sorted = stockout_days.sort_values('Дата')
            stockout_days_sorted['Группа'] = (stockout_days_sorted['Дата'].diff().dt.days != 1).cumsum()
            
            durations = stockout_days_sorted.groupby('Группа').size()
            return round(durations.mean(), 1) if not durations.empty else 0
            
        except Exception:
            return 0
    
    def _calculate_inventory_turnover(self) -> Dict:
        """Расчет показателей оборачиваемости"""
        try:
            # Средний остаток
            avg_inventory = self.data['Остаток'].mean()
            
            # Общие продажи за период
            total_sales = self.data['Продажи, шт.'].sum()
            
            # Количество дней в периоде
            date_range = (self.data['Дата'].max() - self.data['Дата'].min()).days + 1
            
            # Оборачиваемость в днях
            if total_sales > 0:
                turnover_days = (avg_inventory * date_range) / total_sales
            else:
                turnover_days = float('inf')
            
            # Оборачиваемость в разах за год
            turnover_times = 365 / turnover_days if turnover_days > 0 and turnover_days != float('inf') else 0
            
            return {
                "avg_inventory": round(avg_inventory, 0),
                "total_sales": round(total_sales, 0),
                "turnover_days": round(turnover_days, 1) if turnover_days != float('inf') else "Нет данных",
                "turnover_times_per_year": round(turnover_times, 2),
                "period_days": date_range
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_demand_forecasting(self) -> Dict:
        """Прогнозирование спроса на основе исторических данных"""
        forecast = {
            "trend_analysis": {},
            "seasonal_forecast": {},
            "recommendations": []
        }
        
        try:
            if len(self.data) < 30:  # Минимум месяц данных
                forecast["error"] = "Недостаточно данных для прогнозирования"
                return forecast
            
            # Трендовый анализ
            days_numeric = (self.data['Дата'] - self.data['Дата'].min()).dt.days
            trend_correlation = days_numeric.corr(self.data['Остаток'])
            
            forecast["trend_analysis"] = {
                "trend_direction": "Растущий" if trend_correlation > 0.3 else "Падающий" if trend_correlation < -0.3 else "Стабильный",
                "trend_strength": abs(trend_correlation),
                "correlation_coefficient": round(trend_correlation, 3)
            }
            
            # Прогноз по сезонности (следующие 3 месяца)
            current_month = self.data['Дата'].max().month
            next_months = [(current_month + i - 1) % 12 + 1 for i in range(1, 4)]
            
            monthly_patterns = self.data.groupby('Месяц')['Остаток'].mean()
            
            seasonal_predictions = {}
            for month in next_months:
                if month in monthly_patterns.index:
                    predicted_stock = monthly_patterns[month]
                    seasonal_predictions[self._get_month_name(month)] = {
                        "predicted_avg_stock": round(predicted_stock, 0),
                        "confidence": "Высокая" if month in monthly_patterns.index else "Низкая"
                    }
            
            forecast["seasonal_forecast"] = seasonal_predictions
            forecast["recommendations"] = self._generate_forecasting_recommendations(forecast)
            
        except Exception as e:
            forecast["error"] = str(e)
        
        return forecast
    
    def create_stock_charts(self) -> Dict[str, go.Figure]:
        """Создание графиков анализа остатков"""
        charts = {}
        
        try:
            # 1. Временной ряд остатков
            fig_timeseries = go.Figure()
            
            fig_timeseries.add_trace(go.Scatter(
                x=self.data['Дата'],
                y=self.data['Остаток'],
                mode='lines',
                name='Остатки',
                line=dict(color='blue', width=2)
            ))
            
            # Добавляем скользящие средние
            if 'Скользящее_среднее_7д' in self.data.columns:
                fig_timeseries.add_trace(go.Scatter(
                    x=self.data['Дата'],
                    y=self.data['Скользящее_среднее_7д'],
                    mode='lines',
                    name='Скольз. среднее 7 дней',
                    line=dict(color='orange', width=1, dash='dash')
                ))
            
            if 'Скользящее_среднее_30д' in self.data.columns:
                fig_timeseries.add_trace(go.Scatter(
                    x=self.data['Дата'],
                    y=self.data['Скользящее_среднее_30д'],
                    mode='lines',
                    name='Скольз. среднее 30 дней',
                    line=dict(color='red', width=1, dash='dot')
                ))
            
            fig_timeseries.update_layout(
                title='Динамика остатков во времени',
                xaxis_title='Дата',
                yaxis_title='Количество остатков',
                height=500
            )
            charts["stock_timeseries"] = fig_timeseries
            
            # 2. Сезонный анализ (box plot по месяцам)
            fig_seasonal = px.box(
                self.data,
                x='Месяц',
                y='Остаток',
                title='Сезонное распределение остатков по месяцам'
            )
            fig_seasonal.update_xaxes(
                tickmode='array',
                tickvals=list(range(1, 13)),
                ticktext=[self._get_month_name(i) for i in range(1, 13)]
            )
            fig_seasonal.update_layout(height=400)
            charts["seasonal_distribution"] = fig_seasonal
            
            # 3. Heatmap остатков по дням недели и месяцам
            if len(self.data['Год'].unique()) > 1:
                self.data['День_недели'] = self.data['Дата'].dt.day_name()
                
                heatmap_data = self.data.pivot_table(
                    values='Остаток',
                    index='Месяц',
                    columns='День_недели',
                    aggfunc='mean'
                ).fillna(0)
                
                # Переупорядочиваем дни недели
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                heatmap_data = heatmap_data.reindex(columns=[day for day in day_order if day in heatmap_data.columns])
                
                fig_heatmap = px.imshow(
                    heatmap_data,
                    title='Тепловая карта остатков по месяцам и дням недели',
                    labels={'x': 'День недели', 'y': 'Месяц', 'color': 'Средние остатки'},
                    color_continuous_scale='Blues'
                )
                fig_heatmap.update_layout(height=400)
                charts["stock_heatmap"] = fig_heatmap
            
            # 4. Анализ пополнений и дефицитов
            if 'Пополнение' in self.data.columns:
                restocking_data = self.data[self.data['Пополнение'] == True]
                stockout_data = self.data[self.data['Остаток'] == 0]
                
                fig_events = go.Figure()
                
                # Основная линия остатков
                fig_events.add_trace(go.Scatter(
                    x=self.data['Дата'],
                    y=self.data['Остаток'],
                    mode='lines',
                    name='Остатки',
                    line=dict(color='blue', width=1)
                ))
                
                # Пополнения
                if not restocking_data.empty:
                    fig_events.add_trace(go.Scatter(
                        x=restocking_data['Дата'],
                        y=restocking_data['Остаток'],
                        mode='markers',
                        name='Пополнения',
                        marker=dict(color='green', size=8, symbol='triangle-up')
                    ))
                
                # Дефициты
                if not stockout_data.empty:
                    fig_events.add_trace(go.Scatter(
                        x=stockout_data['Дата'],
                        y=stockout_data['Остаток'],
                        mode='markers',
                        name='Дефициты',
                        marker=dict(color='red', size=6, symbol='x')
                    ))
                
                fig_events.update_layout(
                    title='События в управлении запасами',
                    xaxis_title='Дата',
                    yaxis_title='Остатки',
                    height=500
                )
                charts["supply_events"] = fig_events
            
            # 5. Распределение уровней остатков
            stock_distribution = self.data['Остаток_категория'].value_counts()
            
            fig_distribution = px.pie(
                values=stock_distribution.values,
                names=stock_distribution.index,
                title='Распределение дней по уровню остатков'
            )
            fig_distribution.update_layout(height=400)
            charts["stock_level_distribution"] = fig_distribution
            
        except Exception as e:
            st.error(f"Ошибка при создании графиков остатков: {e}")
        
        return charts
    
    def _get_month_name(self, month_number: int) -> str:
        """Получение названия месяца по номеру"""
        months = {
            1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
            5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
            9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
        }
        return months.get(month_number, f"Месяц {month_number}")
    
    def _generate_seasonal_recommendations(self, analysis: Dict) -> List[str]:
        """Генерация рекомендаций по сезонности"""
        recommendations = []
        
        try:
            # Анализ пиковых месяцев
            if analysis["peak_stock_months"]:
                peak_months = list(analysis["peak_stock_months"].values())
                if len(peak_months) >= 2:
                    # Находим наиболее частый пиковый месяц
                    peak_month_counts = {}
                    for peak in peak_months:
                        month = peak["month_name"]
                        peak_month_counts[month] = peak_month_counts.get(month, 0) + 1
                    
                    most_common_peak = max(peak_month_counts.items(), key=lambda x: x[1])
                    recommendations.append(f"📈 Стабильный пик остатков в {most_common_peak[0]}")
            
            # Сезонные инсайты
            seasonal_insights = analysis.get("seasonal_insights", {})
            if "volatility_analysis" in seasonal_insights:
                vol_analysis = seasonal_insights["volatility_analysis"]
                recommendations.append(f"📊 Самый нестабильный сезон: {vol_analysis['most_volatile_season']}")
                recommendations.append(f"✅ Самый стабильный сезон: {vol_analysis['least_volatile_season']}")
            
            if "stock_level_analysis" in seasonal_insights:
                stock_analysis = seasonal_insights["stock_level_analysis"]
                recommendations.append(f"🔺 Максимальные остатки: {stock_analysis['highest_stock_season']}")
                recommendations.append(f"🔻 Минимальные остатки: {stock_analysis['lowest_stock_season']}")
                
                # Рекомендации по планированию
                high_season = stock_analysis['highest_stock_season']
                low_season = stock_analysis['lowest_stock_season']
                recommendations.append(f"📦 Планировать завоз товаров перед {low_season.lower()}")
        
        except Exception as e:
            recommendations.append(f"Ошибка в сезонном анализе: {e}")
        
        return recommendations
    
    def _generate_supply_chain_recommendations(self, analysis: Dict) -> List[str]:
        """Генерация рекомендаций по цепочке поставок"""
        recommendations = []
        
        try:
            stockout_analysis = analysis.get("stockout_analysis", {})
            if "stockout_percentage" in stockout_analysis:
                stockout_pct = stockout_analysis["stockout_percentage"]
                
                if stockout_pct == 0:
                    recommendations.append("✅ Отличное управление запасами - дефицитов нет")
                elif stockout_pct < 5:
                    recommendations.append("🟢 Хорошее управление запасами")
                elif stockout_pct < 15:
                    recommendations.append("🟡 Есть проблемы с дефицитами - требует внимания")
                else:
                    recommendations.append("🔴 Серьезные проблемы с дефицитами")
            
            restocking_patterns = analysis.get("restocking_patterns", {})
            if "total_restocking_events" in restocking_patterns:
                events_count = restocking_patterns["total_restocking_events"]
                if events_count > 50:
                    recommendations.append("📦 Частые пополнения - возможно стоит оптимизировать логистику")
                elif events_count < 10:
                    recommendations.append("📦 Редкие пополнения - крупные партии поставок")
            
            inventory_turnover = analysis.get("inventory_turnover", {})
            if "turnover_times_per_year" in inventory_turnover:
                turnover = inventory_turnover["turnover_times_per_year"]
                if turnover > 12:
                    recommendations.append("🔄 Высокая оборачиваемость - эффективное управление запасами")
                elif turnover < 4:
                    recommendations.append("⚠️ Низкая оборачиваемость - много замороженных запасов")
        
        except Exception as e:
            recommendations.append(f"Ошибка в анализе поставок: {e}")
        
        return recommendations
    
    def _generate_forecasting_recommendations(self, forecast: Dict) -> List[str]:
        """Генерация рекомендаций по прогнозированию"""
        recommendations = []
        
        try:
            trend_analysis = forecast.get("trend_analysis", {})
            if "trend_direction" in trend_analysis:
                trend = trend_analysis["trend_direction"]
                strength = trend_analysis.get("trend_strength", 0)
                
                if trend == "Растущий" and strength > 0.5:
                    recommendations.append("📈 Сильный растущий тренд - планируйте увеличение поставок")
                elif trend == "Падающий" and strength > 0.5:
                    recommendations.append("📉 Сильный падающий тренд - возможно сокращение спроса")
                else:
                    recommendations.append("📊 Стабильная динамика остатков")
            
            seasonal_forecast = forecast.get("seasonal_forecast", {})
            if seasonal_forecast:
                next_month = list(seasonal_forecast.keys())[0]
                next_stock = seasonal_forecast[next_month]["predicted_avg_stock"]
                recommendations.append(f"🔮 Прогноз на {next_month}: {next_stock} единиц в среднем")
        
        except Exception as e:
            recommendations.append(f"Ошибка в прогнозировании: {e}")
        
        return recommendations
    
    def get_summary_metrics(self) -> Dict:
        """Получение сводных метрик для дашборда"""
        try:
            summary = {
                "total_days": len(self.data),
                "avg_stock": round(self.data['Остаток'].mean(), 0),
                "max_stock": self.data['Остаток'].max(),
                "min_stock": self.data['Остаток'].min(),
                "stockout_days": len(self.data[self.data['Остаток'] == 0]),
                "stockout_percentage": round((len(self.data[self.data['Остаток'] == 0]) / len(self.data)) * 100, 2),
                "stock_volatility": round(self.data['Остаток'].std(), 0),
                "period_start": self.data['Дата'].min().strftime('%Y-%m-%d'),
                "period_end": self.data['Дата'].max().strftime('%Y-%m-%d')
            }
            
            # Добавляем оборачиваемость если есть данные о продажах
            if 'Продажи, шт.' in self.data.columns:
                total_sales = self.data['Продажи, шт.'].sum()
                if total_sales > 0 and summary["avg_stock"] > 0:
                    days_in_period = (self.data['Дата'].max() - self.data['Дата'].min()).days + 1
                    turnover_days = (summary["avg_stock"] * days_in_period) / total_sales
                    summary["turnover_days"] = round(turnover_days, 1)
                else:
                    summary["turnover_days"] = "N/A"
            
            return summary
            
        except Exception as e:
            return {"error": str(e)}
