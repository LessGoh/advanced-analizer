import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from .helpers import format_number, format_currency, format_percentage


class DataFormatter:
    """Класс для форматирования данных"""
    
    def __init__(self, decimal_places: int = 2):
        self.decimal_places = decimal_places
    
    def format_dataframe(self, df: pd.DataFrame, column_formats: Dict[str, str] = None) -> pd.DataFrame:
        """
        Форматирование всего датафрейма
        
        Args:
            df: Исходный датафрейм
            column_formats: Словарь с форматами для колонок
        
        Returns:
            Отформатированный датафрейм
        """
        df_formatted = df.copy()
        
        if column_formats is None:
            column_formats = self._detect_column_formats(df)
        
        for column, format_type in column_formats.items():
            if column in df_formatted.columns:
                df_formatted[column] = self._format_column(df_formatted[column], format_type)
        
        return df_formatted
    
    def _detect_column_formats(self, df: pd.DataFrame) -> Dict[str, str]:
        """Автоматическое определение форматов колонок"""
        formats = {}
        
        for column in df.columns:
            column_lower = column.lower()
            
            if any(word in column_lower for word in ['цена', 'выручка', 'стоимость', 'revenue', 'price', '₽']):
                formats[column] = 'currency'
            elif any(word in column_lower for word in ['процент', 'percent', '%']):
                formats[column] = 'percentage'
            elif any(word in column_lower for word in ['дата', 'date', 'месяц']):
                formats[column] = 'date'
            elif df[column].dtype in ['int64', 'float64']:
                # Проверяем, похоже ли на большие числа (количество, объемы)
                if df[column].max() > 1000:
                    formats[column] = 'number'
                else:
                    formats[column] = 'decimal'
            else:
                formats[column] = 'text'
        
        return formats
    
    def _format_column(self, series: pd.Series, format_type: str) -> pd.Series:
        """Форматирование отдельной колонки"""
        
        if format_type == 'currency':
            return series.apply(lambda x: format_currency(x, decimal_places=0))
        elif format_type == 'percentage':
            return series.apply(lambda x: format_percentage(x, decimal_places=1))
        elif format_type == 'number':
            return series.apply(lambda x: format_number(x, decimal_places=0))
        elif format_type == 'decimal':
            return series.apply(lambda x: format_number(x, decimal_places=self.decimal_places))
        elif format_type == 'date':
            return pd.to_datetime(series, errors='coerce').dt.strftime('%Y-%m-%d')
        else:
            return series.astype(str)
    
    def format_metrics_dict(self, metrics: Dict[str, Any]) -> Dict[str, str]:
        """Форматирование словаря метрик"""
        formatted = {}
        
        for key, value in metrics.items():
            key_lower = key.lower()
            
            if any(word in key_lower for word in ['price', 'revenue', 'cost', 'цена', 'выручка', 'стоимость']):
                formatted[key] = format_currency(value)
            elif any(word in key_lower for word in ['percent', 'ratio', 'rate', 'процент']):
                formatted[key] = format_percentage(value)
            elif isinstance(value, (int, float)):
                formatted[key] = format_number(value)
            else:
                formatted[key] = str(value)
        
        return formatted
    
    def create_summary_table(self, data: Dict[str, Any], title: str = "Сводка") -> pd.DataFrame:
        """Создание сводной таблицы из словаря"""
        
        summary_data = []
        for key, value in data.items():
            # Красивое название метрики
            display_name = self._beautify_metric_name(key)
            
            # Форматированное значение
            if isinstance(value, dict):
                formatted_value = str(value)  # Для сложных объектов
            else:
                formatted_value = self._format_single_value(key, value)
            
            summary_data.append({
                "Метрика": display_name,
                "Значение": formatted_value
            })
        
        return pd.DataFrame(summary_data)
    
    def _beautify_metric_name(self, key: str) -> str:
        """Преобразование ключа в читаемое название"""
        
        name_mapping = {
            'total_score': 'Общий балл',
            'niche_rating': 'Рейтинг ниши',
            'trend_score': 'Скоринг трендов',
            'query_score': 'Скоринг запросов',
            'price_score': 'Скоринг цен',
            'stock_score': 'Скоринг остатков',
            'ads_score': 'Скоринг рекламы',
            'avg_cpm': 'Средняя ставка',
            'avg_price': 'Средняя цена',
            'total_products': 'Всего товаров',
            'effective_queries': 'Эффективных запросов',
            'stockout_percentage': 'Процент дефицитов',
            'revenue_per_product': 'Выручка на товар'
        }
        
        return name_mapping.get(key, key.replace('_', ' ').title())
    
    def _format_single_value(self, key: str, value: Any) -> str:
        """Форматирование одного значения на основе ключа"""
        
        if pd.isna(value) or value is None:
            return "N/A"
        
        key_lower = key.lower()
        
        if any(word in key_lower for word in ['price', 'revenue', 'cost', 'cpm', 'цена', 'выручка']):
            return format_currency(value)
        elif any(word in key_lower for word in ['percent', 'ratio', 'rate', 'процент']):
            return format_percentage(value)
        elif isinstance(value, (int, float)):
            return format_number(value)
        else:
            return str(value)


