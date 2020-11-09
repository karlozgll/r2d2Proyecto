$(document).ready(function() {

    $('#formsong').on('submit', function(event) {
        $.ajax({
                data: { nombre: $('#namesong').val() },
                type: 'POST',
                url: 'process'
            })
            .done(function(data) {
                if (data.error) {
                    $('contsong').text(data.error).show();
                } else {
                    $('#contsong').empty();
                    $('#contsong').html(data);

                }
            });

        event.preventDefault();
    });

    $(".alert").fadeTo(2000, 500).slideUp(500, function(){
        $(".alert").slideUp(500);
    });

    document.addEventListener('play', function(e) {
        var audios = document.getElementsByTagName('audio');
        for (var i = 0, len = audios.length; i < len; i++) {
            if (audios[i] != e.target) {
                audios[i].pause();
            }
        }
    }, true);

    // Pon la variable whichAudio "global"
    var whichAudio;

    $(document).on('click', '.play', function() {
        whichAudio = $('#' + $(this).data('audio'));
        whichAudio[0].paused ?
            whichAudio[0].play() :
            whichAudio[0].pause();
    });

});