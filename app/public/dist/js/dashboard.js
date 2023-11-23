var ingresos = [];
var gastos = [];
var meses = [];

for (var month in reports.data) {
  if (reports.data.hasOwnProperty(month)) {
    ingresos.push(reports.data[month].income);
    gastos.push(reports.data[month].expenses);
    assignMonth(month);
  }
}

console.log("hola");

function assignMonth(month) {
  switch (month) {
    case '1':
      meses.push('Ene');
      break;
    case '2':
      meses.push('Feb');
      break;
    case '3':
      meses.push('Mar');
      break;
    case '4':
      meses.push('Abr');
      break;
    case '5':
      meses.push('May');
      break;
    case '6':
      meses.push('Jun');
      break;
    case '7':
      meses.push('Jul');
      break;
    case '8':
      meses.push('Ago');
      break;
    case '9':
      meses.push('Sept');
      break;
    case '10':
      meses.push('Oct');
      break;
    case '11':
      meses.push('Nov');
      break;
    case '12':
      meses.push('Dic');
      break;
    default:
      break;
  }
}

console.table(reports.data);

var options = {
  chart: {
    type: 'line'
  },
  toolbar: {
    show: true,
    tools: {
      download: true,
      selection: false,
      zoom: false,
      zoomin: false,
      zoomout: false,
      pan: false,
      reset: false
    },
  },
  series: [{
    name: 'Ingresos',
    data: ingresos
  }, {
    name: 'Gastos',
    data: gastos
  }],
  xaxis: {
    categories: meses
  },
  stroke: {
    curve: 'smooth'
  },
  colors: ['#00E396', '#FF4560'],
  noData: {
    text: 'No hay datos disponibles',
    align: 'center',
    verticalAlign: 'middle',
    offsetX: 0,
    offsetY: 0,
    style: {
      color: undefined,
      fontSize: '14px',
      fontFamily: undefined
    }
  }
}

var chart = new ApexCharts(document.querySelector("#chart"), options);

chart.render();