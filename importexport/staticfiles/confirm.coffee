MAX_DISPLAY = 10
# Nombre màxim d'entrades a mostrar abans de col·lapsar-les.

genOnClick = (op) -> ->  # Torna una funció
  list = $("#list_#{op}")
  if list.is ':hidden'
    list.slideDown 'slow'
    $(this).text textMenys
  else
    list.slideUp()
    $(this).text textMes
  return

$(document).ready ->
  for operation, number_of_ops of opn when number_of_ops >= 1
    if number_of_ops <= MAX_DISPLAY
      $("#view_#{operation}").remove()
    else
      $("#list_#{operation}").hide()
      $("#view_#{operation}")
        .text textMes
        .show()
        .click genOnClick operation
  return
