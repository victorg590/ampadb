gen_on_click = (op) -> ->  # Torna una funció
  list = $("#list_#{op}")
  if list.is ':hidden'
    list.slideDown 'slow'
    $(this).text text_menys
  else
    list.slideUp 'slow'
    $(this).text text_mes
  return

$(document).ready ->
  for op in ['add', 'move', 'delete', 'delclasse']
    if opn[op] <= 1
      $("#view_#{op}").remove()
    else
      $("#list_#{op}").hide()
      $("#view_#{op}")
        .text text_mes
        .show()
        .click gen_on_click op
  return
