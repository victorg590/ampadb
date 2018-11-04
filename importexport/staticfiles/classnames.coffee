setParamNoRepeat = (paramName, newVal) ->
  $sel = $("#map_form input[name=\"#{paramName}\"]")
  newValJson = JSON.stringify newVal
  if $sel.length
    $sel.val newValJson
  else
    $('#map_form').append ->
      $('<input>').attr('type', 'hidden').attr('name', paramName)
        .val newValJson
  return

$(document).ready ->
  $('#submit_map').click ->
    classDict = {}
    $('.classe-def').each ->
      imf = $(this).children('label').text()
      to = $(this).children('select').val()
      classDict[imf] = if to == '' then null else to
      return

    setParamNoRepeat 'res', classDict
    setParamNoRepeat 'delete', $('#delete_missing').prop 'checked'
    $('#map_form').submit()
    return

  $('.classe-def').each ->
    imf = $(this).children('label').text()
    $(this).children('select').val (mapaAnterior[imf] ? '')
    return

  $('#delete_missing').prop 'checked', eliminarAnterior
  return
