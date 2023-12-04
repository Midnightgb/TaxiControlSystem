let bandera = sessionStorage.getItem('bandera') || 0;
document.addEventListener("DOMContentLoaded", function () {
    const openModalButton = document.getElementById("openModalButton");
    const closeModalButton = document.getElementById("closeModalButton");

   

    const modal = document.getElementById("modalPago");
    

    openModalButton.addEventListener("click", function () {
        modal.classList.remove("hidden");
    });

    closeModalButton.addEventListener("click", function () {
        modal.classList.add("hidden");
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

    window.onload = function () {
        const bandera = sessionStorage.getItem('bandera');
        
    
        if (bandera == 1) {
            Swal.fire({
                icon: 'success',
                title: 'Pago realizado correctamente',
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
    }
    
});