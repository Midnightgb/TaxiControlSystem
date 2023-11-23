let income;
let expense;

window.onload = function () {
  const incomeSpan = document.getElementById("income");
  const incomeText = incomeSpan.innerText;
  const expenseSpan = document.getElementById("expense");
  const expenseText = expense.innerText;
  
  moneyFormat(incomeText, incomeSpan);
  moneyFormat(expenseText, expenseSpan);
}

function moneyFormat(money, span) {
  const moneyFormat = new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
  });
  span.innerText = moneyFormat.format(money);
}