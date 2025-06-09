import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional
from config import SCORING_CONFIG, TREND_THRESHOLDS, QUERY_THRESHOLDS, ADS_THRESHOLDS, TOTAL_SCORE_RANGES


class ScoringEngine:
    """Основной движок скоринга ниши MPStats"""
    
    def __init__(self):
        self.scores = {}
        self.detailed_scores = {}
        self.recommendations = {}
    
    def calculate_total_score(self, loaded_data: Dict[str, pd.DataFrame]) -> Dict:
        """Расчет общего скоринга ниши"""
        
        # Инициализируем результаты
        results = {
            "trend_score": 0,
            "query_score": 0,
            "price_score": 0,
            "stock_score": 0,
            "ads_score": 0,
            "total_score": 0,
            "niche_rating": "poor",
            "detailed_analysis": {},
            "recommendations": []
        }
        
        # Рассчитываем скоринг для каждого модуля
        if "trends" in loaded_data:
            results["trend_score"], results["detailed_analysis"]["trends"] = self._calculate_trend_score(loaded_data["trends"])
        
        if "queries" in loaded_data:
            results["query_score"], results["detailed_analysis"]["queries"] = self._calculate_query_score(loaded_data["queries"])
        
        if "price" in loaded_data:
            results["price_score"], results["detailed_analysis"]["price"] = self._calculate_price_score(loaded_data["price"])
        
        if "days" in loaded_data:
            results["stock_score"], results["detailed_analysis"]["stock"] = self._calculate_stock_score(loaded_data["days"])
        
        if "products" in loaded_data:
            results["ads_score"], results["detailed_analysis"]["ads"] = self._calculate_ads_score(loaded_data["products"])
        
        # Рассчитываем общий балл
        results["total_score"] = (
            results["trend_score"] + 
            results["query_score"] + 
            results["price_score"] + 
            results["stock_score"] + 
            results["ads_score"]
        )
        
        # Определяем рейтинг ниши
        results["niche_rating"] = self._get_niche_rating(results["total_score"])
        
        # Генерируем рекомендации
        results["recommendations"] = self._generate_recommendations(results)
        
        self.scores = results
        return results
    
    def _calculate_trend_score(self, df: pd.DataFrame) -> Tuple[int, Dict]:
        """Скоринг трендов и пиковых месяцев"""
        
        analysis = {
            "peak_months": {},
            "yoy_changes": {},
            "score_breakdown": {},
            "total_score": 0
        }
        
        try:
            # Группируем данные по годам
            df['Год'] = df['Месяц'].dt.year
            df['Месяц_номер'] = df['Месяц'].dt.month
            
            # 1. Определяем пиковые месяцы по продажам для каждого года
            peak_months = {}
            for year in df['Год'].unique():
                year_data = df[df['Год'] == year]
                if not year_data.empty and 'Продажи' in year_data.columns:
                    peak_month = year_data.loc[year_data['Продажи'].idxmax(), 'Месяц_номер']
                    peak_months[year] = peak_month
            
            analysis["peak_months"] = peak_months
            
            # 2. Рассчитываем YoY изменения для разных метрик
            metrics = [
                ("brands_with_sales", "Бренды с продажами"),
                ("brands_total", "Бренды"),
                ("products_with_sales", "Товары с продажами"),
                ("products_total", "Товары"),
                ("avg_check", "Средний чек, ₽")
            ]
            
            scores = []
            
            for metric_key, metric_col in metrics:
                if metric_col in df.columns:
                    yoy_score, yoy_change = self._calculate_yoy_score(df, metric_col)
                    analysis["yoy_changes"][metric_key] = yoy_change
                    analysis["score_breakdown"][metric_key] = yoy_score
                    scores.append(yoy_score)
            
            # Итоговый балл - среднее по всем метрикам
            final_score = int(np.mean(scores)) if scores else 0
            analysis["total_score"] = final_score
            
        except Exception as e:
            analysis["error"] = str(e)
            final_score = 0
        
        return final_score, analysis
    
    def _calculate_yoy_score(self, df: pd.DataFrame, metric_col: str) -> Tuple[int, Dict]:
        """Расчет YoY скоринга для метрики"""
        
        try:
            # Группируем по годам и берем среднее значение за год
            yearly_data = df.groupby('Год')[metric_col].mean().sort_index()
            
            if len(yearly_data) < 2:
                return 2, {"message": "Недостаточно данных для YoY анализа"}
            
            # Рассчитываем YoY изменения
            yoy_changes = []
            for i in range(1, len(yearly_data)):
                prev_value = yearly_data.iloc[i-1]
                curr_value = yearly_data.iloc[i]
                
                if prev_value > 0:
                    change_percent = ((curr_value - prev_value) / prev_value) * 100
                    yoy_changes.append(change_percent)
            
            if not yoy_changes:
                return 2, {"message": "Не удалось рассчитать YoY изменения"}
            
            # Определяем средний YoY рост
            avg_yoy_change = np.mean(yoy_changes)
            
            # Определяем балл на основе пороговых значений
            if avg_yoy_change >= TREND_THRESHOLDS["excellent"]:
                score = 4
                trend = "Отличный рост"
            elif avg_yoy_change >= TREND_THRESHOLDS["good"]:
                score = 3
                trend = "Хороший рост"
            elif avg_yoy_change >= TREND_THRESHOLDS["stable"]:
                score = 2
                trend = "Стабильность"
            else:
                score = 1
                trend = "Снижение"
            
            change_data = {
                "avg_yoy_change": round(avg_yoy_change, 2),
                "trend": trend,
                "yearly_values": yearly_data.to_dict(),
                "yoy_changes": [round(x, 2) for x in yoy_changes]
            }
            
            return score, change_data
            
        except Exception as e:
            return 1, {"error": str(e)}
    
    def _calculate_query_score(self, df: pd.DataFrame) -> Tuple[int, Dict]:
        """Скоринг запросов"""
        
        analysis = {
            "total_queries": len(df),
            "effective_queries": 0,
            "efficiency_ratio": 0,
            "top_queries": [],
            "score": 0
        }
        
        try:
            # Рассчитываем эффективные запросы (коэффициент >= 2.0)
            if "Коэффициент_спрос_предложение" in df.columns:
                effective_queries = df[df["Коэффициент_спрос_предложение"] >= 2.0]
                analysis["effective_queries"] = len(effective_queries)
                
                # Процент эффективных запросов
                if len(df) > 0:
                    efficiency_ratio = (len(effective_queries) / len(df)) * 100
                    analysis["efficiency_ratio"] = round(efficiency_ratio, 2)
                
                # Топ-10 самых эффективных запросов
                top_queries = df.nlargest(10, "Коэффициент_спрос_предложение")[
                    ["Ключевое слово", "Частота WB", "Товаров в запросе", "Коэффициент_спрос_предложение"]
                ].to_dict('records')
                analysis["top_queries"] = top_queries
                
                # Определяем скоринг на основе процента эффективных запросов
                if efficiency_ratio >= 20:  # 20% и более эффективных запросов
                    score = 4
                elif efficiency_ratio >= 10:  # 10-20%
                    score = 3
                elif efficiency_ratio >= 5:   # 5-10%
                    score = 2
                else:  # Менее 5%
                    score = 1
                
                analysis["score"] = score
            else:
                score = 0
                analysis["error"] = "Отсутствует коэффициент спрос/предложение"
                
        except Exception as e:
            analysis["error"] = str(e)
            score = 0
        
        return score, analysis
    
    def _calculate_price_score(self, df: pd.DataFrame) -> Tuple[int, Dict]:
        """Скоринг ценовой сегментации"""
        
        analysis = {
            "best_segment": {},
            "segment_analysis": [],
            "score": 0
        }
        
        try:
            if "Выручка на товар, ₽" in df.columns:
                # Находим самый эффективный сегмент
                best_segment_idx = df["Выручка на товар, ₽"].idxmax()
                best_segment = df.loc[best_segment_idx]
                
                analysis["best_segment"] = {
                    "price_range": f"{best_segment['От']}-{best_segment['До']} ₽",
                    "revenue_per_product": best_segment["Выручка на товар, ₽"],
                    "products_count": best_segment.get("Товары", 0),
                    "sellers_count": best_segment.get("Продавцы", 0)
                }
                
                # Анализ всех сегментов
                segment_data = []
                for _, row in df.iterrows():
                    segment_data.append({
                        "price_range": f"{row['От']}-{row['До']} ₽",
                        "revenue_per_product": row["Выручка на товар, ₽"],
                        "products": row.get("Товары", 0),
                        "products_with_sales": row.get("Товары с продажами", 0),
                        "sellers": row.get("Продавцы", 0)
                    })
                
                analysis["segment_analysis"] = segment_data
                
                # Скоринг на основе распределения выручки и конкуренции
                max_revenue = df["Выручка на товар, ₽"].max()
                median_revenue = df["Выручка на товар, ₽"].median()
                
                # Проверяем есть ли сегменты с низкой конкуренцией и высокой выручкой
                low_competition_segments = df[
                    (df["Выручка на товар, ₽"] > median_revenue) & 
                    (df.get("Продавцы", 0) < df["Продавцы"].median() if "Продавцы" in df.columns else True)
                ]
                
                if len(low_competition_segments) >= 3:
                    score = 4  # Много выгодных сегментов
                elif len(low_competition_segments) >= 2:
                    score = 3  # Есть выгодные сегменты
                elif len(low_competition_segments) >= 1:
                    score = 2  # Один выгодный сегмент
                else:
                    score = 1  # Нет явно выгодных сегментов
                
                analysis["score"] = score
            else:
                score = 0
                analysis["error"] = "Отсутствует колонка 'Выручка на товар'"
                
        except Exception as e:
            analysis["error"] = str(e)
            score = 0
        
        return score, analysis
    
    def _calculate_stock_score(self, df: pd.DataFrame) -> Tuple[int, Dict]:
        """Скоринг остатков и сезонности"""
        
        analysis = {
            "seasonal_patterns": {},
            "peak_stock_months": {},
            "score": 0
        }
        
        try:
            if "Остаток" in df.columns and "Дата" in df.columns:
                df['Год'] = df['Дата'].dt.year
                df['Месяц'] = df['Дата'].dt.month
                
                # Находим пиковые месяцы по остаткам для каждого года
                peak_months = {}
                for year in df['Год'].unique():
                    year_data = df[df['Год'] == year]
                    if not year_data.empty:
                        monthly_avg = year_data.groupby('Месяц')['Остаток'].mean()
                        peak_month = monthly_avg.idxmax()
                        peak_months[year] = {
                            "month": peak_month,
                            "avg_stock": round(monthly_avg[peak_month], 0)
                        }
                
                analysis["peak_stock_months"] = peak_months
                
                # Анализ сезонности
                monthly_stats = df.groupby('Месяц')['Остаток'].agg(['mean', 'std']).round(0)
                analysis["seasonal_patterns"] = monthly_stats.to_dict('index')
                
                # Скоринг на основе стабильности поставок
                cv_stock = df['Остаток'].std() / df['Остаток'].mean() if df['Остаток'].mean() > 0 else 0
                
                # Процент дней с нулевыми остатками
                zero_stock_ratio = (df['Остаток'] == 0).sum() / len(df) * 100
                
                if cv_stock < 0.3 and zero_stock_ratio < 10:  # Стабильные поставки
                    score = 4
                elif cv_stock < 0.5 and zero_stock_ratio < 20:  # Умеренная вариативность
                    score = 3
                elif cv_stock < 0.7 and zero_stock_ratio < 30:  # Высокая вариативность
                    score = 2
                else:  # Нестабильные поставки
                    score = 1
                
                analysis["coefficient_variation"] = round(cv_stock, 3)
                analysis["zero_stock_ratio"] = round(zero_stock_ratio, 2)
                analysis["score"] = score
            else:
                score = 0
                analysis["error"] = "Отсутствуют необходимые колонки для анализа остатков"
                
        except Exception as e:
            analysis["error"] = str(e)
            score = 0
        
        return score, analysis
    
    def _calculate_ads_score(self, df: pd.DataFrame) -> Tuple[int, Dict]:
        """Скоринг рекламы с учетом ваших корректировок"""
        
        analysis = {
            "top_10_analysis": {},
            "top_100_analysis": {},
            "ratio_analysis": {},
            "organic_analysis": {},
            "score": 0
        }
        
        try:
            # Фильтруем топ-10 и топ-100 товары
            top_10 = df[df['Category position avg'] <= 10]
            top_100 = df[df['Category position avg'] <= 100]
            
            if len(top_10) == 0 or len(top_100) == 0:
                return 0, {"error": "Недостаточно товаров в топе для анализа"}
            
            # Анализ топ-10
            avg_cpm_top10 = top_10['Search cpm avg'].mean()
            avg_price_top10 = top_10['Final price'].mean()
            ratio_top10 = avg_price_top10 / avg_cmp_top10 if avg_cmp_top10 > 0 else 0
            
            analysis["top_10_analysis"] = {
                "avg_cpm": round(avg_cmp_top10, 2),
                "avg_price": round(avg_price_top10, 2),
                "price_to_cpm_ratio": round(ratio_top10, 2),
                "products_count": len(top_10)
            }
            
            # Анализ топ-100
            avg_cmp_top100 = top_100['Search cmp avg'].mean()
            avg_price_top100 = top_100['Final price'].mean()
            ratio_top100 = avg_price_top100 / avg_cmp_top100 if avg_cmp_top100 > 0 else 0
            
            analysis["top_100_analysis"] = {
                "avg_cpm": round(avg_cmp_top100, 2),
                "avg_price": round(avg_price_top100, 2),
                "price_to_cpm_ratio": round(ratio_top100, 2),
                "products_count": len(top_100)
            }
            
            # Скоринг по коэффициенту "Чек/Ставка"
            score_top10 = self._get_ratio_score(ratio_top10)
            score_top100 = self._get_ratio_score(ratio_top100)
            
            # Берем худший результат (как вы указали)
            final_score = min(score_top10, score_top100)
            
            analysis["ratio_analysis"] = {
                "score_top10": score_top10,
                "score_top100": score_top100,
                "final_score": final_score,
                "interpretation": self._get_ratio_interpretation(min(ratio_top10, ratio_top100))
            }
            
            # Анализ органических позиций
            organic_top10 = top_10[top_10['Search words in ads'] == 0]
            organic_top100 = top_100[top_100['Search words in ads'] == 0]
            
            organic_percent_top10 = len(organic_top10) / len(top_10) * 100 if len(top_10) > 0 else 0
            organic_percent_top100 = len(organic_top100) / len(top_100) * 100 if len(top_100) > 0 else 0
            
            analysis["organic_analysis"] = {
                "organic_top10_count": len(organic_top10),
                "organic_top100_count": len(organic_top100),
                "organic_percent_top10": round(organic_percent_top10, 2),
                "organic_percent_top100": round(organic_percent_top100, 2)
            }
            
            analysis["score"] = final_score
            
        except Exception as e:
            analysis["error"] = str(e)
            final_score = 0
        
        return final_score, analysis
    
    def _get_ratio_score(self, ratio: float) -> int:
        """Определение балла по коэффициенту Чек/Ставка"""
        if ratio >= ADS_THRESHOLDS["excellent"]:
            return 4
        elif ratio >= ADS_THRESHOLDS["good"]:
            return 3
        elif ratio >= ADS_THRESHOLDS["average"]:
            return 2
        elif ratio >= ADS_THRESHOLDS["poor"]:
            return 1
        else:
            return 0
    
    def _get_ratio_interpretation(self, ratio: float) -> str:
        """Интерпретация коэффициента Чек/Ставка"""
        if ratio >= 4.0:
            return "Очень выгодная ниша"
        elif ratio >= 3.0:
            return "Хорошая ниша"
        elif ratio >= 2.0:
            return "Средняя конкуренция"
        elif ratio >= 1.0:
            return "Высокая конкуренция"
        else:
            return "Перегретая ниша"
    
    def _get_niche_rating(self, total_score: int) -> str:
        """Определение общего рейтинга ниши"""
        for rating, (min_score, max_score) in TOTAL_SCORE_RANGES.items():
            if min_score <= total_score <= max_score:
                return rating
        return "poor"
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Генерация рекомендаций на основе скоринга"""
        recommendations = []
        
        # Рекомендации по общему баллу
        if results["total_score"] >= 16:
            recommendations.append("🟢 Отличная ниша для входа! Высокий потенциал роста.")
        elif results["total_score"] >= 11:
            recommendations.append("🟡 Хорошая ниша с умеренными рисками.")
        elif results["total_score"] >= 6:
            recommendations.append("🟠 Средняя ниша. Требуется детальный анализ конкурентов.")
        else:
            recommendations.append("🔴 Сложная ниша. Высокие риски входа.")
        
        # Специфические рекомендации по модулям
        if results["trend_score"] <= 2:
            recommendations.append("📉 Тренды показывают снижение. Рассмотрите альтернативные ниши.")
        
        if results["query_score"] >= 3:
            recommendations.append("🔍 Много эффективных запросов. Используйте их для SEO.")
        elif results["query_score"] <= 2:
            recommendations.append("🔍 Мало эффективных запросов. Конкуренция высокая.")
        
        if results["ads_score"] <= 2:
            recommendations.append("🎯 Высокие рекламные ставки относительно чека. Ниша может быть перегрета.")
        elif results["ads_score"] >= 3:
            recommendations.append("🎯 Умеренные рекламные ставки. Хорошие возможности для продвижения.")
        
        return recommendations
    
    def get_scores(self) -> Dict:
        """Получение результатов скоринга"""
        return self.scores
