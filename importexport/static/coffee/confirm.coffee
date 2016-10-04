gen_on_click = (op) ->
  ->
    list = $("#list_#{op}")
    if list.is ':hidden'
      list.show()
      $(this).text text_menys
    else
      list.hide()
      $(this).text text_mes
    return

$(document).ready ->
  for op in ['add', 'move', 'delete', 'delclasse']
    if opn[op] <= 1
      console.log "#{opn[op]} (<= 1)"
      $("#view_#{op}").remove()
    else
      console.log "#{opn[op]} (> 1)"
      $("#list_#{op}").hide()
      $("#view_#{op}")
        .text text_mes
        .show()
        .click gen_on_click op
  return
