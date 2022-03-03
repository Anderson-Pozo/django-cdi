var tblMatriculation;
var select_period;
let select_level;

function getData() {
    tblMatriculation = $('#data').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        ajax: {
            url: window.location.pathname,
            type: 'POST',
            data: {
                'action': 'search',
                'period': select_period.val(),
                'level': select_level.val()
            },
            dataSrc: ""
        },
        columns: [
            {"data": "id"},
            {"data": "date_joined"},
            {"data": "period.name"},
            {"data": "level.name"},
            {"data": "student.user.full_name"},
            {"data": "student.user.dni"},            
            {"data": "id"},
            {"data": "id"},
        ],
        columnDefs: [
            {
                targets: [-2],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    return '<a rel="matters" class="btn btn-info btn-xs btn-flat" data-toggle="tooltip" title="Detalle Registro""><i class="fas fa-book"></i> <span class="badge badge-secondary">'+row.cant+'</span></a> ';
                }
            },
            
            {
                targets: [-1],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    var buttons = '<a href="/school/matriculation/update/' + row.id + '/" class="btn btn-warning btn-xs btn-flat" data-toggle="tooltip" title="Eliminar Registro"><i class="fas fa-edit"></i></a> ';
                    buttons += '<a href="/school/matriculation/delete/' + row.id + '/" class="btn btn-danger btn-xs btn-flat" data-toggle="tooltip" title="Editar Registro"><i class="fas fa-trash-alt"></i></a> ';
                    return buttons;
                }
            },
        ],
        rowCallback: function (row, data, index) {

        },
        initComplete: function (settings, json) {
            $('[data-toggle="tooltip"]').tooltip();
        }
    });
}

$(function () {

    select_period = $('select[name="period"]');
    select_level = $('select[name="course"]');

    $('.select2').select2({
        theme: 'bootstrap4',
        language: "es",
    });

    select_period.on('change', function () {
        getData();
    });

    select_level.on('change', function () {
        getData();
    });

    getData();

    $('#data tbody').on('click', 'a[rel="matters"]', function () {
        $('.tooltip').remove();
        var tr = tblMatriculation.cell($(this).closest('td, li')).index(),
            rows = tblMatriculation.row(tr.row).data();
        $('#tblMatter').DataTable({
            responsive: true,
            autoWidth: false,
            destroy: true,
            ajax: {
                url: pathname,
                type: 'POST',
                data: {
                    'action': 'search_matters',
                    'id': rows.id
                },
                dataSrc: ""
            },
            columns: [
                {data: "perioddetail.contract.teacher.user.full_name"},
                {data: "perioddetail.contract.job.name"},
                {data: "perioddetail.matter.name"},
                {data: "perioddetail.matter.level.name"},
            ],
            columnDefs: [
                {
                    targets: [-1],
                    class: 'text-center',
                    render: function (data, type, row) {
                        return data;
                    }
                }
            ]
        });
        $('#myModalMatters').modal('show');
    });
});