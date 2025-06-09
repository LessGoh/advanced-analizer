import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple, Optional
import streamlit as st


class PriceAnalyzer:
    """Анализатор ценовой сегментации"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        self.prepare_data()
        
    def prepare_data(self):
        """Подготовка данных для анализа"""
        # Убираем строки с пустыми ценовыми диапазонами
        self.data = self.data.dropna(subset=['От', 'До'])
        
        # Добавляем вычисляемые поля
        self.data['Ценовой_диапазон'] = self.data['От'].astype(str) + ' - ' + self.data['До'].astype(str) + ' ₽'
        self.data['Средняя_цена'] = (self.data['От'] + self.data['До']) / 2
        self.data['Ширина_диапазона'] = self.data['До'] - self.data['От']
        
        # Эффективность сегмента (выручка на товар с учетом конкуренции)
        if all(col in self.data.columns for col in ['Выручка на товар, ₽', 'Продавцы']):
            # Чем выше выручка на товар и меньше продавцов, тем лучше
            max_revenue = self.data['Выручка на товар, ₽'].max()
            min_sellers = self.data['Продавцы'].min() if self.data['Продавцы'].min() > 0 else 1
            
            self.data['Эффективность_сегмента'] = (
                (self.data['Выручка на товар, ₽'] / max_revenue) * 0.7 +
                (min_sellers / self.data['Продавцы'].replace(0, min_sellers)) * 0.3
            ) * 100
        else:
            self.data['Эффективность_сегмента'] = 0
        
        # Категоризация по привлекательности
        self.data['Категория_привлекательности'] = self.data['Эффективность_сегмента'].apply(self._categorize_attractiveness)
    
    def _categorize_attractiveness(self, efficiency: float) -> str:
        """Категоризация привлекательности сегмента"""
        if efficiency >= 80:
            return "Очень привлекательный"
        elif efficiency >= 60:
            return "Привлекательный"
        elif efficiency >= 40:
            return "Средний"
        else:
            return "Низкая привлекательность"
    
    def get_segment_analysis(self) -> Dict:
        """Анализ ценовых сегментов"""
        analysis = {
            "best_segment": {},
            "segment_comparison": [],
            "price_distribution": {},
            "recommendations": []
        }
        
        try:
            # Определяем лучший сегмент по выручке на товар
            if 'Выручка на товар, ₽' in self.data.columns:
                best_idx = self.data['Выручка на товар, ₽'].idxmax()
                best_segment = self.data.loc[best_idx]
                
                analysis["best_segment"] = {
                    "price_range": best_segment['Ценовой_диапазон'],
                    "revenue_per_product": round(best_segment['Выручка на товар, ₽'], 2),
                    "avg_price": round(best_segment['Средняя_цена'], 2),
                    "products": int(best_segment.get('Товары', 0)),
                    "products_with_sales": int(best_segment.get('Товары с продажами', 0)),
                    "sellers": int(best_segment.get('Продавцы', 0)),
                    "brands": int(best_segment.get('Бренды', 0)),
                    "total_revenue": round(best_segment.get('Выручка, ₽', 0), 2),
                    "efficiency_score": round(best_segment['Эффективность_сегмента'], 2)
                }
            
            # Сравнение всех сегментов
            for idx, row in self.data.iterrows():
                segment_data = {
                    "price_range": row['Ценовой_диапазон'],
                    "avg_price": round(row['Средняя_цена'], 2),
                    "revenue_per_product": round(row.get('Выручка на товар, ₽', 0), 2),
                    "total_revenue": round(row.get('Выручка, ₽', 0), 2),
                    "products": int(row.get('Товары', 0)),
                    "products_with_sales": int(row.get('Товары с продажами', 0)),
                    "sellers": int(row.get('Продавцы', 0)),
                    "conversion_rate": round((row.get('Товары с продажами', 0) / max(row.get('Товары', 1), 1)) * 100, 2),
                    "efficiency_score": round(row['Эффективность_сегмента'], 2),
                    "category": row['Категория_привлекательности']
                }
                analysis["segment_comparison"].append(segment_data)
            
            # Распределение по ценам
            total_products = self.data['Товары'].sum() if 'Товары' in self.data.columns else 0
            total_revenue = self.data['Выручка, ₽'].sum() if 'Выручка, ₽' in self.data.columns else 0
            
            analysis["price_distribution"] = {
                "total_segments": len(self.data),
                "price_range_min": self.data['От'].min(),
                "price_range_max": self.data['До'].max(),
                "avg_segment_price": round(self.data['Средняя_цена'].mean(), 2),
                "total_products": int(total_products),
                "total_revenue": round(total_revenue, 2),
                "segments_by_attractiveness": self.data['Категория_привлекательности'].value_counts().to_dict()
            }
            
            # Генерация рекомендаций
            analysis["recommendations"] = self._generate_segment_recommendations(analysis)
            
        except Exception as e:
            analysis["error"] = str(e)
        
        return analysis
    
    def get_competition_analysis(self) -> Dict:
        """Анализ конкуренции по сегментам"""
        analysis = {
            "competition_overview": {},
            "low_competition_segments": [],
            "market_gaps": [],
            "recommendations": []
        }
        
        try:
            if all(col in self.data.columns for col in ['Продавцы', 'Товары', 'Выручка на товар, ₽']):
                # Общий обзор конкуренции
                analysis["competition_overview"] = {
                    "avg_sellers_per_segment": round(self.data['Продавцы'].mean(), 1),
                    "avg_products_per_segment": round(self.data['Товары'].mean(), 1),
                    "segments_with_low_competition": len(self.data[self.data['Продавцы'] <= self.data['Продавцы'].quantile(0.3)]),
                    "segments_with_high_revenue": len(self.data[self.data['Выручка на товар, ₽'] >= self.data['Выручка на товар, ₽'].quantile(0.7)])
                }
                
                # Сегменты с низкой конкуренцией
                low_competition = self.data[
                    self.data['Продавцы'] <= self.data['Продавцы'].quantile(0.4)
                ].nlargest(5, 'Выручка на товар, ₽')
                
                for idx, row in low_competition.iterrows():
                    analysis["low_competition_segments"].append({
                        "price_range": row['Ценовой_диапазон'],
                        "sellers": int(row['Продавцы']),
                        "products": int(row['Товары']),
                        "revenue_per_product": round(row['Выручка на товар, ₽'], 2),
                        "competition_level": "Низкая" if row['Продавцы'] <= 10 else "Средняя"
                    })
                
                # Рыночные пробелы (высокая выручка на товар + низкая конкуренция)
                market_gaps = self.data[
                    (self.data['Продавцы'] <= self.data['Продавцы'].median()) &
                    (self.data['Выручка на товар, ₽'] >= self.data['Выручка на товар, ₽'].quantile(0.6))
                ]
                
                for idx, row in market_gaps.iterrows():
                    gap_opportunity = {
                        "price_range": row['Ценовой_диапазон'],
                        "revenue_per_product": round(row['Выручка на товар, ₽'], 2),
                        "sellers": int(row['Продавцы']),
                        "products": int(row['Товары']),
                        "opportunity_score": round(row['Эффективность_сегмента'], 2)
                    }
                    analysis["market_gaps"].append(gap_opportunity)
                
                analysis["recommendations"] = self._generate_competition_recommendations(analysis)
            
        except Exception as e:
            analysis["error"] = str(e)
        
        return analysis
    
    def get_pricing_strategy(self) -> Dict:
        """Рекомендации по ценовой стратегии"""
        strategy = {
            "optimal_price_ranges": [],
            "pricing_insights": {},
            "strategy_recommendations": [],
            "risk_assessment": {}
        }
        
        try:
            # Оптимальные ценовые диапазоны (топ-3 по эффективности)
            top_segments = self.data.nlargest(3, 'Эффективность_сегмента')
            
            for idx, row in top_segments.iterrows():
                strategy["optimal_price_ranges"].append({
                    "price_range": row['Ценовой_диапазон'],
                    "min_price": row['От'],
                    "max_price": row['До'],
                    "avg_price": round(row['Средняя_цена'], 2),
                    "revenue_per_product": round(row['Выручка на товар, ₽'], 2),
                    "competition_level": "Низкая" if row['Продавцы'] <= self.data['Продавцы'].quantile(0.3) else 
                                       "Средняя" if row['Продавцы'] <= self.data['Продавцы'].quantile(0.7) else "Высокая",
                    "efficiency_score": round(row['Эффективность_сегмента'], 2)
                })
            
            # Ценовые инсайты
            if 'Выручка на товар, ₽' in self.data.columns:
                price_revenue_corr = self.data['Средняя_цена'].corr(self.data['Выручка на товар, ₽'])
                
                strategy["pricing_insights"] = {
                    "price_revenue_correlation": round(price_revenue_corr, 3),
                    "sweet_spot_analysis": self._find_price_sweet_spots(),
                    "premium_viability": self._assess_premium_segment(),
                    "budget_viability": self._assess_budget_segment()
                }
            
            # Стратегические рекомендации
            strategy["strategy_recommendations"] = self._generate_pricing_strategy_recommendations(strategy)
            
            # Оценка рисков
            strategy["risk_assessment"] = self._assess_pricing_risks()
            
        except Exception as e:
            strategy["error"] = str(e)
        
        return strategy
    
    def _find_price_sweet_spots(self) -> Dict:
        """Поиск ценовых sweet spots"""
        try:
            # Sweet spot = высокая выручка на товар при умеренной конкуренции
            sweet_spots = self.data[
                (self.data['Выручка на товар, ₽'] >= self.data['Выручка на товар, ₽'].quantile(0.7)) &
                (self.data['Продавцы'] <= self.data['Продавцы'].quantile(0.6))
            ]
            
            if len(sweet_spots) > 0:
                return {
                    "found": True,
                    "count": len(sweet_spots),
                    "price_range_min": sweet_spots['От'].min(),
                    "price_range_max": sweet_spots['До'].max(),
                    "avg_revenue_per_product": round(sweet_spots['Выручка на товар, ₽'].mean(), 2)
                }
            else:
                return {"found": False}
                
        except Exception:
            return {"found": False, "error": "Ошибка в расчете"}
    
    def _assess_premium_segment(self) -> Dict:
        """Оценка премиум сегмента"""
        try:
            premium_threshold = self.data['Средняя_цена'].quantile(0.8)
            premium_segments = self.data[self.data['Средняя_цена'] >= premium_threshold]
            
            if len(premium_segments) > 0:
                return {
                    "viable": True,
                    "avg_revenue_per_product": round(premium_segments['Выручка на товар, ₽'].mean(), 2),
                    "avg_competition": round(premium_segments['Продавцы'].mean(), 1),
                    "segments_count": len(premium_segments)
                }
            else:
                return {"viable": False}
                
        except Exception:
            return {"viable": False, "error": "Ошибка в анализе премиум сегмента"}
    
    def _assess_budget_segment(self) -> Dict:
        """Оценка бюджетного сегмента"""
        try:
            budget_threshold = self.data['Средняя_цена'].quantile(0.3)
            budget_segments = self.data[self.data['Средняя_цена'] <= budget_threshold]
            
            if len(budget_segments) > 0:
                return {
                    "viable": True,
                    "avg_revenue_per_product": round(budget_segments['Выручка на товар, ₽'].mean(), 2),
                    "avg_competition": round(budget_segments['Продавцы'].mean(), 1),
                    "segments_count": len(budget_segments)
                }
            else:
                return {"viable": False}
                
        except Exception:
            return {"viable": False, "error": "Ошибка в анализе бюджетного сегмента"}
    
    def _assess_pricing_risks(self) -> Dict:
        """Оценка ценовых рисков"""
        risks = {
            "competition_risk": "Низкий",
            "saturation_risk": "Низкий", 
            "price_war_risk": "Низкий"
        }
        
        try:
            # Риск конкуренции
            avg_sellers = self.data['Продавцы'].mean()
            if avg_sellers > 50:
                risks["competition_risk"] = "Высокий"
            elif avg_sellers > 20:
                risks["competition_risk"] = "Средний"
            
            # Риск насыщения
            conversion_rates = self.data['Товары с продажами'] / self.data['Товары']
            avg_conversion = conversion_rates.mean()
            if avg_conversion < 0.3:
                risks["saturation_risk"] = "Высокий"
            elif avg_conversion < 0.5:
                risks["saturation_risk"] = "Средний"
            
            # Риск ценовой войны (много сегментов с низкой выручкой на товар)
            low_revenue_segments = len(self.data[self.data['Выручка на товар, ₽'] < self.data['Выручка на товар, ₽'].median()])
            if low_revenue_segments > len(self.data) * 0.7:
                risks["price_war_risk"] = "Высокий"
            elif low_revenue_segments > len(self.data) * 0.5:
                risks["price_war_risk"] = "Средний"
                
        except Exception:
            pass
        
        return risks
    
    def create_price_charts(self) -> Dict[str, go.Figure]:
        """Создание графиков ценового анализа"""
        charts = {}
        
        try:
            # 1. График выручки на товар по сегментам
            fig_revenue = px.bar(
                self.data,
                x='Ценовой_диапазон',
                y='Выручка на товар, ₽',
                title='Выручка на товар по ценовым сегментам',
                labels={'Выручка на товар, ₽': 'Выручка на товар (₽)', 'Ценовой_диапазон': 'Ценовой диапазон'},
                color='Эффективность_сегмента',
                color_continuous_scale='RdYlGn'
            )
            fig_revenue.update_xaxes(tickangle=45)
            fig_revenue.update_layout(height=500)
            charts["revenue_by_segment"] = fig_revenue
            
            # 2. Scatter plot: Цена vs Конкуренция vs Выручка
            fig_scatter = px.scatter(
                self.data,
                x='Средняя_цена',
                y='Продавцы',
                size='Выручка на товар, ₽',
                color='Эффективность_сегмента',
                hover_data=['Ценовой_диапазон', 'Товары'],
                title='Соотношение цены, конкуренции и выручки',
                labels={
                    'Средняя_цена': 'Средняя цена (₽)',
                    'Продавцы': 'Количество продавцов',
                    'Эффективность_сегмента': 'Эффективность'
                },
                color_continuous_scale='RdYlGn'
            )
            fig_scatter.update_layout(height=500)
            charts["price_competition_scatter"] = fig_scatter
            
            # 3. Анализ привлекательности сегментов
            attractiveness_counts = self.data['Категория_привлекательности'].value_counts()
            fig_attractiveness = px.pie(
                values=attractiveness_counts.values,
                names=attractiveness_counts.index,
                title='Распределение сегментов по привлекательности'
            )
            fig_attractiveness.update_layout(height=400)
            charts["segment_attractiveness"] = fig_attractiveness
            
            # 4. Сравнение метрик по сегментам
            fig_comparison = make_subplots(
                rows=2, cols=2,
                subplot_titles=['Выручка на товар', 'Количество продавцов', 'Количество товаров', 'Общая выручка'],
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # Выручка на товар
            fig_comparison.add_trace(
                go.Bar(x=self.data['Ценовой_диапазон'], y=self.data['Выручка на товар, ₽'], 
                      name='Выручка на товар'),
                row=1, col=1
            )
            
            # Продавцы
            fig_comparison.add_trace(
                go.Bar(x=self.data['Ценовой_диапазон'], y=self.data['Продавцы'], 
                      name='Продавцы'),
                row=1, col=2
            )
            
            # Товары
            fig_comparison.add_trace(
                go.Bar(x=self.data['Ценовой_диапазон'], y=self.data['Товары'], 
                      name='Товары'),
                row=2, col=1
            )
            
            # Общая выручка
            if 'Выручка, ₽' in self.data.columns:
                fig_comparison.add_trace(
                    go.Bar(x=self.data['Ценовой_диапазон'], y=self.data['Выручка, ₽'], 
                          name='Общая выручка'),
                    row=2, col=2
                )
            
            fig_comparison.update_xaxes(tickangle=45)
            fig_comparison.update_layout(height=600, title_text="Сравнение метрик по ценовым сегментам")
            charts["metrics_comparison"] = fig_comparison
            
            # 5. Heatmap эффективности
            # Создаем матрицу: цена vs количество продавцов
            price_bins = pd.cut(self.data['Средняя_цена'], bins=5, labels=['Очень низкая', 'Низкая', 'Средняя', 'Высокая', 'Очень высокая'])
            seller_bins = pd.cut(self.data['Продавцы'], bins=5, labels=['Очень мало', 'Мало', 'Средне', 'Много', 'Очень много'])
            
            heatmap_data = pd.crosstab(price_bins, seller_bins, values=self.data['Выручка на товар, ₽'], aggfunc='mean')
            
            fig_heatmap = px.imshow(
                heatmap_data,
                title='Тепловая карта: выручка на товар по цене и конкуренции',
                labels={'x': 'Уровень конкуренции', 'y': 'Ценовой уровень', 'color': 'Выручка на товар'},
                color_continuous_scale='RdYlGn'
            )
            fig_heatmap.update_layout(height=400)
            charts["efficiency_heatmap"] = fig_heatmap
            
        except Exception as e:
            st.error(f"Ошибка при создании графиков ценового анализа: {e}")
        
        return charts
    
    def _generate_segment_recommendations(self, analysis: Dict) -> List[str]:
        """Генерация рекомендаций по сегментам"""
        recommendations = []
        
        try:
            if "best_segment" in analysis and analysis["best_segment"]:
                best = analysis["best_segment"]
                recommendations.append(f"🎯 Лучший сегмент: {best['price_range']} с выручкой {best['revenue_per_product']} ₽ на товар")
                
                if best["sellers"] < 20:
                    recommendations.append("🟢 В лучшем сегменте низкая конкуренция")
                elif best["sellers"] > 50:
                    recommendations.append("🟡 В лучшем сегменте высокая конкуренция")
            
            # Анализ распределения привлекательности
            if "price_distribution" in analysis:
                attractive_count = analysis["price_distribution"]["segments_by_attractiveness"].get("Очень привлекательный", 0) + \
                                analysis["price_distribution"]["segments_by_attractiveness"].get("Привлекательный", 0)
                total_segments = analysis["price_distribution"]["total_segments"]
                
                if attractive_count >= total_segments * 0.4:
                    recommendations.append("🚀 Много привлекательных ценовых сегментов")
                elif attractive_count >= total_segments * 0.2:
                    recommendations.append("🟡 Есть привлекательные ценовые сегменты")
                else:
                    recommendations.append("🔴 Мало привлекательных ценовых сегментов")
        
        except Exception as e:
            recommendations.append(f"Ошибка в анализе сегментов: {e}")
        
        return recommendations
    
    def _generate_competition_recommendations(self, analysis: Dict) -> List[str]:
        """Генерация рекомендаций по конкуренции"""
        recommendations = []
        
        try:
            if "competition_overview" in analysis:
                overview = analysis["competition_overview"]
                avg_sellers = overview["avg_sellers_per_segment"]
                
                if avg_sellers < 15:
                    recommendations.append("🟢 Низкая средняя конкуренция - хорошие возможности")
                elif avg_sellers < 30:
                    recommendations.append("🟡 Умеренная конкуренция")
                else:
                    recommendations.append("🔴 Высокая конкуренция в большинстве сегментов")
                
                low_comp_count = overview["segments_with_low_competition"]
                if low_comp_count > 3:
                    recommendations.append(f"🎯 Найдено {low_comp_count} сегментов с низкой конкуренцией")
            
            gaps_count = len(analysis.get("market_gaps", []))
            if gaps_count > 2:
                recommendations.append(f"💎 Обнаружено {gaps_count} рыночных пробелов")
        
        except Exception as e:
            recommendations.append(f"Ошибка в анализе конкуренции: {e}")
        
        return recommendations
    
    def _generate_pricing_strategy_recommendations(self, strategy: Dict) -> List[str]:
        """Генерация стратегических рекомендаций"""
        recommendations = []
        
        try:
            optimal_ranges = strategy.get("optimal_price_ranges", [])
            if optimal_ranges:
                top_range = optimal_ranges[0]
                recommendations.append(f"💰 Рекомендуемый ценовой диапазон: {top_range['price_range']}")
                
                if top_range["competition_level"] == "Низкая":
                    recommendations.append("🎯 Возможно премиальное позиционирование")
                elif top_range["competition_level"] == "Высокая":
                    recommendations.append("⚡ Требуется четкое конкурентное преимущество")
            
            insights = strategy.get("pricing_insights", {})
            if "price_revenue_correlation" in insights:
                corr = insights["price_revenue_correlation"]
                if corr > 0.5:
                    recommendations.append("📈 Положительная корреляция цены и выручки - премиум стратегия возможна")
                elif corr < -0.3:
                    recommendations.append("📉 Обратная корреляция - фокус на объемы и низкие цены")
            
            sweet_spots = insights.get("sweet_spot_analysis", {})
            if sweet_spots.get("found"):
                recommendations.append(f"🎯 Найден ценовой sweet spot: {sweet_spots['price_range_min']}-{sweet_spots['price_range_max']} ₽")
        
        except Exception as e:
            recommendations.append(f"Ошибка в стратегических рекомендациях: {e}")
        
        return recommendations
    
    def get_summary_metrics(self) -> Dict:
        """Получение сводных метрик для дашборда"""
        try:
            summary = {
                "total_segments": len(self.data),
                "price_range_min": self.data['От'].min(),
                "price_range_max": self.data['До'].max(),
                "best_revenue_per_product": round(self.data['Выручка на товар, ₽'].max(), 2),
                "avg_competition": round(self.data['Продавцы'].mean(), 1),
                "attractive_segments": len(self.data[self.data['Эффективность_сегмента'] >= 60]),
                "total_revenue": round(self.data['Выручка, ₽'].sum(), 2) if 'Выручка, ₽' in self.data.columns else 0,
                "avg_segment_efficiency": round(self.data['Эффективность_сегмента'].mean(), 2)
            }
            
            return summary
            
        except Exception as e:
            return {"error": str(e)}
