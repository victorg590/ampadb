(function() {
  $(document).ready(function() {
    $('#contrasenya').parent().children().addClass('password-block');
    return $('#format').change(function() {
      if ($('#format input[value=""]').is(":checked") || $('#format input[value="pickle"]').is(":checked")) {
        return $('.password-block').slideDown('slow');
      } else {
        return $('.password-block').slideUp('slow');
      }
    });
  });

}).call(this);

//# sourceMappingURL=import.js.map
