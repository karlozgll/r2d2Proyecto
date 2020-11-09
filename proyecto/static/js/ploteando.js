$(document).ready(function() {

    $('#formmap').on('submit', function(event) {
        $('#contploteo').html('<img class="rounded mx-auto d-block" width="60" height="60" src="http://www.3engine.net/wp/wp-content/uploads/2016/03/loading.gif" alt="loading"> </img> <hr>')
        $.ajax({
                data: { lat: $('#lat').val(), lon: $('#lon').val(), fecha: $('#fecha').val(), start: $('#start').val() },
                type: 'POST',
                url: 'ploteomaps'
            })
            .done(function(data) {
                if (data.error) {
                    $('#contploteo').text(data.error).show();
                } else {
                    $('#contploteo').empty();
                    $('#contploteo').html(data);

                }
            });

        event.preventDefault();
    });
});