class ChartFormatter:
    """Класс для форматирования графиков"""
    
    def __init__(self):
        self.default_colors = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
        
        self.chart_template = {
            'layout': {
                'font': {'family': 'Arial, sans-serif', 'size': 12},
                'plot_bgcolor': 'rgba(0,0,0,0)',
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'margin': {'l': 40, 'r': 40, 't': 60, 'b': 40}
            }
        }
    
    def apply_theme(self, fig: go.Figure, theme: str = "modern") -> go.Figure:
        """Применение темы к графику"""
        
        if theme == "modern":
            fig.update_layout(
                font=dict(family="Arial, sans-serif", size=12, color="#333"),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=50, r=50, t=60, b=50),
                showlegend=True,
                legend=dict(
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="rgba(0,0,0,0.2)",
                    borderwidth=1
                )
            )
            
            # Стилизация осей
            fig.update_xaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.2)',
                showline=True,
                linewidth=1,
                linecolor='rgba(128,128,128,0.5)'
            )
            
            fig.update_yaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.2)',
                showline=True,
                linewidth=1,
                linecolor='rgba(128,128,128,0.5)'
            )
        
        elif theme == "dark":
            fig.update_layout(
                font=dict(family="Arial, sans-serif", size=12, color="#fff"),
                plot_bgcolor='rgba(30,30,30,1)',
                paper_bgcolor='rgba(20,20,20,1)',
                margin=dict(l=50, r=50, t=60, b=50)
            )
            
            fig.update_xaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.3)',
                color='#fff'
            )
            
            fig.update_yaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.3)',
                color='#fff'
            )
        
        return fig
    
    def format_axis_labels(self, fig: go.Figure, x_format: str = None, y_format: str = None) -> go.Figure:
        """Форматирование подписей осей"""
        
        if x_format == 'currency':
            fig.update_xaxes(tickformat=',.0f')
        elif x_format == 'percentage':
            fig.update_xaxes(tickformat='.1%')
        elif x_format == 'date':
            fig.update_xaxes(tickformat='%Y-%m')
        
        if y_format == 'currency':
            fig.update_yaxes(tickformat=',.0f')
        elif y_format == 'percentage':
            fig.update_yaxes(tickformat='.1%')
        elif y_format == 'number':
            fig.update_yaxes(tickformat=',.0f')
        
        return fig
    
    def add_value_labels(self, fig: go.Figure, format_type: str = 'number') -> go.Figure:
        """Добавление подписей значений на график"""
        
        for trace in fig.data:
            if hasattr(trace, 'y') and trace.y is not None:
                if format_type == 'currency':
                    texttemplate = '%{y:,.0f} ₽'
                elif format_type == 'percentage':
                    texttemplate = '%{y:.1f}%'
                else:
                    texttemplate = '%{y:,.0f}'
                
                trace.update(texttemplate=texttemplate, textposition="outside")
        
        return fig
    
    def create_color_scale(self, values: List[float], color_scheme: str = 'RdYlGn') -> List[str]:
        """Создание цветовой шкалы для значений"""
        
        if not values:
            return []
        
        min_val, max_val = min(values), max(values)
        
        if color_scheme == 'RdYlGn':
            # Красный-Желтый-Зеленый (плохо-средне-хорошо)
            colors = []
            for val in values:
                if min_val == max_val:
                    normalized = 0.5
                else:
                    normalized = (val - min_val) / (max_val - min_val)
                
                if normalized < 0.33:
                    colors.append('#d62728')  # Красный
                elif normalized < 0.67:
                    colors.append('#ff7f0e')  # Оранжевый
                else:
                    colors.append('#2ca02c')  # Зеленый
            
            return colors
        
        elif color_scheme == 'Blues':
            # Градиент синего
            colors = []
            for val in values:
                if min_val == max_val:
                    intensity = 0.5
                else:
                    intensity = (val - min_val) / (max_val - min_val)
                
                # От светло-синего к темно-синему
                r = int(255 - (255 - 31) * intensity)
                g = int(255 - (255 - 119) * intensity)
                b = int(255 - (255 - 180) * intensity)
                
                colors.append(f'rgb({r},{g},{b})')
            
            return colors
        
        else:
            # Возвращаем стандартную палитру
            return self.default_colors[:len(values)]


