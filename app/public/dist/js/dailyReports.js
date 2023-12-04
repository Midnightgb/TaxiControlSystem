let banderaOpen = sessionStorage.getItem('banderaOpen') || 0;
document.addEventListener("DOMContentLoaded", function () {
    const openModalPago = document.getElementById("openModalPago");
    const closeModalPago = document.getElementById("closeModalPago");

    const modalPago = document.getElementById("modalPago");

    openModalPago.addEventListener("click", function () {
        modalPago.classList.remove("hidden");
    });

    closeModalPago.addEventListener("click", function () {
        modalPago.classList.add("hidden");
    });
    const form = document.getElementById("formPago");

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
                modalPago.classList.add("hidden");

                sessionStorage.setItem('banderaOpen', '1');

                // Recargar la página después de un breve retraso
                setTimeout(function () {
                    location.reload();
                }, 500);
            } else {
                sessionStorage.setItem('banderaOpen', '2');
            }

        } catch (error) {
            console.error("Error al enviar la solicitud:", error);
        }
    });

    window.onload = function () {
        const banderaOpen = sessionStorage.getItem('banderaOpen');
        
    
        if (banderaOpen == 1) {
            Swal.fire({
                icon: 'success',
                title: 'Pago realizado correctamente',
                showConfirmButton: false,
                timer: 1500,
                didClose: () => {
                    sessionStorage.setItem('banderaOpen', '0');
                }
            });
        } else if (banderaOpen == 2) {
            Swal.fire({
                icon: 'error',
                title: 'Oops...',
                text: 'Algo salió mal!',
                didClose: () => {
                    sessionStorage.setItem('banderaOpen', '0');
                }
            });
        }
    }
    
});