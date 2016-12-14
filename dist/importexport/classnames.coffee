setParamNoRepeat = (paramName, newVal) ->
  sel = $("#map_form input[name=\"#{paramName}\"]")
  if sel.length
    sel.val JSON.stringify newVal
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
      if not (classDict[to]?.push imf)?
        classDict[to] = [imf]
      return

    sel = $('#map_form input[name="res"]')
    setParamNoRepeat 'res', classDict
    setParamNoRepeat 'delete', $('#delete_missing').prop 'checked'
    $('#map_form').submit()
    return

  if preData? and Object.keys(preData).length > 0
    $('.classe-def').each ->
      imf = $(this).children('label').text()
      $(this).children('select').val preData[imf] if preData[imf]?
      return

  $('#delete_missing').prop 'checked', preDelete
  return
