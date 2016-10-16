textMostraRegistered = "#{TEXT_MOSTRA_TOT} (#{N_REGISTERED}" +
    " usuari#{if N_REGISTERED == 1 then '' else 's'})"
textMostraUnregistered = "#{TEXT_MOSTRA_TOT} (#{N_UNREGISTERED}" +
  " usuari#{if N_UNREGISTERED == 1 then '' else 's'})"

window.cachedRegistered = null
window.cachedUnregistered = null

formatRegistered = (users) ->
  for u in users
    $('<tr>')
      .append($('<td>')
        .append ->
          if not u.alumne?
            $()  # No posis res
          else
            $('<a>')
              .attr 'href', u.alumneUrl ? '#'
              .text u.alumne
        )
      .append $('<td>').append($('<span>')
        .addClass 'username'
        .text u.username
        )
      .append $('<td>').append ->
        if u.admin
          $('<span>')
            .addClass 'glyphicon glyphicon-ok'
            .css 'color', '#008000'
        else
          $('<span>')
            .addClass 'glyphicon glyphicon-remove'
            .css 'color', '#FF0000'
      .append $('<td>').append($('<a>')
        .addClass 'btn btn-default'
        .attr 'href', u.changePasswordUrl
        .text "Canviar contrasenya"
        )
      .append $('<td>').append($('<a>')
        .addClass 'btn btn-danger'
        .attr 'href', u.deleteUrl
        .text "Eliminar"
        )

getRegisteredUsers = (data, status) ->
  if status != 'success'
    console.error "Error: #{status} | #{data ? '[No data]'}"
    return $()
  window.cachedRegistered = formatRegistered data.registeredUsers

  return

formatUnregistered = (users) ->
  for u in users
    $('<tr>')
      .append $('<td>').append($('<a>')
        .attr 'href', u.alumneUrl
        .text u.alumne
        )
      .append $('<td>').append($('<span>')
        .addClass 'username'
        .text u.username
        )
      .append $('<td>').text u.codi
      .append($('<td>')
        .append ->
          $('<div>')
            .addClass 'btn-group'
            .attr 'role', 'group'
            .append($('<a>')
              .addClass 'btn btn-primary'
              .attr 'href', u.changeAutoUrl
              .text "Generar"
              )
            .append($('<a>')
              .addClass 'btn btn-default'
              .attr 'href', u.changeUrl
              .text "Canviar"
              )
        )
      .append $('<td>').append($('<a>')
        .addClass 'btn btn-danger'
        .attr 'href', u.cancelUrl
        .text "Cancel·lar"
        )

getUnregisteredUsers = (data, status) ->
  if status != 'success'
    console.error "Error: #{status} | #{data ? '[No data]'}"
    return $()
  window.cachedUnregistered = formatUnregistered data.unregisteredUsers

  return

toggleRegistered = ->
  $table = $('#table_registered')
  $toggle = $('#registered_toggle')
  if $table.is ':hidden'
    show = ->
      $table.slideDown 'slow'
      $toggle.text TEXT_AMAGA
      return
    if window.cachedRegistered?
      show()
    else
      $spinner = $('#registered_spinner').show()
      ajax = $.getJSON REGISTERED_USERS_URL, getRegisteredUsers
      $.when(ajax).done ->
        ($table.find 'tbody')
          .find 'tr'
          .remove()
          .end()
          .append window.cachedRegistered
          $spinner.hide()
        return
      show()
  else
    $table.slideUp 'fast'
    $toggle.text textMostraRegistered
  return

toggleUnregistered = ->
  $table = $('#table_unregistered')
  $toggle = $('#unregistered_toggle')
  if $table.is ':hidden'
    show = ->
      $table.slideDown 'slow'
      $toggle.text TEXT_AMAGA
      return
    if window.cachedUnregistered?
      show()
    else
      $spinner = $('#unregistered_spinner').show()
      ajax = $.getJSON UNREGISTERED_USERS_URL, getUnregisteredUsers
      $.when(ajax).done ->
        ($table.find 'tbody')
        .find 'tr'
        .remove()
        .end()
        .append window.cachedUnregistered
        $spinner.hide()
        return
      show()
  else
    $table.slideUp 'fast'
    $toggle.text textMostraUnregistered
  return

parseSearch = (data) ->
  $('#resultats_cerca').show()
  $('#n_res_total')
    .show()
    .text "#{data.registeredUsers.length + data.unregisteredUsers.length} " +
      "resultats"
  if data.registeredUsers.length > 0
    $('#cerca_registrats').show()
    $('#n_res_registered')
      .show()
      .text "#{data.registeredUsers.length} resultats"
    $('#search_registered').show().find 'tbody tr'
      .remove()
      .end()
      .append formatRegistered data.registeredUsers
  else
    $('#n_res_registered').hide()
    $('#cerca_registrats').hide()
    $('#search_registered').hide()

  if data.unregisteredUsers.length > 0
    $('#cerca_no_registrats').show()
    $('#n_res_unregistered')
      .show()
      .text "#{data.unregisteredUsers.length} resultats"
    $('#search_unregistered').show().find 'tbody tr'
      .remove()
      .end()
      .append formatUnregistered data.unregisteredUsers
  else
    $('#n_res_unregistered').hide()
    $('#cerca_no_registrats').hide()
    $('#search_unregistered').hide()
  return

hideSearch = ->
  $('#resultats_cerca').hide()
  $('#cerca_registrats').hide()
  $('#cerca_no_registrats').hide()
  $('#search_registered').hide()
  $('#search_unregistered').hide()
  $('#n_res_total').hide()
  $('#n_res_registered').hide()
  $('#n_res_unregistered').hide()
  return

$(document).ready ->
  $('#unregistered_spinner').hide()
  $('#registered_spinner').hide()
  if N_REGISTERED <= MAX_DISPLAY and REGISTERED?
    $('#registered_toggle').hide()
    $('#table_registered tbody')
      .find 'tr'
      .remove()
      .end()
      .append formatRegistered REGISTERED

  else
    $('#table_registered').hide()
    $('#registered_toggle')
      .text textMostraRegistered
      .click toggleRegistered
  if N_UNREGISTERED <= MAX_DISPLAY and UNREGISTERED?
    $('#unregistered_toggle').hide()
    $('#table_unregistered tbody')
      .find 'tr'
      .remove()
      .end()
      .append formatUnregistered UNREGISTERED
  else
    $('#table_unregistered').hide()
    $('#unregistered_toggle')
      .text textMostraUnregistered
      .click toggleUnregistered
  hideSearch()
  $('#search_field').keyup (event) ->
    if event.keyCode == 13  # 13 = "Enter"
      $('#search_btn').click()
    return
  $('#search_btn').click ->
    q = $('#search_field').val()
    if not q
      hideSearch()
      return
    $.getJSON SEARCH_URL, {q: q}, (data, status) ->
        if status != 'success'
          console.error "Error: #{status} | #{data ? '[No data]'}"
          return
        parseSearch data
        return
    return
  return
