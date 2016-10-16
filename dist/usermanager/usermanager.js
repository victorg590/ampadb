(function() {
  var formatRegistered, formatUnregistered, getRegisteredUsers, getUnregisteredUsers, hideSearch, parseSearch, textMostraRegistered, textMostraUnregistered, toggleRegistered, toggleUnregistered;

  textMostraRegistered = (TEXT_MOSTRA_TOT + " (" + N_REGISTERED) + (" usuari" + (N_REGISTERED === 1 ? '' : 's') + ")");

  textMostraUnregistered = (TEXT_MOSTRA_TOT + " (" + N_UNREGISTERED) + (" usuari" + (N_UNREGISTERED === 1 ? '' : 's') + ")");

  window.cachedRegistered = null;

  window.cachedUnregistered = null;

  formatRegistered = function(users) {
    var i, len, results, u;
    results = [];
    for (i = 0, len = users.length; i < len; i++) {
      u = users[i];
      results.push($('<tr>').append($('<td>').append(function() {
        var ref;
        if (u.alumne == null) {
          return $();
        } else {
          return $('<a>').attr('href', (ref = u.alumneUrl) != null ? ref : '#').text(u.alumne);
        }
      })).append($('<td>').append($('<span>').addClass('username').text(u.username))).append($('<td>').append(function() {
        if (u.admin) {
          return $('<span>').addClass('glyphicon glyphicon-ok').css('color', '#008000');
        } else {
          return $('<span>').addClass('glyphicon glyphicon-remove').css('color', '#FF0000');
        }
      })).append($('<td>').append($('<a>').addClass('btn btn-default').attr('href', u.changePasswordUrl).text("Canviar contrasenya"))).append($('<td>').append($('<a>').addClass('btn btn-danger').attr('href', u.deleteUrl).text("Eliminar"))));
    }
    return results;
  };

  getRegisteredUsers = function(data, status) {
    if (status !== 'success') {
      console.error("Error: " + status + " | " + (data != null ? data : '[No data]'));
      return $();
    }
    window.cachedRegistered = formatRegistered(data.registeredUsers);
  };

  formatUnregistered = function(users) {
    var i, len, results, u;
    results = [];
    for (i = 0, len = users.length; i < len; i++) {
      u = users[i];
      results.push($('<tr>').append($('<td>').append($('<a>').attr('href', u.alumneUrl).text(u.alumne))).append($('<td>').append($('<span>').addClass('username').text(u.username))).append($('<td>').text(u.codi)).append($('<td>').append(function() {
        return $('<div>').addClass('btn-group').attr('role', 'group').append($('<a>').addClass('btn btn-primary').attr('href', u.changeAutoUrl).text("Generar")).append($('<a>').addClass('btn btn-default').attr('href', u.changeUrl).text("Canviar"));
      })).append($('<td>').append($('<a>').addClass('btn btn-danger').attr('href', u.cancelUrl).text("Cancel·lar"))));
    }
    return results;
  };

  getUnregisteredUsers = function(data, status) {
    if (status !== 'success') {
      console.error("Error: " + status + " | " + (data != null ? data : '[No data]'));
      return $();
    }
    window.cachedUnregistered = formatUnregistered(data.unregisteredUsers);
  };

  toggleRegistered = function() {
    var $spinner, $table, $toggle, ajax, show;
    $table = $('#table_registered');
    $toggle = $('#registered_toggle');
    if ($table.is(':hidden')) {
      show = function() {
        $table.slideDown('slow');
        $toggle.text(TEXT_AMAGA);
      };
      if (window.cachedRegistered != null) {
        show();
      } else {
        $spinner = $('#registered_spinner').show();
        ajax = $.getJSON(REGISTERED_USERS_URL, getRegisteredUsers);
        $.when(ajax).done(function() {
          ($table.find('tbody')).find('tr').remove().end().append(window.cachedRegistered);
          $spinner.hide();
        });
        show();
      }
    } else {
      $table.slideUp('fast');
      $toggle.text(textMostraRegistered);
    }
  };

  toggleUnregistered = function() {
    var $spinner, $table, $toggle, ajax, show;
    $table = $('#table_unregistered');
    $toggle = $('#unregistered_toggle');
    if ($table.is(':hidden')) {
      show = function() {
        $table.slideDown('slow');
        $toggle.text(TEXT_AMAGA);
      };
      if (window.cachedUnregistered != null) {
        show();
      } else {
        $spinner = $('#unregistered_spinner').show();
        ajax = $.getJSON(UNREGISTERED_USERS_URL, getUnregisteredUsers);
        $.when(ajax).done(function() {
          ($table.find('tbody')).find('tr').remove().end().append(window.cachedUnregistered);
          $spinner.hide();
        });
        show();
      }
    } else {
      $table.slideUp('fast');
      $toggle.text(textMostraUnregistered);
    }
  };

  parseSearch = function(data) {
    $('#resultats_cerca').show();
    $('#n_res_total').show().text(((data.registeredUsers.length + data.unregisteredUsers.length) + " ") + "resultats");
    if (data.registeredUsers.length > 0) {
      $('#cerca_registrats').show();
      $('#n_res_registered').show().text(data.registeredUsers.length + " resultats");
      $('#search_registered').show().find('tbody tr').remove().end().append(formatRegistered(data.registeredUsers));
    } else {
      $('#n_res_registered').hide();
      $('#cerca_registrats').hide();
      $('#search_registered').hide();
    }
    if (data.unregisteredUsers.length > 0) {
      $('#cerca_no_registrats').show();
      $('#n_res_unregistered').show().text(data.unregisteredUsers.length + " resultats");
      $('#search_unregistered').show().find('tbody tr').remove().end().append(formatUnregistered(data.unregisteredUsers));
    } else {
      $('#n_res_unregistered').hide();
      $('#cerca_no_registrats').hide();
      $('#search_unregistered').hide();
    }
  };

  hideSearch = function() {
    $('#resultats_cerca').hide();
    $('#cerca_registrats').hide();
    $('#cerca_no_registrats').hide();
    $('#search_registered').hide();
    $('#search_unregistered').hide();
    $('#n_res_total').hide();
    $('#n_res_registered').hide();
    $('#n_res_unregistered').hide();
  };

  $(document).ready(function() {
    $('#unregistered_spinner').hide();
    $('#registered_spinner').hide();
    if (N_REGISTERED <= MAX_DISPLAY && (typeof REGISTERED !== "undefined" && REGISTERED !== null)) {
      $('#registered_toggle').hide();
      $('#table_registered tbody').find('tr').remove().end().append(formatRegistered(REGISTERED));
    } else {
      $('#table_registered').hide();
      $('#registered_toggle').text(textMostraRegistered).click(toggleRegistered);
    }
    if (N_UNREGISTERED <= MAX_DISPLAY && (typeof UNREGISTERED !== "undefined" && UNREGISTERED !== null)) {
      $('#unregistered_toggle').hide();
      $('#table_unregistered tbody').find('tr').remove().end().append(formatUnregistered(UNREGISTERED));
    } else {
      $('#table_unregistered').hide();
      $('#unregistered_toggle').text(textMostraUnregistered).click(toggleUnregistered);
    }
    hideSearch();
    $('#search_field').keyup(function(event) {
      if (event.keyCode === 13) {
        $('#search_btn').click();
      }
    });
    $('#search_btn').click(function() {
      var q;
      q = $('#search_field').val();
      if (!q) {
        hideSearch();
        return;
      }
      $.getJSON(SEARCH_URL, {
        q: q
      }, function(data, status) {
        if (status !== 'success') {
          console.error("Error: " + status + " | " + (data != null ? data : '[No data]'));
          return;
        }
        parseSearch(data);
      });
    });
  });

}).call(this);

//# sourceMappingURL=usermanager.js.map
