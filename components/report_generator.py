import streamlit as st
import pandas as pd
from typing import Dict, Any
from datetime import datetime


class ReportGenerator:
    """Компонент для генерации отчетов"""
    
    def __init__(self):
        pass
    
    def generate_summary_report(self, scoring_results: Dict, analysis_results: Dict = None) -> str:
        """Генерация краткого отчета"""
        
        total_score = scoring_results.get('total_score', 0)
        niche_rating = scoring_results.get('niche_rating', 'poor')
        
        report = f"""
# 📊 Отчет анализа ниши MPStats

**Дата:** {datetime.now().strftime('%d.%m.%Y %H:%M')}

## 🎯 Основные результаты
- **Общий скоринг:** {total_score}/20 баллов
- **Рейтинг ниши:** {niche_rating.title()}

## 📊 Детальный скоринг
- Анализ трендов: {scoring_results.get('trend_score', 0)}/4
- Анализ запросов: {scoring_results.get('query_score', 0)}/4
- Ценовая сегментация: {scoring_results.get('price_score', 0)}/4
- Анализ остатков: {scoring_results.get('stock_score', 0)}/4
- Рекламный анализ: {scoring_results.get('ads_score', 0)}/4

## 💡 Рекомендации
"""
        
        recommendations = scoring_results.get('recommendations', [])
        for i, rec in enumerate(recommendations, 1):
            report += f"{i}. {rec}\n"
        
        return report
    
    def render_export_controls(self, scoring_results: Dict, analysis_results: Dict = None):
        """Элементы управления экспортом"""
        
        st.subheader("📤 Экспорт результатов")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Скачать текстовый отчет", use_container_width=True):
                report_text = self.generate_summary_report(scoring_results, analysis_results)
                
                st.download_button(
                    label="💾 Сохранить отчет",
                    data=report_text,
                    file_name=f"mpstats_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
        
        with col2:
            if st.button("📊 Создать Excel отчет", use_container_width=True):
                try:
                    excel_data = self.create_excel_report(scoring_results, analysis_results)
                    st.success("✅ Excel отчет готов к скачиванию")
                except Exception as e:
                    st.error(f"❌ Ошибка при создании Excel: {e}")
    
    def create_excel_report(self, scoring_results: Dict, analysis_results: Dict = None) -> bytes:
        """Создание Excel отчета"""
        
        # Создаем DataFrame с результатами
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
        
        df = pd.DataFrame(summary_data)
        
        # Возвращаем как bytes для скачивания
        return df.to_excel(index=False)
    
    def render_detailed_results(self, analysis_results: Dict):
        """Отображение детальных результатов"""
        
        if not analysis_results:
            st.info("Нет детальных результатов для отображения")
            return
        
        st.subheader("📋 Детальные результаты анализа")
        
        for module_name, module_data in analysis_results.items():
            with st.expander(f"📊 {module_name.title()}"):
                
                if isinstance(module_data, dict):
                    # Отображаем основные метрики
                    if 'summary' in module_data:
                        summary = module_data['summary']
                        
                        # Создаем таблицу метрик
                        metrics_data = []
                        for key, value in summary.items():
                            metrics_data.append({
                                'Метрика': key.replace('_', ' ').title(),
                                'Значение': str(value)
                            })
                        
                        if metrics_data:
                            st.dataframe(pd.DataFrame(metrics_data), use_container_width=True)
                    
                    # Отображаем другие данные
                    for key, value in module_data.items():
                        if key not in ['summary', 'charts'] and not key.startswith('_'):
                            st.write(f"**{key.replace('_', ' ').title()}:** {value}")
                
                else:
                    st.write(str(module_data))
