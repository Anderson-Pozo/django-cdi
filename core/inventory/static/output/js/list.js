$(function () {
    $('#data tbody').on('click', 'a[rel="details"]', function () {
        $('.tooltip').remove();
        const td = table.cell($(this).closest('td, li')).index(),
            rows = table.row(td.row).data();
        const id = parseInt(rows[0]);
        $('#tblMatDetails').DataTable({
            responsive: true,
            autoWidth: false,
            destroy: true,
            ajax: {
                url: pathname,
                type: 'POST',
                data: {
                    action: 'search_outputs', id: id
                },
                dataSrc: ""
            },
            columns: [
                {data: "material"},
                {data: "bodega_id"},
                {data: "amount"},
            ],
            columnDefs: [
                {
                    targets: [-1],
                    class: 'text-center',
                    render: function (data, type, row) {
                        return '<b>'+data+'</b>';
                    }
                }
            ]
        });
        $('#myModalOutputs').modal('show');
    });
});
