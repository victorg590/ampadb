confirmIsRequired = false
$password = $('#contrasenya')
$confirm = $('#repeteix_la_contrasenya')
$submit = $('#export-form button[type="submit"]')


changeRequired = ($to, nowRequired) ->
  $parent = $to.parent()
  if confirmIsRequired == nowRequired
      return
  if nowRequired
    $parent.addClass "required"
    $to.attr "required", true
    confirmIsRequired = true
  else
    $parent.removeClass "required"
    $to.attr "required", null
    confirmIsRequired = false
  return

showPassword = (show, immediate = false) ->
  speed = if immediate then 0 else "slow"
  if show
    $('.password-block').slideDown speed
  else
    $('.password-block').slideUp speed
  return

checkPassword = ->
  return $password.val() == $confirm.val()

$(document).ready ->
  # Assigna una classe als camps de contrasenya per a que sigui més fàcil
  # mostrar-los i ocultar-los 
  $password.parent().children().addClass 'password-block'
  $confirm.parent().
    children().addClass 'password-block'
  $confirm.parent().addClass 'has-feedback'
  $confirm.attr 'disabled', true

  showPassword false, true # Ocultar la contrasenya a l'inici
  $pickle = $('#format input[value="pickle"]')
  # Només mostrar la contrasenya per a Pickle
  $('#format').change ->
    showPassword $pickle.is ":checked"
    return

  # Fer que la confirmació sigui obligatòria si hi ha una contrasenya
  $password.keyup ->
    if not $(this).val() and confirmIsRequired
      changeRequired($confirm, false)
    else if $(this).val() and not confirmIsRequired
      changeRequired($confirm, true)
    $confirm.keyup()
    return
  
  $confirm.keyup ->
    if not $password.val()
      $confirm.parent().removeClass 'has-error has-success'
      $confirm.attr 'disabled', true
      $submit.attr 'disabled', null
    else if checkPassword()
      $confirm.attr 'disabled', null
      $confirm.parent().removeClass 'has-error'
      $confirm.parent().addClass 'has-success'
      $submit.attr 'disabled', null
    else
      $confirm.attr 'disabled', null
      $confirm.parent().removeClass 'has-success'
      $confirm.parent().addClass 'has-error'
      $submit.attr 'disabled', true
    return
  
  $('#export-form').submit ->
    if $password.val() and not checkPassword()
      return false
    else
      return true
  return