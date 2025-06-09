import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple, Optional
import streamlit as st
from config import ADS_THRESHOLDS


class AdsAnalyzer:
    """Анализатор рекламных данных с учетом коэффициента Чек/Ставка"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        self.prepare_data()
        
    def prepare_data(self):
        """Подготовка данных для анализа"""
        # Убираем товары без позиций в категории
        self.data = self.data.dropna(subset=['Category position avg'])
        
        # Заполняем пустые значения в рекламных полях
        ads_columns = ['Search cpm avg', 'Search words in ads', 'Search organic position avg']
        for col in ads_columns:
            if col in self.data.columns:
                self.data[col] = self.data[col].fillna(0)
        
        # Определяем сегменты товаров
        self.data['Position_segment'] = self.data['Category position avg'].apply(self._categorize_position)
        
        # Рассчитываем коэффициент Чек/Ставка
        if all(col in self.data.columns for col in ['Final price', 'Search cpm avg']):
            self.data['Price_to_CPM_ratio'] = np.where(
                self.data['Search cmp avg'] > 0,
                self.data['Final price'] / self.data['Search cmp avg'],
                0
            )
        else:
            self.data['Price_to_CPM_ratio'] = 0
        
        # Определяем использование рекламы
        self.data['Uses_ads'] = self.data['Search words in ads'] > 0
        self.data['Organic_only'] = (self.data['Search words in ads'] == 0) & (self.data['Search organic position avg'] > 0)
        
        # Категоризация эффективности рекламы
        self.data['Ad_efficiency_category'] = self.data['Price_to_CPM_ratio'].apply(self._categorize_ad_efficiency)
    
    def _categorize_position(self, position: float) -> str:
        """Категоризация позиции товара"""
        if pd.isna(position):
            return "Неизвестно"
        elif position <= 10:
            return "ТОП-10"
        elif position <= 100:
            return "ТОП-100"
        else:
            return "Вне ТОП-100"
    
    def _categorize_ad_efficiency(self, ratio: float) -> str:
        """Категоризация эффективности рекламы по коэффициенту Чек/Ставка"""
        if ratio >= ADS_THRESHOLDS["excellent"]:
            return "Очень эффективно"
        elif ratio >= ADS_THRESHOLDS["good"]:
            return "Эффективно"
        elif ratio >= ADS_THRESHOLDS["average"]:
            return "Средне"
        elif ratio >= ADS_THRESHOLDS["poor"]:
            return "Неэффективно"
        else:
            return "Очень неэффективно"
    
    def get_top_segments_analysis(self) -> Dict:
        """Анализ ТОП-10 и ТОП-100 сегментов согласно вашим требованиям"""
        analysis = {
            "top_10_analysis": {},
            "top_100_analysis": {},
            "comparison": {},
            "recommendations": []
        }
        
        try:
            # Фильтруем ТОП сегменты
            top_10 = self.data[self.data['Category position avg'] <= 10]
            top_100 = self.data[self.data['Category position avg'] <= 100]
            
            if len(top_10) == 0:
                analysis["error"] = "Нет товаров в ТОП-10"
                return analysis
            
            if len(top_100) == 0:
                analysis["error"] = "Нет товаров в ТОП-100"
                return analysis
            
            # Анализ ТОП-10
            analysis["top_10_analysis"] = {
                "products_count": len(top_10),
                "avg_cpm": round(top_10['Search cpm avg'].mean(), 2),
                "median_cpm": round(top_10['Search cpm avg'].median(), 2),
                "avg_price": round(top_10['Final price'].mean(), 2),
                "median_price": round(top_10['Final price'].median(), 2),
                "avg_ratio": round(top_10['Price_to_CPM_ratio'].mean(), 2),
                "median_ratio": round(top_10['Price_to_CPM_ratio'].median(), 2),
                "products_with_ads": len(top_10[top_10['Uses_ads'] == True]),
                "organic_products": len(top_10[top_10['Organic_only'] == True]),
                "ads_percentage": round((len(top_10[top_10['Uses_ads'] == True]) / len(top_10)) * 100, 2)
            }
            
            # Анализ ТОП-100
            analysis["top_100_analysis"] = {
                "products_count": len(top_100),
                "avg_cpm": round(top_100['Search cpm avg'].mean(), 2),
                "median_cpm": round(top_100['Search cpm avg'].median(), 2),
                "avg_price": round(top_100['Final price'].mean(), 2),
                "median_price": round(top_100['Final price'].median(), 2),
                "avg_ratio": round(top_100['Price_to_CPM_ratio'].mean(), 2),
                "median_ratio": round(top_100['Price_to_CPM_ratio'].median(), 2),
                "products_with_ads": len(top_100[top_100['Uses_ads'] == True]),
                "organic_products": len(top_100[top_100['Organic_only'] == True]),
                "ads_percentage": round((len(top_100[top_100['Uses_ads'] == True]) / len(top_100)) * 100, 2)
            }
            
            # Сравнительный анализ
            analysis["comparison"] = {
                "cpm_difference": round(analysis["top_10_analysis"]["avg_cpm"] - analysis["top_100_analysis"]["avg_cpm"], 2),
                "price_difference": round(analysis["top_10_analysis"]["avg_price"] - analysis["top_100_analysis"]["avg_price"], 2),
                "ratio_difference": round(analysis["top_10_analysis"]["avg_ratio"] - analysis["top_100_analysis"]["avg_ratio"], 2),
                "ads_usage_difference": round(analysis["top_10_analysis"]["ads_percentage"] - analysis["top_100_analysis"]["ads_percentage"], 2)
            }
            
            # Оценка перегрева ниши
            analysis["niche_assessment"] = self._assess_niche_heat(analysis)
            
            analysis["recommendations"] = self._generate_top_segments_recommendations(analysis)
            
        except Exception as e:
            analysis["error"] = str(e)
        
        return analysis
    
    def _assess_niche_heat(self, analysis: Dict) -> Dict:
        """Оценка перегрева ниши на основе коэффициента Чек/Ставка"""
        assessment = {
            "niche_status": "Нормальная",
            "heat_level": 1,  # 1-5 шкала
            "reasoning": []
        }
        
        try:
            top_10_ratio = analysis["top_10_analysis"]["avg_ratio"]
            top_100_ratio = analysis["top_100_analysis"]["avg_ratio"]
            
            # Используем худший коэффициент (как в scoring_engine)
            worst_ratio = min(top_10_ratio, top_100_ratio)
            
            if worst_ratio >= 4.0:
                assessment["niche_status"] = "Очень выгодная"
                assessment["heat_level"] = 1
                assessment["reasoning"].append("Высокий коэффициент Чек/Ставка - низкая конкуренция")
            elif worst_ratio >= 3.0:
                assessment["niche_status"] = "Хорошая"
                assessment["heat_level"] = 2
                assessment["reasoning"].append("Хороший коэффициент Чек/Ставка - умеренная конкуренция")
            elif worst_ratio >= 2.0:
                assessment["niche_status"] = "Средняя конкуренция"
                assessment["heat_level"] = 3
                assessment["reasoning"].append("Средний коэффициент Чек/Ставка")
            elif worst_ratio >= 1.0:
                assessment["niche_status"] = "Высокая конкуренция"
                assessment["heat_level"] = 4
                assessment["reasoning"].append("Низкий коэффициент Чек/Ставка - дорогая реклама")
            else:
                assessment["niche_status"] = "Перегретая ниша"
                assessment["heat_level"] = 5
                assessment["reasoning"].append("Очень низкий коэффициент Чек/Ставка - реклама дороже товара")
            
            # Дополнительные факторы
            top_10_ads_pct = analysis["top_10_analysis"]["ads_percentage"]
            top_100_ads_pct = analysis["top_100_analysis"]["ads_percentage"]
            
            if top_10_ads_pct > 90:
                assessment["reasoning"].append("Почти все товары в ТОП-10 используют рекламу")
                assessment["heat_level"] = min(assessment["heat_level"] + 1, 5)
            
            if top_100_ads_pct > 80:
                assessment["reasoning"].append("Высокий процент рекламных товаров в ТОП-100")
            
            if analysis["comparison"]["cpm_difference"] > 100:
                assessment["reasoning"].append("Значительная разница в ставках между ТОП-10 и ТОП-100")
            
        except Exception as e:
            assessment["reasoning"].append(f"Ошибка в оценке: {e}")
        
        return assessment
    
    def get_organic_analysis(self) -> Dict:
        """Анализ органических позиций"""
        analysis = {
            "organic_overview": {},
            "organic_opportunities": [],
            "organic_vs_paid": {},
            "recommendations": []
        }
        
        try:
            # Общий обзор органики
            total_products = len(self.data)
            organic_products = len(self.data[self.data['Organic_only'] == True])
            products_with_ads = len(self.data[self.data['Uses_ads'] == True])
            
            analysis["organic_overview"] = {
                "total_products": total_products,
                "organic_products": organic_products,
                "paid_products": products_with_ads,
                "organic_percentage": round((organic_products / total_products) * 100, 2),
                "paid_percentage": round((products_with_ads / total_products) * 100, 2),
                "avg_organic_position": round(self.data[self.data['Search organic position avg'] > 0]['Search organic position avg'].mean(), 1)
            }
            
            # Органические возможности в ТОП сегментах
            top_10_organic = self.data[(self.data['Category position avg'] <= 10) & (self.data['Organic_only'] == True)]
            top_100_organic = self.data[(self.data['Category position avg'] <= 100) & (self.data['Organic_only'] == True)]
            
            if not top_10_organic.empty:
                analysis["organic_opportunities"].append({
                    "segment": "ТОП-10",
                    "organic_count": len(top_10_organic),
                    "avg_revenue": round(top_10_organic['Revenue'].mean(), 2) if 'Revenue' in top_10_organic.columns else 0,
                    "avg_sales": round(top_10_organic['Sales'].mean(), 1) if 'Sales' in top_10_organic.columns else 0
                })
            
            if not top_100_organic.empty:
                analysis["organic_opportunities"].append({
                    "segment": "ТОП-100",
                    "organic_count": len(top_100_organic),
                    "avg_revenue": round(top_100_organic['Revenue'].mean(), 2) if 'Revenue' in top_100_organic.columns else 0,
                    "avg_sales": round(top_100_organic['Sales'].mean(), 1) if 'Sales' in top_100_organic.columns else 0
                })
            
            # Сравнение органики и рекламы
            if 'Revenue' in self.data.columns:
                organic_revenue = self.data[self.data['Organic_only'] == True]['Revenue'].mean()
                paid_revenue = self.data[self.data['Uses_ads'] == True]['Revenue'].mean()
                
                analysis["organic_vs_paid"] = {
                    "organic_avg_revenue": round(organic_revenue, 2) if not pd.isna(organic_revenue) else 0,
                    "paid_avg_revenue": round(paid_revenue, 2) if not pd.isna(paid_revenue) else 0,
                    "organic_advantage": round(((organic_revenue - paid_revenue) / paid_revenue) * 100, 2) if paid_revenue > 0 and not pd.isna(organic_revenue) else 0
                }
            
            analysis["recommendations"] = self._generate_organic_recommendations(analysis)
            
        except Exception as e:
            analysis["error"] = str(e)
        
        return analysis
    
    def get_competition_insights(self) -> Dict:
        """Инсайты по конкуренции в рекламе"""
        insights = {
            "competition_levels": {},
            "price_segments_analysis": {},
            "brand_analysis": {},
            "recommendations": []
        }
        
        try:
            # Анализ уровней конкуренции по ставкам
            if 'Search cpm avg' in self.data.columns:
                cmp_data = self.data[self.data['Search cpm avg'] > 0]
                
                if not cmp_data.empty:
                    cmp_quartiles = cmp_data['Search cpm avg'].quantile([0.25, 0.5, 0.75])
                    
                    insights["competition_levels"] = {
                        "low_competition": {
                            "threshold": f"≤{cmp_quartiles[0.25]:.0f} ₽",
                            "count": len(cmp_data[cmp_data['Search cpm avg'] <= cmp_quartiles[0.25]]),
                            "avg_ratio": round(cmp_data[cmp_data['Search cpm avg'] <= cmp_quartiles[0.25]]['Price_to_CPM_ratio'].mean(), 2)
                        },
                        "medium_competition": {
                            "threshold": f"{cmp_quartiles[0.25]:.0f}-{cmp_quartiles[0.75]:.0f} ₽",
                            "count": len(cmp_data[(cmp_data['Search cpm avg'] > cmp_quartiles[0.25]) & (cmp_data['Search cpm avg'] <= cmp_quartiles[0.75])]),
                            "avg_ratio": round(cmp_data[(cmp_data['Search cpm avg'] > cmp_quartiles[0.25]) & (cmp_data['Search cmp avg'] <= cmp_quartiles[0.75])]['Price_to_CPM_ratio'].mean(), 2)
                        },
                        "high_competition": {
                            "threshold": f">{cmp_quartiles[0.75]:.0f} ₽",
                            "count": len(cmp_data[cmp_data['Search cpm avg'] > cmp_quartiles[0.75]]),
                            "avg_ratio": round(cmp_data[cmp_data['Search cpm avg'] > cmp_quartiles[0.75]]['Price_to_CPM_ratio'].mean(), 2)
                        }
                    }
            
            # Анализ по ценовым сегментам
            if 'Final price' in self.data.columns:
                price_bins = pd.qcut(self.data['Final price'], q=4, labels=['Бюджет', 'Средний-', 'Средний+', 'Премиум'])
                price_analysis = self.data.groupby(price_bins).agg({
                    'Search cmp avg': 'mean',
                    'Price_to_CPM_ratio': 'mean',
                    'Uses_ads': 'sum'
                }).round(2)
                
                insights["price_segments_analysis"] = price_analysis.to_dict('index')
            
            # Анализ по брендам (если есть данные)
            if 'Brand' in self.data.columns:
                brand_stats = self.data.groupby('Brand').agg({
                    'Search cpm avg': 'mean',
                    'Price_to_CPM_ratio': 'mean',
                    'Uses_ads': 'sum',
                    'Final price': 'mean'
                }).round(2)
                
                # Топ-5 брендов по эффективности рекламы
                top_brands = brand_stats.nlargest(5, 'Price_to_CPM_ratio')
                insights["brand_analysis"] = {
                    "top_efficient_brands": top_brands.to_dict('index'),
                    "total_brands": len(brand_stats),
                    "brands_using_ads": len(brand_stats[brand_stats['Uses_ads'] > 0])
                }
            
            insights["recommendations"] = self._generate_competition_insights_recommendations(insights)
            
        except Exception as e:
            insights["error"] = str(e)
        
        return insights
    
    def create_ads_charts(self) -> Dict[str, go.Figure]:
        """Создание графиков рекламного анализа"""
        charts = {}
        
        try:
            # 1. Коэффициент Чек/Ставка по позициям
            fig_ratio = px.scatter(
                self.data[self.data['Search cpm avg'] > 0],
                x='Category position avg',
                y='Price_to_CPM_ratio',
                size='Final price',
                color='Position_segment',
                hover_data=['Brand', 'Search cpm avg'] if 'Brand' in self.data.columns else ['Search cpm avg'],
                title='Коэффициент Чек/Ставка по позициям в категории',
                labels={
                    'Category position avg': 'Позиция в категории',
                    'Price_to_CPM_ratio': 'Коэффициент Чек/Ставка'
                }
            )
            
            # Добавляем пороговые линии
            fig_ratio.add_hline(y=4.0, line_dash="dash", line_color="green", annotation_text="Отлично (4.0)")
            fig_ratio.add_hline(y=3.0, line_dash="dash", line_color="yellow", annotation_text="Хорошо (3.0)")
            fig_ratio.add_hline(y=2.0, line_dash="dash", line_color="orange", annotation_text="Средне (2.0)")
            fig_ratio.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="Плохо (1.0)")
            
            fig_ratio.update_layout(height=500)
            charts["ratio_by_position"] = fig_ratio
            
            # 2. Сравнение ТОП-10 и ТОП-100
            top_10 = self.data[self.data['Category position avg'] <= 10]
            top_100 = self.data[(self.data['Category position avg'] > 10) & (self.data['Category position avg'] <= 100)]
            
            comparison_data = pd.DataFrame({
                'Сегмент': ['ТОП-10', 'ТОП-100'],
                'Средняя_ставка': [top_10['Search cpm avg'].mean(), top_100['Search cpm avg'].mean()],
                'Средний_чек': [top_10['Final price'].mean(), top_100['Final price'].mean()],
                'Коэффициент': [top_10['Price_to_CPM_ratio'].mean(), top_100['Price_to_CPM_ratio'].mean()]
            })
            
            fig_comparison = make_subplots(
                rows=1, cols=3,
                subplot_titles=['Средняя ставка', 'Средний чек', 'Коэффициент Чек/Ставка']
            )
            
            fig_comparison.add_trace(
                go.Bar(x=comparison_data['Сегмент'], y=comparison_data['Средняя_ставка'], name='Ставка'),
                row=1, col=1
            )
            
            fig_comparison.add_trace(
                go.Bar(x=comparison_data['Сегмент'], y=comparison_data['Средний_чек'], name='Чек'),
                row=1, col=2
            )
            
            fig_comparison.add_trace(
                go.Bar(x=comparison_data['Сегмент'], y=comparison_data['Коэффициент'], name='Коэффициент'),
                row=1, col=3
            )
            
            fig_comparison.update_layout(height=400, title_text="Сравнение ТОП-10 и ТОП-100")
            charts["top_segments_comparison"] = fig_comparison
            
            # 3. Распределение эффективности рекламы
            efficiency_counts = self.data['Ad_efficiency_category'].value_counts()
            
            fig_efficiency = px.pie(
                values=efficiency_counts.values,
                names=efficiency_counts.index,
                title='Распределение товаров по эффективности рекламы'
            )
            fig_efficiency.update_layout(height=400)
            charts["ad_efficiency_distribution"] = fig_efficiency
            
            # 4. Органика vs Реклама
            organic_paid_data = pd.DataFrame({
                'Тип': ['Органика', 'Реклама'],
                'Количество': [
                    len(self.data[self.data['Organic_only'] == True]),
                    len(self.data[self.data['Uses_ads'] == True])
                ]
            })
            
            fig_organic_paid = px.bar(
                organic_paid_data,
                x='Тип',
                y='Количество',
                title='Органические vs Рекламные товары',
                color='Тип',
                color_discrete_map={'Органика': 'green', 'Реклама': 'red'}
            )
            fig_organic_paid.update_layout(height=400)
            charts["organic_vs_paid"] = fig_organic_paid
            
            # 5. Heatmap: Цена vs Ставка vs Позиция
            # Создаем бины для лучшей визуализации
            price_bins = pd.qcut(self.data['Final price'], q=5, labels=['Очень низкая', 'Низкая', 'Средняя', 'Высокая', 'Очень высокая'])
            position_bins = pd.cut(self.data['Category position avg'], bins=[0, 10, 50, 100, 500, float('inf')], 
                                 labels=['1-10', '11-50', '51-100', '101-500', '>500'])
            
            heatmap_data = pd.crosstab(price_bins, position_bins, values=self.data['Search cmp avg'], aggfunc='mean')
            
            fig_heatmap = px.imshow(
                heatmap_data,
                title='Тепловая карта: средние ставки по цене и позиции',
                labels={'x': 'Позиция в категории', 'y': 'Ценовой сегмент', 'color': 'Средняя ставка'},
                color_continuous_scale='Reds'
            )
            fig_heatmap.update_layout(height=400)
            charts["price_position_heatmap"] = fig_heatmap
            
        except Exception as e:
            st.error(f"Ошибка при создании графиков рекламного анализа: {e}")
        
        return charts
    
    def _generate_top_segments_recommendations(self, analysis: Dict) -> List[str]:
        """Генерация рекомендаций по ТОП сегментам"""
        recommendations = []
        
        try:
            niche_assessment = analysis.get("niche_assessment", {})
            niche_status = niche_assessment.get("niche_status", "Неизвестно")
            heat_level = niche_assessment.get("heat_level", 3)
            
            if heat_level <= 2:
                recommendations.append(f"🟢 {niche_status} ниша - хорошие возможности для продвижения")
            elif heat_level == 3:
                recommendations.append(f"🟡 {niche_status} - требуется сбалансированная стратегия")
            else:
                recommendations.append(f"🔴 {niche_status} - высокие риски в рекламном продвижении")
            
            # Конкретные рекомендации по ставкам
            top_10_data = analysis["top_10_analysis"]
            top_100_data = analysis["top_100_analysis"]
            
            recommendations.append(f"💰 Средняя ставка в ТОП-10: {top_10_data['avg_cpm']} ₽")
            recommendations.append(f"💰 Средняя ставка в ТОП-100: {top_100_data['avg_cpm']} ₽")
            
            # Рекомендации по органике
            organic_pct_top10 = 100 - top_10_data["ads_percentage"]
            if organic_pct_top10 > 30:
                recommendations.append("🌱 Много органических позиций в ТОП-10 - есть возможности без рекламы")
            elif organic_pct_top10 < 10:
                recommendations.append("🎯 Почти все позиции в ТОП-10 рекламные - реклама обязательна")
        
        except Exception as e:
            recommendations.append(f"Ошибка в анализе: {e}")
        
        return recommendations
    
    def _generate_organic_recommendations(self, analysis: Dict) -> List[str]:
        """Генерация рекомендаций по органике"""
        recommendations = []
        
        try:
            overview = analysis.get("organic_overview", {})
            organic_pct = overview.get("organic_percentage", 0)
            
            if organic_pct > 40:
                recommendations.append("🌱 Высокий процент органических товаров - SEO работает")
            elif organic_pct < 20:
                recommendations.append("🎯 Мало органических товаров - рынок зависит от рекламы")
            
            opportunities = analysis.get("organic_opportunities", [])
            for opp in opportunities:
                if opp["organic_count"] > 0:
                    recommendations.append(f"✅ В {opp['segment']} есть {opp['organic_count']} органических товаров")
            
            vs_paid = analysis.get("organic_vs_paid", {})
            if "organic_advantage" in vs_paid and vs_paid["organic_advantage"] > 0:
                recommendations.append(f"📈 Органика показывает на {vs_paid['organic_advantage']:.1f}% лучше выручку")
        
        except Exception as e:
            recommendations.append(f"Ошибка в анализе органики: {e}")
        
        return recommendations
    
    def _generate_competition_insights_recommendations(self, insights: Dict) -> List[str]:
        """Генерация рекомендаций по конкурентным инсайтам"""
        recommendations = []
        
        try:
            competition_levels = insights.get("competition_levels", {})
            if "low_competition" in competition_levels:
                low_comp = competition_levels["low_competition"]
                recommendations.append(f"🎯 Низкая конкуренция: ставки до {low_comp['threshold']}, коэффициент {low_comp['avg_ratio']}")
            
            price_segments = insights.get("price_segments_analysis", {})
            if price_segments:
                best_segment = max(price_segments.items(), key=lambda x: x[1].get('Price_to_CPM_ratio', 0))
                recommendations.append(f"💎 Лучший ценовой сегмент: {best_segment[0]} (коэффициент {best_segment[1]['Price_to_CPM_ratio']})")
            
            brand_analysis = insights.get("brand_analysis", {})
            if "brands_using_ads" in brand_analysis:
                ads_brands = brand_analysis["brands_using_ads"]
                total_brands = brand_analysis["total_brands"]
                ads_pct = (ads_brands / total_brands) * 100
                
                if ads_pct > 80:
                    recommendations.append("🔥 Большинство брендов используют рекламу - высокая конкуренция")
                elif ads_pct < 50:
                    recommendations.append("🌟 Многие бренды не рекламируются - есть возможности")
        
        except Exception as e:
            recommendations.append(f"Ошибка в конкурентном анализе: {e}")
        
        return recommendations
    
    def get_summary_metrics(self) -> Dict:
        """Получение сводных метрик для дашборда"""
        try:
            top_10 = self.data[self.data['Category position avg'] <= 10]
            top_100 = self.data[self.data['Category position avg'] <= 100]
            
            summary = {
                "total_products": len(self.data),
                "top_10_count": len(top_10),
                "top_100_count": len(top_100),
                "avg_cpm_top_10": round(top_10['Search cpm avg'].mean(), 2) if len(top_10) > 0 else 0,
                "avg_cpm_top_100": round(top_100['Search cpm avg'].mean(), 2) if len(top_100) > 0 else 0,
                "avg_ratio_top_10": round(top_10['Price_to_CPM_ratio'].mean(), 2) if len(top_10) > 0 else 0,
                "avg_ratio_top_100": round(top_100['Price_to_CPM_ratio'].mean(), 2) if len(top_100) > 0 else 0,
                "products_with_ads": len(self.data[self.data['Uses_ads'] == True]),
                "organic_products": len(self.data[self.data['Organic_only'] == True]),
                "ads_usage_percentage": round((len(self.data[self.data['Uses_ads'] == True]) / len(self.data)) * 100, 2),
                "niche_heat_level": min(self.get_top_segments_analysis().get("niche_assessment", {}).get("heat_level", 3), 5)
            }
            
            return summary
            
        except Exception as e:
            return {"error": str(e)}
