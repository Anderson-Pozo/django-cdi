var input_daterange;
var current_date;
var tblReport = null;
var columns = [];
var select_breakfast;
var parameters;

function initTable() {
    tblReport = $('#tblReport').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
    });

    $.each(tblReport.settings()[0].aoColumns, function (key, value) {
        columns.push(value.sWidthOrig);
    });
}

function generateReport(all) {
    parameters = {
        'action': 'search_report',
        'start_date': input_daterange.data('daterangepicker').startDate.format('YYYY-MM-DD'),
        'end_date': input_daterange.data('daterangepicker').endDate.format('YYYY-MM-DD'),
        'breakfast': select_breakfast.val()
    };

    if (all) {
        parameters['start_date'] = '';
        parameters['end_date'] = '';
    }

    tblReport = $('#tblReport').DataTable({
        destroy: true,
        responsive: true,
        autoWidth: false,
        ajax: {
            url: pathname,
            type: 'POST',
            data: parameters,
            dataSrc: ''
        },
        order: [[0, 'asc']],
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
                className: 'btn btn-danger btn-flat btn-xs btnPdf',
                action: function (e, dt, node, config) {
                    parameters['action'] = 'generate_pdf';
                    $.ajax({
                        url: pathname,
                        type: 'POST',
                        data: parameters,
                        xhrFields: {
                            responseType: 'blob'
                        },
                        success: function (request) {
                            console.log(request);
                            var d = new Date();
                            var date_now = d.getFullYear() + "_" + d.getMonth() + "_" + d.getDay();
                            var a = document.createElement("a");
                            document.body.appendChild(a);
                            a.style = "display: none";
                            const blob = new Blob([request], {type: 'application/pdf'});
                            const url = URL.createObjectURL(blob);
                            a.href = url;
                            a.download = "download_pdf_" + date_now + ".pdf";
                            a.click();
                            window.URL.revokeObjectURL(url);
                        },
                        error: function (jqXHR, textStatus, errorThrown) {
                            message_error(errorThrown + ' ' + textStatus);
                        }
                    });
                }
            }
        ],
        columns: [
            {data: "breakfast.name"},
            {data: "date_joined"},
            {data: "student.user.full_name"},
            {data: "cant"},
            {data: "desc"},
        ],
        columnDefs: [
            {
                targets: [-2],
                class: 'text-center',
                render: function (data, type, row) {
                    return data;
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

    current_date = new moment().format('YYYY-MM-DD');
    input_daterange = $('input[name="date_range"]');
    select_breakfast = $('select[name="breakfast"]');

    $('.select2').select2({
        theme: 'bootstrap4',
        language: "es",
    });

    select_breakfast.on('change', function () {
        generateReport();
    });

    input_daterange
        .daterangepicker({
            language: 'auto',
            startDate: new Date(),
            locale: {
                format: 'YYYY-MM-DD',
            }
        })
        .on('apply.daterangepicker', function (ev, picker) {
            generateReport();
        });

    $('.drp-buttons').hide();

    initTable();

    $('.btnSearchReport').on('click', function () {
        generateReport(false);
    });

    $('.btnSearchAll').on('click', function () {
        generateReport(true);
    });

    $('.btnPdf').on('click', function (e) {
        e.preventDefault();
        alert('x');
    });
});