gen_on_click = (seccio, ctx) -> ->  # Torna una funció
  if ctx.tancats_current[seccio]
    $("##{seccio} tr.tancat").hide 'fast'
    $("#tancats_#{seccio}").text text_amagar_tancats
    ctx.tancats_current[seccio] = false
  else
    $("##{seccio} tr.tancat").show 'fast'
    $("#tancats_#{seccio}").text text_veure_tancats
    ctx.tancats_current[seccio] = true
  return

$(document).ready ->
  $('#tancats_rebuts').text text_veure_tancats
    .click gen_on_click 'rebuts', @
  $('#rebuts tr.tancat').hide()
  $('#tancats_enviats').text text_veure_tancats
    .click gen_on_click 'enviats', @
  $('#enviats tr.tancat').hide()
  @tancats_current =
    rebuts: false
    enviats: false
  return
