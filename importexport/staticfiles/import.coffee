$(document).ready ->
  $('#contrasenya').parent().children().addClass('password-block')
  $('#format').change ->
    selected = ''
    for format of extensions
      selected = format if $("#format input[value=\"#{format}\"").is ':checked'

    if (selected == '' or selected == 'pickle')
      $('.password-block').slideDown 'slow'
    else
      $('.password-block').slideUp 'slow'

    $("#ifile").attr 'accepts', extensions[selected]