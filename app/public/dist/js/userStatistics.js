document.addEventListener("DOMContentLoaded", function () {
    const currentIncomeElement = document.getElementById("current");
    const pastIncomeElement = document.getElementById("past");

    if (currentIncomeElement && pastIncomeElement) {
        const currentIncome = currentIncomeElement.innerText;
        const currentIncomeValue = parseFloat(currentIncome.replace(/[^\d.-]/g, '')) || 0;
        console.log(currentIncomeValue);

        const pastIncome = pastIncomeElement.innerText;
        const pastIncomeValue = parseFloat(pastIncome.replace(/[^\d.-]/g, '')) || 0;
        console.log(pastIncomeValue);

        const ctx = document.getElementById('chartMonthlyIncome').getContext('2d');

        let backgroundColor = ['#787aeb', '#00ebff'];
        
        const myChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [currentIncomeValue, pastIncomeValue],
                    backgroundColor: backgroundColor,
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

        if (currentIncomeValue == 0 && pastIncomeValue == 0) {
            document.getElementById("chartMonthlyIncome").style.display = "none";
            document.getElementById("noData").style.display = "block";
        }

    } else {
        console.log("No se encontraron los elementos");
    }
});