class ReportFormatter:
    """Класс для форматирования отчетов"""
    
    def __init__(self):
        self.data_formatter = DataFormatter()
    
    def generate_executive_summary(self, scoring_results: Dict, analysis_results: Dict = None) -> str:
        """Генерация краткой сводки для руководства"""
        
        total_score = scoring_results.get('total_score', 0)
        niche_rating = scoring_results.get('niche_rating', 'poor')
        
        # Определяем рекомендацию
        if total_score >= 16:
            recommendation = "🟢 **Рекомендация: ВХОДИТЬ В НИШУ**"
            risk_level = "Низкий риск"
        elif total_score >= 11:
            recommendation = "🟡 **Рекомендация: ВХОДИТЬ С ОСТОРОЖНОСТЬЮ**"
            risk_level = "Средний риск"
        elif total_score >= 6:
            recommendation = "🟠 **Рекомендация: ТРЕБУЕТСЯ ДЕТАЛЬНЫЙ АНАЛИЗ**"
            risk_level = "Высокий риск"
        else:
            recommendation = "🔴 **Рекомендация: НЕ ВХОДИТЬ В НИШУ**"
            risk_level = "Очень высокий риск"
        
        summary = f"""
## 📋 Краткая сводка анализа ниши

### 🎯 Основные результаты
- **Общий скоринг:** {total_score}/20 баллов
- **Рейтинг ниши:** {niche_rating.title()}
- **Уровень риска:** {risk_level}

{recommendation}

### 📊 Детальный скоринг
- Анализ трендов: {scoring_results.get('trend_score', 0)}/4
- Анализ запросов: {scoring_results.get('query_score', 0)}/4
- Ценовая сегментация: {scoring_results.get('price_score', 0)}/4
- Анализ остатков: {scoring_results.get('stock_score', 0)}/4
- Рекламный анализ: {scoring_results.get('ads_score', 0)}/4

### 💡 Ключевые инсайты
"""
        
        # Добавляем рекомендации из результатов
        recommendations = scoring_results.get('recommendations', [])
        for i, rec in enumerate(recommendations[:3], 1):
            summary += f"{i}. {rec}\n"
        
        return summary
    
    def create_detailed_report(self, scoring_results: Dict, analysis_results: Dict) -> str:
        """Создание детального отчета"""
        
        report = f"""
# 📊 Детальный анализ ниши MPStats

**Дата анализа:** {datetime.now().strftime('%d.%m.%Y %H:%M')}

{self.generate_executive_summary(scoring_results, analysis_results)}

---

## 📈 Анализ трендов
"""
        
        if 'trends' in analysis_results:
            trends_data = analysis_results['trends']
            
            # Пиковые месяцы
            if 'peak_months_by_year' in trends_data:
                report += "\n### 🔥 Пиковые месяцы продаж\n"
                for year, data in trends_data['peak_months_by_year'].items():
                    report += f"- **{year}:** {data.get('month_name', 'N/A')} ({data.get('sales', 0):,.0f} продаж)\n"
            
            # YoY динамика
            if 'yoy_changes' in trends_data:
                report += "\n### 📊 Динамика год к году\n"
                for metric, data in trends_data['yoy_changes'].items():
                    if isinstance(data, dict) and 'avg_yoy_change' in data:
                        change = data['avg_yoy_change']
                        trend_icon = "📈" if change > 0 else "📉" if change < -5 else "➡️"
                        report += f"- {metric.replace('_', ' ').title()}: {trend_icon} {change:+.1f}%\n"
        
        report += "\n---\n"
        
        # Анализ запросов
        if 'queries' in analysis_results:
            queries_data = analysis_results['queries']
            report += f"""
## 🔍 Анализ поисковых запросов

- **Всего запросов:** {queries_data.get('total_queries', 0):,}
- **Эффективных запросов:** {queries_data.get('effective_queries', 0):,}
- **Процент эффективности:** {queries_data.get('efficiency_ratio', 0):.1f}%

### 🎯 Топ возможности
"""
            
            top_opportunities = queries_data.get('top_opportunities', [])
            for i, opp in enumerate(top_opportunities[:5], 1):
                keyword = opp.get('Ключевое слово', 'N/A')
                frequency = opp.get('Частота WB', 0)
                products = opp.get('Товаров в запросе', 0)
                ratio = opp.get('Коэффициент_спрос_предложение', 0)
                report += f"{i}. **{keyword}** - частота: {frequency:,}, товаров: {products}, коэффициент: {ratio:.1f}\n"
        
        report += "\n---\n"
        
        # Ценовая сегментация
        if 'price' in analysis_results:
            price_data = analysis_results['price']
            best_segment = price_data.get('best_segment', {})
            
            report += f"""
## 💰 Ценовая сегментация

### 🏆 Лучший ценовой сегмент
- **Диапазон:** {best_segment.get('price_range', 'N/A')}
- **Выручка на товар:** {format_currency(best_segment.get('revenue_per_product', 0))}
- **Количество продавцов:** {best_segment.get('sellers', 0)}
- **Количество товаров:** {best_segment.get('products', 0)}
"""
        
        report += "\n---\n"
        
        # Рекламный анализ
        if 'ads' in analysis_results:
            ads_data = analysis_results['ads']
            
            report += f"""
## 🎯 Рекламный анализ

### 📊 Анализ ТОП сегментов
- **Средняя ставка ТОП-10:** {format_currency(ads_data.get('avg_cpm_top10', 0))}
- **Средняя ставка ТОП-100:** {format_currency(ads_data.get('avg_cmp_top100', 0))}
- **Коэффициент Чек/Ставка ТОП-10:** {ads_data.get('avg_ratio_top10', 0):.1f}
- **Коэффициент Чек/Ставка ТОП-100:** {ads_data.get('avg_ratio_top100', 0):.1f}

### 🌡️ Температура ниши
"""
            
            niche_assessment = ads_data.get('niche_assessment', {})
            status = niche_assessment.get('niche_status', 'Неизвестно')
            heat_level = niche_assessment.get('heat_level', 3)
            
            heat_emoji = "🟢" if heat_level <= 2 else "🟡" if heat_level == 3 else "🔴"
            report += f"{heat_emoji} **{status}** (уровень {heat_level}/5)\n"
        
        report += f"""

---

## 🎯 Заключение и рекомендации

### 📋 Итоговый скоринг: {scoring_results.get('total_score', 0)}/20 баллов

### 💡 Основные рекомендации:
"""
        
        recommendations = scoring_results.get('recommendations', [])
        for i, rec in enumerate(recommendations, 1):
            report += f"{i}. {rec}\n"
        
        report += f"""

---

*Отчет сгенерирован автоматически с помощью MPStats Analyzer*
"""
        
        return report
    
    def export_to_excel(self, scoring_results: Dict, analysis_results: Dict, filename: str = None) -> str:
        """Экспорт результатов в Excel"""
        
        if filename is None:
            filename = f"mpstats_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            
            # Лист 1: Общая сводка
            summary_data = {
                'Метрика': [
                    'Общий скоринг',
                    'Рейтинг ниши',
                    'Анализ трендов',
                    'Анализ запросов',
                    'Ценовая сегментация',
                    'Анализ остатков',
                    'Рекламный анализ'
                ],
                'Значение': [
                    f"{scoring_results.get('total_score', 0)}/20",
                    scoring_results.get('niche_rating', 'poor').title(),
                    f"{scoring_results.get('trend_score', 0)}/4",
                    f"{scoring_results.get('query_score', 0)}/4",
                    f"{scoring_results.get('price_score', 0)}/4",
                    f"{scoring_results.get('stock_score', 0)}/4",
                    f"{scoring_results.get('ads_score', 0)}/4"
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Общая сводка', index=False)
            
            # Лист 2: Рекомендации
            if scoring_results.get('recommendations'):
                recommendations_df = pd.DataFrame({
                    'Рекомендация': scoring_results['recommendations']
                })
                recommendations_df.to_excel(writer, sheet_name='Рекомендации', index=False)
            
            # Листы с детальными данными
            for module_name, module_data in analysis_results.items():
                if isinstance(module_data, dict):
                    try:
                        # Пытаемся преобразовать в DataFrame
                        if 'summary' in module_data:
                            module_df = pd.DataFrame([module_data['summary']])
                            sheet_name = module_name.title()[:31]  # Ограничение Excel
                            module_df.to_excel(writer, sheet_name=sheet_name, index=False)
                    except:
                        continue
        
        return filename
    
    def format_comparison_table(self, current_results: Dict, previous_results: Dict) -> pd.DataFrame:
        """Создание таблицы сравнения результатов"""
        
        metrics = [
            ('Общий скоринг', 'total_score'),
            ('Анализ трендов', 'trend_score'),
            ('Анализ запросов', 'query_score'),
            ('Ценовая сегментация', 'price_score'),
            ('Анализ остатков', 'stock_score'),
            ('Рекламный анализ', 'ads_score')
        ]
        
        comparison_data = []
        
        for metric_name, metric_key in metrics:
            current_val = current_results.get(metric_key, 0)
            previous_val = previous_results.get(metric_key, 0)
            change = current_val - previous_val
            change_pct = (change / previous_val * 100) if previous_val > 0 else 0
            
            comparison_data.append({
                'Метрика': metric_name,
                'Текущее значение': current_val,
                'Предыдущее значение': previous_val,
                'Изменение': change,
                'Изменение %': f"{change_pct:+.1f}%"
            })
        
        return pd.DataFrame(comparison_data)
