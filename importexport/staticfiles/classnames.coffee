$(document).ready ->
  $('#submit_map').click ->
    classDict = {}
    classDict[c] = [] for c of classes
    $('.classe-def').each ->
      imf = $(this).children('label').text()
      to = $(this).children('select').val()
      classDict[to].push imf
    if $('#delete_missing').is ':checked'
      classDict[k] = null for k, v of classDict when v.length == 0
    sel = $('#map_form input[name="res"]')
    if sel.length
      sel.val JSON.stringify classDict
    else
      $('#map_form').append ->
        $('<input>').attr('type', 'hidden').attr('name', 'res').
          val JSON.stringify classDict
    $('#map_form').submit()
    return

  if preData? and Object.keys(preData).length > 0
    $('.classe-def').each ->
      imf = $(this).children('label').text()
      $(this).children('select').val preData[imf] if preData[imf]?
      return

  $('#delete_missing').prop 'checked', preDelete

  $('.classe-def > select').each ->
    $(this)
      .find 'option'
      .remove()
      .end()
      .append -> $ '<option>', {value: k, text: v} for k, v of classes
    return

  return
