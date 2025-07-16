document.addEventListener('DOMContentLoaded', function() {
    function renderPlotlyChart(chartId, dataId) {
        const chartDiv = document.getElementById(chartId);
        const chartDataElement = document.getElementById(dataId);

        if (!chartDiv || !chartDataElement) {
            return Promise.resolve(); // Return a resolved promise if chart can't be rendered
        }

        const figure = JSON.parse(chartDataElement.textContent);
        if (figure && figure.data && figure.data.length > 0) {
            return Plotly.newPlot(chartId, figure.data, figure.layout, { responsive: true });
        }
        return Promise.resolve();
    }

    // Render the topic chart and then check its height
    renderPlotlyChart('topicFreqChart', 'topic-chart-data').then(function() {
        const expandBtn = document.getElementById('expandTopicChartBtn');
        const topicChartContainer = document.getElementById('topicChartContainer');
        const chartDiv = document.getElementById('topicFreqChart');

        if (expandBtn && topicChartContainer && chartDiv) {
            const isOverflowing = chartDiv.clientHeight > topicChartContainer.clientHeight;

            if (isOverflowing) {
                expandBtn.style.display = 'block';
                expandBtn.textContent = 'Show More';
            } else {
                expandBtn.style.display = 'none';
                topicChartContainer.classList.add('is-expanded'); // Show full chart if not overflowing
            }

            expandBtn.addEventListener('click', function() {
                const isExpanded = topicChartContainer.classList.toggle('is-expanded');
                this.textContent = isExpanded ? 'Show Less' : 'Show More';

                if (!isExpanded) {
                    topicChartContainer.scrollIntoView({ behavior: 'smooth' });
                }
            });
        }
    });

    // Render the category chart (it doesn't need special handling)
    renderPlotlyChart('categoryFreqChart', 'category-chart-data');
});
