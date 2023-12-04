function openUpdatePaymentModal(idConductor, idPago, valorActual) {
    document.getElementById('updatePaymentModal').classList.remove('hidden');
    document.getElementById('id_conductor').value = idConductor;
    document.getElementById('id_pago').value = idPago;
    document.getElementById('valorpagos').value = valorActual;
}

function closeUpdatePaymentModal() {
    document.getElementById('updatePaymentModal').classList.add('hidden');
}