let banderaUser = sessionStorage.getItem('banderaUser') || 0;
console.log("banderaUser:", banderaUser);

let bandera_2 = sessionStorage.getItem('bandera_2') || 0;
console.log("bandera:", bandera_2);

document.addEventListener("DOMContentLoaded", function () {

    banderaUser = sessionStorage.getItem('banderaUser') || 0;

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

    const form = document.getElementById("updateUserForm1");

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

                sessionStorage.setItem('banderaUser', '1');

                // Recargar la página después de un breve retraso
                setTimeout(function () {
                    location.reload();
                }, 500);
            } else {
                sessionStorage.setItem('banderaUser', '2');
            }

        } catch (error) {
            console.error("Error al enviar la solicitud:", error);
            sessionStorage.setItem('banderaUser', '2');
        }
    });

    console.log("bandera CON LA SESION SETEADA :", banderaUser);


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

window.addEventListener("load", function () {

    const banderaUser = sessionStorage.getItem('banderaUser');
    const bandera_2 = sessionStorage.getItem('bandera_2');

    console.log("banderaUser luego de que se recargue:", banderaUser);

    if (banderaUser == 1) {
        console.log("entro a la alerta");
        Swal.fire({
            icon: 'success',
            title: 'Usuario Actualizado',
            showConfirmButton: false,
            timer: 1500,
            didClose: () => {
                sessionStorage.setItem('banderaUser', '0');
            }
        });
    } else if (banderaUser == 2) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Algo salió mal!',
            didClose: () => {
                sessionStorage.setItem('banderaUser', '0');
            }
        });
    }

    if (bandera_2 == 1) {
        Swal.fire({
            icon: 'success',
            title: 'Vehiculo Actualizado',
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
});

