let fechita = document.getElementById('fecha')

fechita.addEventListener('keypress', fechita.onkeypress = notteclado)

function notteclado(e) {
    tecla = (fechita) ? e.keyCode : e.which;
    console.log(tecla)
    if (tecla == 8) return true; //Tecla de retroceso (para poder borrar)
    if (tecla >= 48 && tecla <= 57) return false
}