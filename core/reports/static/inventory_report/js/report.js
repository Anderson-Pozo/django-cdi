let columns = [];
let tblReport = null;
let select_bodega;

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
    let parameters = {
        'action': 'search_report',
        'bodega': select_bodega.val()
        
    };

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
                            let d = new Date();
                            let date_now = d.getFullYear() + "_" + d.getMonth() + "_" + d.getDay();
                            let a = document.createElement("a");
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
            //{data: "id"},
            {data: "material.name"},
            {data: "material.description"},
            //{data: "material.bodega_id"},
            {data: "stock"},
        ],
        columnDefs: [
            {
                targets: [-1],
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

    select_bodega = $('select[name="bodega"]');

    $('.select2').select2({
        theme: 'bootstrap4',
        language: "es",
    });

    select_bodega.on('change', function () {
        generateReport();
    });

    

    $('.drp-buttons').hide();

    initTable();
});