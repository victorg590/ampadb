(function() {
  var $confirm, $password, changeRequired, checkPassword, confirmIsRequired, showPassword;

  confirmIsRequired = false;

  $password = $('#contrasenya');

  $confirm = $('#repeteix_la_contrasenya');

  changeRequired = function($to, nowRequired) {
    var $parent;
    $parent = $to.parent();
    if (confirmIsRequired === nowRequired) {
      return;
    }
    if (nowRequired) {
      $parent.addClass("required");
      $to.attr("required", true);
      confirmIsRequired = true;
    } else {
      $parent.removeClass("required");
      $to.attr("required", null);
      confirmIsRequired = false;
    }
  };

  showPassword = function(show, immediate) {
    var speed;
    if (immediate == null) {
      immediate = false;
    }
    speed = immediate ? 0 : "slow";
    if (show) {
      $('.password-block').slideDown(speed);
    } else {
      $('.password-block').slideUp(speed);
    }
  };

  checkPassword = function() {
    return $password.val() === $confirm.val();
  };

  $(document).ready(function() {
    var $pickle;
    $password.parent().children().addClass('password-block');
    $confirm.parent().children().addClass('password-block');
    $confirm.parent().addClass('has-feedback');
    $confirm.attr('disabled', true);
    showPassword(false, true);
    $pickle = $('#format input[value="pickle"]');
    $('#format').change(function() {
      showPassword($pickle.is(":checked"));
    });
    $password.keyup(function() {
      if (!$(this).val() && confirmIsRequired) {
        changeRequired($confirm, false);
      } else if ($(this).val() && !confirmIsRequired) {
        changeRequired($confirm, true);
      }
      $confirm.keyup();
    });
    $confirm.keyup(function() {
      if (!$password.val()) {
        $confirm.parent().removeClass('has-error has-success');
        $confirm.attr('disabled', true);
      } else if (checkPassword()) {
        $confirm.attr('disabled', null);
        $confirm.parent().removeClass('has-error');
        $confirm.parent().addClass('has-success');
      } else {
        $confirm.attr('disabled', null);
        $confirm.parent().removeClass('has-success');
        $confirm.parent().addClass('has-error');
      }
    });
  });

}).call(this);

//# sourceMappingURL=export.js.map
