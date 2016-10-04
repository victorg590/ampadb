$(document).ready ->
  $('#submit_map').click ->
    class_dict = {}
    class_dict[c] = [] for c in classes
    $('.classe-def').each ->
      imf = $(this).children('label').text()
      to = $(this).children('select').val()
      class_dict[to].push imf
    if $('#delete_missing').is ':checked'
      class_dict[k] = null for k, v of class_dict when v.length == 0
    #alert JSON.stringify class_dict
    sel = $('#map_form input[name="res"]')
    if sel.length
      sel.val JSON.stringify class_dict
    else
      $('#map_form').append ->
        $('<input>').attr('type', 'hidden').attr('name', 'res').
          val JSON.stringify class_dict
    $('#map_form').submit()
    return

  if pre_data? and Object.keys(pre_data).length > 0
    $('.classe-def').each ->
      imf = $(this).children('label').text()
      if pre_data[imf]?
        $(this).children('select').val pre_data[imf]
      return
  return
