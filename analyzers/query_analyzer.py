import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple, Optional
import streamlit as st


class QueryAnalyzer:
    """Анализатор поисковых запросов"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        self.prepare_data()
        
    def prepare_data(self):
        """Подготовка данных для анализа"""
        # Убираем строки с пустыми или нулевыми значениями
        self.data = self.data.dropna(subset=['Частота WB', 'Товаров в запросе'])
        self.data = self.data[self.data['Товаров в запросе'] > 0]
        
        # Рассчитываем коэффициент спрос/предложение если его нет
        if 'Коэффициент_спрос_предложение' not in self.data.columns:
            self.data['Коэффициент_спрос_предложение'] = self.data['Частота WB'] / self.data['Товаров в запросе']
        
        # Добавляем категории эффективности
        self.data['Категория_эффективности'] = self.data['Коэффициент_спрос_предложение'].apply(self._categorize_efficiency)
        
        # Рассчитываем потенциал запроса
        self.data['Потенциал_запроса'] = self._calculate_query_potential()
    
    def _categorize_efficiency(self, ratio: float) -> str:
        """Категоризация эффективности запроса"""
        if ratio >= 5.0:
            return "Отлично (≥5x)"
        elif ratio >= 3.0:
            return "Хорошо (3-5x)"
        elif ratio >= 2.0:
            return "Средне (2-3x)"
        else:
            return "Низко (<2x)"
    
    def _calculate_query_potential(self) -> pd.Series:
        """Расчет потенциала запроса (комбинированная метрика)"""
        # Нормализуем метрики
        freq_norm = self.data['Частота WB'] / self.data['Частота WB'].max()
        ratio_norm = np.minimum(self.data['Коэффициент_спрос_предложение'] / 10, 1.0)  # Ограничиваем сверху
        
        # Потенциал = частота * коэффициент эффективности
        return (freq_norm * ratio_norm * 100).round(2)
    
    def get_efficiency_analysis(self) -> Dict:
        """Анализ эффективности запросов"""
        analysis = {
            "total_queries": len(self.data),
            "efficiency_breakdown": {},
            "effective_queries": {},
            "top_opportunities": [],
            "recommendations": []
        }
        
        try:
            # Разбивка по категориям эффективности
            efficiency_counts = self.data['Категория_эффективности'].value_counts()
            total = len(self.data)
            
            for category, count in efficiency_counts.items():
                percentage = (count / total) * 100
                analysis["efficiency_breakdown"][category] = {
                    "count": count,
                    "percentage": round(percentage, 2)
                }
            
            # Эффективные запросы (коэффициент >= 2.0)
            effective_df = self.data[self.data['Коэффициент_спрос_предложение'] >= 2.0]
            analysis["effective_queries"] = {
                "count": len(effective_df),
                "percentage": round((len(effective_df) / total) * 100, 2),
                "avg_frequency": round(effective_df['Частота WB'].mean(), 0) if len(effective_df) > 0 else 0,
                "avg_ratio": round(effective_df['Коэффициент_спрос_предложение'].mean(), 2) if len(effective_df) > 0 else 0
            }
            
            # Топ возможности (высокий потенциал + коэффициент >= 2)
            top_opportunities = self.data[
                (self.data['Коэффициент_спрос_предложение'] >= 2.0) &
                (self.data['Частота WB'] >= self.data['Частота WB'].quantile(0.7))  # Топ 30% по частоте
            ].nlargest(20, 'Потенциал_запроса')
            
            analysis["top_opportunities"] = top_opportunities[[
                'Ключевое слово', 'Частота WB', 'Товаров в запросе', 
                'Коэффициент_спрос_предложение', 'Потенциал_запроса'
            ]].to_dict('records')
            
            # Генерация рекомендаций
            analysis["recommendations"] = self._generate_efficiency_recommendations(analysis)
            
        except Exception as e:
            analysis["error"] = str(e)
        
        return analysis
    
    def get_competition_analysis(self) -> Dict:
        """Анализ уровня конкуренции"""
        analysis = {
            "competition_levels": {},
            "market_saturation": {},
            "niche_gaps": [],
            "recommendations": []
        }
        
        try:
            # Анализ уровня конкуренции по количеству товаров в запросе
            self.data['Уровень_конкуренции'] = pd.cut(
                self.data['Товаров в запросе'],
                bins=[0, 10, 50, 200, float('inf')],
                labels=['Низкая (≤10)', 'Средняя (11-50)', 'Высокая (51-200)', 'Очень высокая (>200)'],
                include_lowest=True
            )
            
            competition_stats = self.data.groupby('Уровень_конкуренции').agg({
                'Ключевое слово': 'count',
                'Частота WB': 'mean',
                'Коэффициент_спрос_предложение': 'mean'
            }).round(2)
            
            analysis["competition_levels"] = competition_stats.to_dict('index')
            
            # Анализ насыщенности рынка
            total_queries = len(self.data)
            low_competition = len(self.data[self.data['Товаров в запросе'] <= 50])
            high_frequency = len(self.data[self.data['Частота WB'] >= self.data['Частота WB'].median()])
            
            analysis["market_saturation"] = {
                "low_competition_percentage": round((low_competition / total_queries) * 100, 2),
                "high_frequency_percentage": round((high_frequency / total_queries) * 100, 2),
                "market_status": self._determine_market_status(low_competition, high_frequency, total_queries)
            }
            
            # Поиск ниш с низкой конкуренцией и высоким спросом
            niche_gaps = self.data[
                (self.data['Товаров в запросе'] <= 30) &  # Низкая конкуренция
                (self.data['Частота WB'] >= self.data['Частота WB'].quantile(0.6))  # Высокий спрос
            ].nlargest(15, 'Частота WB')
            
            analysis["niche_gaps"] = niche_gaps[[
                'Ключевое слово', 'Частота WB', 'Товаров в запросе', 'Коэффициент_спрос_предложение'
            ]].to_dict('records')
            
            analysis["recommendations"] = self._generate_competition_recommendations(analysis)
            
        except Exception as e:
            analysis["error"] = str(e)
        
        return analysis
    
    def get_keyword_insights(self) -> Dict:
        """Анализ ключевых слов и инсайты"""
        insights = {
            "keyword_stats": {},
            "length_analysis": {},
            "frequency_distribution": {},
            "semantic_groups": {},
            "recommendations": []
        }
        
        try:
            # Базовая статистика по ключевым словам
            insights["keyword_stats"] = {
                "total_unique_keywords": len(self.data),
                "avg_frequency": round(self.data['Частота WB'].mean(), 0),
                "median_frequency": round(self.data['Частота WB'].median(), 0),
                "avg_competition": round(self.data['Товаров в запросе'].mean(), 0),
                "median_competition": round(self.data['Товаров в запросе'].median(), 0)
            }
            
            # Анализ длины запросов
            self.data['Длина_запроса'] = self.data['Ключевое слово'].str.split().str.len()
            length_stats = self.data.groupby('Длина_запроса').agg({
                'Ключевое слово': 'count',
                'Частота WB': 'mean',
                'Коэффициент_спрос_предложение': 'mean'
            }).round(2)
            
            insights["length_analysis"] = length_stats.to_dict('index')
            
            # Распределение частотности
            freq_ranges = pd.cut(
                self.data['Частота WB'],
                bins=[0, 1000, 10000, 100000, float('inf')],
                labels=['Низкая (≤1K)', 'Средняя (1-10K)', 'Высокая (10-100K)', 'Очень высокая (>100K)'],
                include_lowest=True
            )
            
            freq_distribution = freq_ranges.value_counts()
            insights["frequency_distribution"] = {
                range_name: count for range_name, count in freq_distribution.items()
            }
            
            # Простая семантическая группировка (по первому слову)
            self.data['Первое_слово'] = self.data['Ключевое слово'].str.split().str[0].str.lower()
            semantic_groups = self.data['Первое_слово'].value_counts().head(10)
            
            insights["semantic_groups"] = {
                word: count for word, count in semantic_groups.items()
            }
            
            insights["recommendations"] = self._generate_keyword_recommendations(insights)
            
        except Exception as e:
            insights["error"] = str(e)
        
        return insights
    
    def create_queries_charts(self) -> Dict[str, go.Figure]:
        """Создание графиков для анализа запросов"""
        charts = {}
        
        try:
            # 1. Scatter plot: Частота vs Конкуренция
            fig_scatter = px.scatter(
                self.data.head(1000),  # Ограничиваем для производительности
                x='Товаров в запросе',
                y='Частота WB',
                color='Коэффициент_спрос_предложение',
                size='Потенциал_запроса',
                hover_data=['Ключевое слово'],
                title='Соотношение спроса и предложения по запросам',
                labels={
                    'Товаров в запросе': 'Количество товаров (конкуренция)',
                    'Частота WB': 'Частота запросов (спрос)',
                    'Коэффициент_спрос_предложение': 'Коэффициент'
                },
                color_continuous_scale='RdYlGn'
            )
            fig_scatter.update_layout(height=500)
            charts["demand_supply_scatter"] = fig_scatter
            
            # 2. Гистограмма эффективности запросов
            efficiency_counts = self.data['Категория_эффективности'].value_counts()
            fig_efficiency = px.bar(
                x=efficiency_counts.index,
                y=efficiency_counts.values,
                title='Распределение запросов по эффективности',
                labels={'x': 'Категория эффективности', 'y': 'Количество запросов'},
                color=efficiency_counts.values,
                color_continuous_scale='RdYlGn'
            )
            fig_efficiency.update_layout(height=400)
            charts["efficiency_distribution"] = fig_efficiency
            
            # 3. Топ-20 запросов по потенциалу
            top_potential = self.data.nlargest(20, 'Потенциал_запроса')
            fig_top_potential = px.bar(
                top_potential,
                x='Потенциал_запроса',
                y='Ключевое слово',
                orientation='h',
                title='Топ-20 запросов по потенциалу',
                labels={'Потенциал_запроса': 'Потенциал запроса', 'Ключевое слово': 'Ключевое слово'},
                color='Коэффициент_спрос_предложение',
                color_continuous_scale='RdYlGn'
            )
            fig_top_potential.update_layout(height=600)
            charts["top_potential_queries"] = fig_top_potential
            
            # 4. Анализ длины запросов
            if 'Длина_запроса' in self.data.columns:
                length_analysis = self.data.groupby('Длина_запроса').agg({
                    'Коэффициент_спрос_предложение': 'mean',
                    'Частота WB': 'mean',
                    'Ключевое слово': 'count'
                }).reset_index()
                
                fig_length = make_subplots(
                    rows=1, cols=2,
                    subplot_titles=['Эффективность по длине', 'Количество запросов по длине']
                )
                
                fig_length.add_trace(
                    go.Bar(x=length_analysis['Длина_запроса'], 
                          y=length_analysis['Коэффициент_спрос_предложение'],
                          name='Средний коэффициент'),
                    row=1, col=1
                )
                
                fig_length.add_trace(
                    go.Bar(x=length_analysis['Длина_запроса'], 
                          y=length_analysis['Ключевое слово'],
                          name='Количество запросов'),
                    row=1, col=2
                )
                
                fig_length.update_layout(height=400, title_text="Анализ запросов по длине")
                charts["length_analysis"] = fig_length
            
            # 5. Heatmap конкуренции
            # Создаем бины для частоты и конкуренции
            freq_bins = pd.qcut(self.data['Частота WB'], q=5, labels=['Очень низкая', 'Низкая', 'Средняя', 'Высокая', 'Очень высокая'])
            comp_bins = pd.qcut(self.data['Товаров в запросе'], q=5, labels=['Очень низкая', 'Низкая', 'Средняя', 'Высокая', 'Очень высокая'])
            
            heatmap_data = pd.crosstab(freq_bins, comp_bins, values=self.data['Коэффициент_спрос_предложение'], aggfunc='mean')
            
            fig_heatmap = px.imshow(
                heatmap_data,
                title='Тепловая карта: эффективность по частоте и конкуренции',
                labels={'x': 'Уровень конкуренции', 'y': 'Частота запросов', 'color': 'Средний коэффициент'},
                color_continuous_scale='RdYlGn'
            )
            fig_heatmap.update_layout(height=400)
            charts["competition_heatmap"] = fig_heatmap
            
        except Exception as e:
            st.error(f"Ошибка при создании графиков запросов: {e}")
        
        return charts
    
    def _determine_market_status(self, low_competition: int, high_frequency: int, total: int) -> str:
        """Определение статуса рынка"""
        low_comp_pct = (low_competition / total) * 100
        high_freq_pct = (high_frequency / total) * 100
        
        if low_comp_pct > 60 and high_freq_pct > 40:
            return "Недонасыщенный рынок"
        elif low_comp_pct < 30 and high_freq_pct < 60:
            return "Перенасыщенный рынок"
        else:
            return "Сбалансированный рынок"
    
    def _generate_efficiency_recommendations(self, analysis: Dict) -> List[str]:
        """Генерация рекомендаций по эффективности"""
        recommendations = []
        
        try:
            effective_pct = analysis["effective_queries"]["percentage"]
            
            if effective_pct >= 20:
                recommendations.append("🟢 Отличная ниша! Много эффективных запросов для продвижения")
            elif effective_pct >= 10:
                recommendations.append("🟡 Хорошая ниша с умеренными возможностями")
            elif effective_pct >= 5:
                recommendations.append("🟠 Средняя ниша. Требуется точечная работа с запросами")
            else:
                recommendations.append("🔴 Сложная ниша. Мало эффективных запросов")
            
            # Конкретные рекомендации
            if len(analysis["top_opportunities"]) > 10:
                recommendations.append(f"🎯 Найдено {len(analysis['top_opportunities'])} перспективных запросов для SEO")
            
            if effective_pct > 0:
                avg_ratio = analysis["effective_queries"]["avg_ratio"]
                if avg_ratio >= 4:
                    recommendations.append("🚀 Высокий средний коэффициент эффективности - быстрый рост возможен")
        
        except Exception as e:
            recommendations.append(f"Ошибка в анализе: {e}")
        
        return recommendations
    
    def _generate_competition_recommendations(self, analysis: Dict) -> List[str]:
        """Генерация рекомендаций по конкуренции"""
        recommendations = []
        
        try:
            market_status = analysis["market_saturation"]["market_status"]
            low_comp_pct = analysis["market_saturation"]["low_competition_percentage"]
            
            if market_status == "Недонасыщенный рынок":
                recommendations.append("🟢 Рынок недонасыщен - отличные возможности для входа")
            elif market_status == "Перенасыщенный рынок":
                recommendations.append("🔴 Рынок перенасыщен - высокая конкуренция")
            else:
                recommendations.append("🟡 Сбалансированный рынок - умеренная конкуренция")
            
            if low_comp_pct > 50:
                recommendations.append("📈 Много запросов с низкой конкуренцией")
            
            niche_gaps_count = len(analysis["niche_gaps"])
            if niche_gaps_count > 10:
                recommendations.append(f"🎯 Найдено {niche_gaps_count} ниш с низкой конкуренцией и высоким спросом")
        
        except Exception as e:
            recommendations.append(f"Ошибка в анализе конкуренции: {e}")
        
        return recommendations
    
    def _generate_keyword_recommendations(self, insights: Dict) -> List[str]:
        """Генерация рекомендаций по ключевым словам"""
        recommendations = []
        
        try:
            # Анализ длины запросов
            if "length_analysis" in insights:
                best_length = max(insights["length_analysis"].items(), 
                                key=lambda x: x[1].get('Коэффициент_спрос_предложение', 0))
                recommendations.append(f"📝 Оптимальная длина запроса: {best_length[0]} слов")
            
            # Семантические группы
            if "semantic_groups" in insights:
                top_semantic = list(insights["semantic_groups"].keys())[:3]
                recommendations.append(f"🔤 Топ семантические группы: {', '.join(top_semantic)}")
        
        except Exception as e:
            recommendations.append(f"Ошибка в анализе ключевых слов: {e}")
        
        return recommendations
    
    def get_summary_metrics(self) -> Dict:
        """Получение сводных метрик для дашборда"""
        try:
            effective_queries = len(self.data[self.data['Коэффициент_спрос_предложение'] >= 2.0])
            
            summary = {
                "total_queries": len(self.data),
                "effective_queries": effective_queries,
                "effectiveness_rate": round((effective_queries / len(self.data)) * 100, 2) if len(self.data) > 0 else 0,
                "avg_frequency": round(self.data['Частота WB'].mean(), 0),
                "avg_competition": round(self.data['Товаров в запросе'].mean(), 0),
                "best_ratio": round(self.data['Коэффициент_спрос_предложение'].max(), 2),
                "top_query": self.data.loc[self.data['Потенциал_запроса'].idxmax(), 'Ключевое слово'] if not self.data.empty else "N/A"
            }
            
            return summary
            
        except Exception as e:
            return {"error": str(e)}
