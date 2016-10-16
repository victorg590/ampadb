genOnClick = (op) -> ->  # Torna una funció
  list = $("#list_#{op}")
  if list.is ':hidden'
    list.slideDown 'slow'
    $(this).text textMenys
  else
    list.slideUp 'slow'
    $(this).text textMes
  return

$(document).ready ->
  for op in ['add', 'move', 'delete', 'delclasse']
    if opn[op] <= 1
      $("#view_#{op}").remove()
    else
      $("#list_#{op}").hide()
      $("#view_#{op}")
        .text textMes
        .show()
        .click genOnClick op
  return
