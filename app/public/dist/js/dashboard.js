let income;
let expense;

window.onload = function () {
  const incomeSpan = document.getElementById("income");
  const incomeText = incomeSpan.innerText;
  expense = document.getElementById("expense");
  moneyFormat(incomeText, incomeSpan);
}

function moneyFormat(money, span) {
  const moneyFormat = new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
  });
  span.innerText = moneyFormat.format(money);
}