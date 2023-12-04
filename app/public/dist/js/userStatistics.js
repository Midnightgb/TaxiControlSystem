document.addEventListener("DOMContentLoaded", function () {
    const currentIncomeElement = document.getElementById("current");
    const pastIncomeElement = document.getElementById("past");
    const chartMonthlyIncomeElement = document.getElementById("chartMonthlyIncome");

    if (currentIncomeElement && pastIncomeElement) {
        const currentIncome = currentIncomeElement.innerText;
        const currentIncomeValue = parseFloat(currentIncome.replace(/[^\d.-]/g, '')) || 0;

        const pastIncome = pastIncomeElement.innerText;
        const pastIncomeValue = parseFloat(pastIncome.replace(/[^\d.-]/g, '')) || 0;

        let options = {
            chart: {
                type: 'donut',
                height: 800,
                width: 489,
            },
            labels: ['Mes Actual', 'Mes Anterior'],
            series: [currentIncomeValue, pastIncomeValue],
            colors: ['#787aeb', '#00ebff'],
            responsive: [{
                breakpoint: 480,
                options: {
                    chart: {
                        width: 300,
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }],
            tooltip: {
                y: {
                    formatter: function (value) {
                        return "$ " + Math.round(value).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ","); // Formato de moneda sin decimales
                    }
                },
                style: {
                    fontSize: '16px',
                    textAlign: 'center',
                },
            },
            dataLabels: {
                enabled: false
            }
        };

        var chart = new ApexCharts(chartMonthlyIncomeElement, options);
        chart.render();

        // Verificar si ambos valores son cero y cambiar el contenido de la tabla
        if (currentIncomeValue == 0 && pastIncomeValue == 0) {
            chartMonthlyIncomeElement.innerHTML = `
                <div style="text-align: center; width: 400px; height: 400px; position: relative; left: 50%; transform: translateX(-50%); top: 30%; ">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"
                        class="h-12 w-12 mx-auto mb-4 text-gray-400">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                    <p class="text-gray-400">No hay datos disponibles</p>
                </div>
            `;
        }

    } else {
        console.log("No se encontraron los elementos");
    }
});
