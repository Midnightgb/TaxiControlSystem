document.addEventListener("DOMContentLoaded", function () {
    var currentIncome = document.getElementById("current").innerText;
    var currentIncomeValue = parseFloat(currentIncome.replace(/[^\d.-]/g, '')); 
    console.log(currentIncomeValue);
    var pastIncome = document.getElementById("past").innerText;
    var pastIncomeValue = parseFloat(pastIncome.replace(/[^\d.-]/g, '')); 
    console.log(pastIncomeValue);

    var ctx = document.getElementById('chartMonthlyIncome').getContext('2d');

    var myChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            
            datasets: [{
                data: [currentIncomeValue, pastIncomeValue],
                backgroundColor: ['#65d4f3', '#6577F3'],
            }],
            labels: ['Mes Actual', 'Mes Anterior'],
            
        },
        
        options: {
            responsive: true,
            maintainAspectRatio: false,
            legend: {
                position: 'bottom',
            },
        }
    });
    console.log(currentIncome);
        console.log(pastIncome);
});
