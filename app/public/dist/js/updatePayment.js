document.getElementById("updatePaymentForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    const formData = new FormData(this);
    const response = await fetch("/update/payment", {
        method: "POST",
        body: formData,
    });

    if (response.ok) {
        const result = await response.json();

        if (result.error_update) {
           
            Swal.fire({
                icon: 'error',
                title: 'Error en la actualización del pago',
                text: result.message_update,  
                showConfirmButton: false,
                timer: 2500,
            });
        } else {
            Swal.fire({
                icon: 'success',
                title: 'Pago Actualizado',
                text: result.message_update, 
                showConfirmButton: false,
                timer: 1500,
                didClose: () => {
                    window.location.reload();
                }
            });
        }
    } else {
        Swal.fire({
            icon: 'error',
            title: 'Error en la solicitud',
            text: 'No se pudo actualizar el pago',
            showConfirmButton: false,
            timer: 1500,
        });
    }
});
