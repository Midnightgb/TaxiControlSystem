document.addEventListener("DOMContentLoaded", function () {
    // Obtener los valores del HTML
    var currentIncome = parseFloat(document.getElementById('current').innerText.replace('$', '').replace(',', ''));
    var pastIncome = parseFloat(document.getElementById('past').innerText.replace('$', '').replace(',', ''));

    // Obtener el contexto del lienzo
    var ctx = document.getElementById('chartMonthlyIncome').getContext('2d');

    // Crear el gráfico circular
    var myChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Mes Actual', 'Mes Anterior'],
            datasets: [{
                data: [currentIncome, pastIncome],
                backgroundColor: ['#65d4f3', '#6577F3'],
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            legend: {
                position: 'bottom',
            },
        }
    });
});
