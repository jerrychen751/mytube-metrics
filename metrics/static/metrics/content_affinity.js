document.addEventListener('DOMContentLoaded', function() {
    function renderPlotlyChart(chartId, dataId) {
        const chartDataElement = document.getElementById(dataId);
        if (!chartDataElement) {
            console.error('Chart data element not found:', dataId);
            return;
        }

        const figure = JSON.parse(chartDataElement.textContent);
        if (figure) {
            Plotly.newPlot(chartId, figure.data, figure.layout, { responsive: true });
        }
    }

    renderPlotlyChart('topicFreqChart', 'topic-chart-data');
    renderPlotlyChart('categoryFreqChart', 'category-chart-data');
});
