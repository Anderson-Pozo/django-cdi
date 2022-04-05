let input_daterange;
let tblMovements;

let select_user;
let select_material;

function getMovementsData(all) {
    let parameters = {
        'action': 'get_data',
        'material': select_material.val(),
        'user': select_user.val(),
        'start_date': input_daterange.data('daterangepicker').startDate.format('YYYY-MM-DD'),
        'end_date': input_daterange.data('daterangepicker').endDate.format('YYYY-MM-DD'),
    };

    if (all) {
        parameters['start_date'] = '';
        parameters['end_date'] = '';
    }

    tblMovements = $('#tblMovements').DataTable({
        destroy: true,
        responsive: {
            details: false
        },
        autoWidth: false,
        ajax: {
            url: pathname,
            type: 'POST',
            data: parameters,
            dataSrc: ''
        },
        order: [[2, 'desc']],
        paging: false,
        ordering: true,
        searching: false,
        dom: 'Bfrtip',
        buttons: [
            {
                extend: 'excelHtml5',
                text: 'Descargar Excel <i class="fas fa-file-excel"></i>',
                titleAttr: 'Excel',
                className: 'btn btn-primary btn-flat btn-xs'
            },
            {
                extend: 'pdfHtml5',
                text: 'Descargar Pdf <i class="fas fa-file-pdf"></i>',
                titleAttr: 'Pdf',
                className: 'btn btn-danger btn-flat btn-xs btnPdf'
            }
        ],
        columns: [
            {data: "id_material"},
            {data: "num_doc"},
            {data: "date"},
            {data: "material"},
            {data: "amount_entry"},
            {data: "amount_output"},
            {data: "employee_teacher"},
            {data: "type_entry"},
        ],
        columnDefs: [
            {
                targets: [0],
                createdCell: (td, cellData, rowData, row, col) => {
                    if ( rowData.type === 'Output'){
                        $(td).addClass('dt-control')
                    }else {
                        $(td).addClass('text-center')
                    }
                },
                render: (data, type, row) => {
                    if (row.type === 'Output') return ''
                    return '-'
                }
            },
            {
                targets: [1, -2, -3, -4],
                orderable: false,
                class: 'text-center',
                render: (data, type, row) => data,
            },
            {
                targets: [-1],
                render: (data, type, row) => {
                    if (row.type_entry === 'Donación'){
                        return `<span data-toggle="tooltip" title="Repr: ${ row.donor.repres }">
                                    ${ row.donor.student }
                                </span>`
                    }
                    return data
                }
            }
        ],
        rowCallback: function (row, data, index) {

        },
        initComplete: function (settings, json) {

        },
    });
}

$(function () {
    input_daterange = $('input[name="date_range"]');
    select_user = $('select[name="users"]');
    select_material = $('select[name="materials"]');

    input_daterange
        .daterangepicker({
            language: 'auto',
            startDate: new Date(),
            locale: {
                format: 'YYYY-MM-DD',
            }
        })
        .on('apply.daterangepicker', function (ev, picker) {
            getMovementsData();
        });


    select_material.on('change', function () {
        getMovementsData();
    });

    select_user.on('change', function () {
        getMovementsData();
    });

    $('.select2').select2({
        theme: 'bootstrap4',
        language: "es",
    });

    $('#tblMovements tbody').on('click', 'td.dt-control', function () {
        let tr = $(this).closest('tr');
        let row = tblMovements.row(tr);

        if (row.child.isShown()) {
            row.child.hide();
            tr.removeClass('shown');
        } else {
            row.child(showRefundsRowChilds(row.data())).show();
            tr.addClass('shown');
        }
    });
    getMovementsData(true);
});