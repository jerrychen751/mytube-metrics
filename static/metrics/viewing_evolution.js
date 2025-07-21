document.addEventListener('DOMContentLoaded', function () {
    const chartDataElement = document.getElementById('chart-data');
    if (chartDataElement) {
        try {
            const chartData = JSON.parse(chartDataElement.textContent);
            if (chartData && chartData.data && chartData.layout) {
                Plotly.newPlot('viewingEvolutionChart', chartData.data, chartData.layout);
            }
        } catch (e) {
            console.error("Error parsing chart data:", e);
        }
    }

    const dailyChartDataElement = document.getElementById('daily-chart-data');
    if (dailyChartDataElement) {
        try {
            const dailyChartData = JSON.parse(dailyChartDataElement.textContent);
            if (dailyChartData && dailyChartData.data && dailyChartData.layout) {
                Plotly.newPlot('dailyWatchFreqChart', dailyChartData.data, dailyChartData.layout);
            }
        } catch (e) {
            console.error("Error parsing daily chart data:", e);
        }
    }
});