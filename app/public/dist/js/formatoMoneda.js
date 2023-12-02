function formatoMoneda(input) {
    let valor;

    if (typeof input === 'string') {
        valor = input;
    } else if (input instanceof HTMLInputElement) {
        // Si se proporciona un elemento de entrada, obtén su valor
        valor = input.value;
    } else {
        return;
    }

    // Elimina cualquier carácter que no sea un dígito
    valor = valor.replace(/[^\d]/g, '');

    // Verifica si el valor resultante es una cadena vacía
    if (valor === '') {
        // Si es una cadena vacía, asigna una cadena vacía al campo de entrada y sale de la función
        if (input instanceof HTMLInputElement) {
            input.value = '';
        }
        return '';
    }

    // Formatea el valor con comas
    valor = new Intl.NumberFormat('es-ES').format(parseInt(valor, 10));

    // Si se proporciona un elemento de entrada, actualiza su valor
    if (input instanceof HTMLInputElement) {
        input.value = valor;
    }

    // Devuelve el valor formateado (opcional, dependiendo de tus necesidades)
    return valor;
}

function limpiarFormatoMoneda(input) {
    let valor;

    if (typeof input === 'string') {
        valor = input;
    } else if (input instanceof HTMLInputElement) {
        // Si se proporciona un elemento de entrada, obtén su valor
        valor = input.value;
    } else {
        return;
    }

    // Elimina cualquier carácter que no sea un dígito
    valor = valor.replace(/[^\d]/g, '');

    // Si el valor resultante es una cadena vacía, asigna una cadena vacía al campo de entrada
    if (valor === '') {
        // Si es una cadena vacía, asigna una cadena vacía al campo de entrada y sale de la función
        if (input instanceof HTMLInputElement) {
            input.value = '';
        }
        return '';
    }

    // Si se proporciona un elemento de entrada, actualiza su valor sin formato de moneda
    if (input instanceof HTMLInputElement) {
        input.value = valor;
    }

    // Devuelve el valor sin formato de moneda (opcional, dependiendo de tus necesidades)
    return valor;
}
