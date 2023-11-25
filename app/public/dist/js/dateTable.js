$(document).ready(function () {
    var table = $('#dataUsers').DataTable({
        select: true,
        destroy: true,
        columnDefs: [
            {
                targets: [3],
                orderable: false
            },
            {
                targets: [3],
                orderable: false 
            }
        ],
        language: {
            url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json',
            "searchPlaceholder": "Busqueda en tabla",
        },
        pagingType: 'full_numbers',
        dom: '<"top"Bfrtip>rt<"bottom"lp><"clear">',
        buttons: [
            {
                extend: 'copy',
                title: 'Reporte del Conductor: {{ conductor.nombre }} {{ conductor.apellido }}',

            },
            {
                extend: 'excel',
                title: 'Reporte del Conductor: {{ conductor.nombre }} {{ conductor.apellido }}'
            },
            {
                extend: 'pdf',
                title: 'Reporte del Conductor: {{ conductor.nombre }} {{ conductor.apellido }} {{ today }}',
                customize: function(doc) {
                    doc.content.splice(0, 0, {
                        text: 'Reporte del Conductor: {{ conductor.nombre }} {{ conductor.apellido }}',
                        fontSize: 16,
                        alignment: 'center',
                        margin: [0, 10, 0, 10]
                    });

                }
            },
            {
                extend: 'csv',
                title: 'Reporte del Conductor: {{ conductor.nombre }} {{ conductor.apellido }}'
            },
            {
                extend: 'print',
                title: 'Reporte del Conductor: {{ conductor.nombre }} {{ conductor.apellido }}'
            }
        ],
        stateSave: true,
        "stripeClasses": [],
        "lengthMenu": [5, 10, 20, 50],
        "pageLength": 10
    });
});