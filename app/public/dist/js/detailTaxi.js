// Al cargar la página, recuperar el valor de 'bandera' del sessionStorage
let bandera = sessionStorage.getItem('bandera') || 0;
console.log("bandera:", bandera);

let bandera_2 = sessionStorage.getItem('bandera_2') || 0;
console.log("bandera:", bandera_2);


var diasSemana = [];
    var pagosDiarios = [];

    var weekdays = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"];

    for (var day in reports_week) {
        if (reports_week.hasOwnProperty(day)) {
            // Obtener el nombre del día de la semana correspondiente
            var date = new Date(day);
            var dayOfWeek = weekdays[date.getDay()];

            diasSemana.push(dayOfWeek);
            pagosDiarios.push(reports_week[day]);
        }
    }

    var chartOptionsWeek = {
        chart: {
            type: "bar"
        },
        series: [{
            name: "Pagos Diarios",
            data: pagosDiarios
        }],
        xaxis: {
            categories: diasSemana
        },
        yaxis: {
            labels: {
                formatter: function (val) {
                    return '$' + val.toFixed(0).replace(/(\d)(?=(\d{3})+$)/g, '$1,');
                }
            }
        },
        colors: ['#787aeb', '#6577F3', '#65d4f3', '#6577F3', '#65d4f3', '#6577F3', '#65d4f3'],
        dataLabels: {
            enabled: true,
            formatter: function (val) {
                return '$' + val.toFixed(0).replace(/(\d)(?=(\d{3})+$)/g, '$1,');
            },
            offsetY: -20,
            style: {
                fontSize: '12px',
                colors: ["#304758"]
            }
        }
    };

    var chartWeek = new ApexCharts(document.getElementById("chartWeek"), chartOptionsWeek);
    chartWeek.render();

document.addEventListener("DOMContentLoaded", function () {
    const openModalButton = document.getElementById("openModalButton");
    const closeModalButton = document.getElementById("closeModalButton");

    const openModalButton2 = document.getElementById("openModalButton2");
    const closeModalButton2 = document.getElementById("closeModalButton2");

    const modal = document.getElementById("myModal");
    const modal2 = document.getElementById("myModal2");

    openModalButton.addEventListener("click", function () {
        modal.classList.remove("hidden");
    });

    closeModalButton.addEventListener("click", function () {
        modal.classList.add("hidden");
    });

    openModalButton2.addEventListener("click", function () {
        modal2.classList.remove("hidden");
    });

    closeModalButton2.addEventListener("click", function () {
        modal2.classList.add("hidden");
    });

    const form = document.getElementById("updateUserForm");

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const formData = new FormData(form);

        try {
            const response = await fetch(form.action, {
                method: "POST",
                body: formData,
            });

            console.log("Respuesta del servidor:", response.ok);

            if (response.ok) {
                modal.classList.add("hidden");

                sessionStorage.setItem('bandera', '1');

                // Recargar la página después de un breve retraso
                setTimeout(function () {
                    location.reload();
                }, 500);
            } else {
                sessionStorage.setItem('bandera', '2');
            }

        } catch (error) {
            console.error("Error al enviar la solicitud:", error);
        }
    });

    console.log("bandera CON LA SESION SETEADA :", bandera);


    const form2 = document.getElementById("updateTaxiForm");

    form2.addEventListener("submit", async function (event) {
        event.preventDefault();

        const formData = new FormData(form2);

        try {
            const response = await fetch(form2.action, {
                method: "POST",
                body: formData,
            });

            console.log("Respuesta del servidor:", response.ok);

            if (response.ok) {
                modal2.classList.add("hidden");

                sessionStorage.setItem('bandera_2', '1');

                // Recargar la página después de un breve retraso
                setTimeout(function () {
                    location.reload();
                }, 500);
            } else {
                sessionStorage.setItem('bandera_2', '2');
            }

        } catch (error) {
            console.error("Error al enviar la solicitud:", error);
        }
    });

    console.log("bandera_2 CON LA SESION SETEADA :", bandera_2);



});

// Ejecutar las alertas después de que la página se ha recargado
window.onload = function () {
    const bandera = sessionStorage.getItem('bandera');
    const bandera_2 = sessionStorage.getItem('bandera_2');

    if (bandera == 1) {
        Swal.fire({
            icon: 'success',
            title: 'Usuario Actualizado',
            showConfirmButton: false,
            timer: 1500,
            didClose: () => {
                sessionStorage.setItem('bandera', '0');
            }
        });
    } else if (bandera == 2) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Algo salió mal!',
            didClose: () => {
                sessionStorage.setItem('bandera', '0');
            }
        });
    }

    if (bandera_2 == 1) {
        Swal.fire({
            icon: 'success',
            title: 'Taxi Actualizado',
            showConfirmButton: false,
            timer: 1500,
            didClose: () => {
                sessionStorage.setItem('bandera_2', '0');
            }
        });
    } else if (bandera_2 == 2) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Algo salió mal!',
            didClose: () => {
                sessionStorage.setItem('bandera_2', '0');
            }
        });
    }

};