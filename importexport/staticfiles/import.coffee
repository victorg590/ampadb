$(document).ready ->
  $('#contrasenya').parent().children().addClass('password-block')
  $('#format').change ->
    if ($('#format input[value=""]').is(":checked") or
    $('#format input[value="pickle"]').is(":checked"))
      $('.password-block').slideDown 'slow'
    else
      $('.password-block').slideUp 'slow'