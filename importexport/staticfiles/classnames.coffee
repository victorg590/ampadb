setParamNoRepeat = (paramName, newVal) ->
  $sel = $("#map_form input[name=\"#{paramName}\"]")
  if $sel.length
    $sel.val JSON.stringify newVal
  else
    $('#map_form').append ->
      $('<input>').attr('type', 'hidden').attr('name', paramName)
        .val JSON.stringify newVal

$(document).ready ->
  $('#submit_map').click ->
    classDict = {}
    $('.classe-def').each ->
      imf = $(this).children('label').text()
      to = $(this).children('select').val()
      to = null if to == ''
      if classDict[to]?
        classDict[to].push imf
      else
        classDict[to] = [imf]
      return

    setParamNoRepeat 'res', classDict
    setParamNoRepeat 'delete', $('#delete_missing').prop 'checked'
    $('#map_form').submit()
    return

  $('.classe-def').each ->
    imf = $(this).children('label').text()
    $(this).children('select').val (preData[imf] ? '')
    return

  $('#delete_missing').prop 'checked', preDelete
  return
