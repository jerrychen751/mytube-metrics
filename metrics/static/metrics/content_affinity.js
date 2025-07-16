document.addEventListener('DOMContentLoaded', function() {
    function renderPlotlyChart(chartId, dataId) {
        const chartDiv = document.getElementById(chartId);
        const chartDataElement = document.getElementById(dataId);

        if (!chartDiv || !chartDataElement) {
            return;
        }

        const figure = JSON.parse(chartDataElement.textContent);
        if (figure && figure.data && figure.data.length > 0) {
            Plotly.newPlot(chartId, figure.data, figure.layout, { responsive: true });
        }
    }

    renderPlotlyChart('topicFreqChart', 'topic-chart-data');
    renderPlotlyChart('categoryFreqChart', 'category-chart-data');

    const expandBtn = document.getElementById('expandTopicChartBtn');
    const topicChartContainer = document.getElementById('topicChartContainer');

    if (expandBtn && topicChartContainer) {
        // Check if the chart is taller than the container
        const chartDiv = document.getElementById('topicFreqChart');
        if (chartDiv.clientHeight <= topicChartContainer.clientHeight) {
            expandBtn.style.display = 'none';
            topicChartContainer.classList.add('is-expanded');
        }

        expandBtn.addEventListener('click', function() {
            topicChartContainer.classList.add('is-expanded');
            this.style.display = 'none';
        });
    }
});
