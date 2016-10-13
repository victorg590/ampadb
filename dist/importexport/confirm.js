(function() {
  var genOnClick;

  genOnClick = function(op) {
    return function() {
      var list;
      list = $("#list_" + op);
      if (list.is(':hidden')) {
        list.slideDown('slow');
        $(this).text(textMenys);
      } else {
        list.slideUp('slow');
        $(this).text(textMes);
      }
    };
  };

  $(document).ready(function() {
    var i, len, op, ref;
    ref = ['add', 'move', 'delete', 'delclasse'];
    for (i = 0, len = ref.length; i < len; i++) {
      op = ref[i];
      if (opn[op] <= 1) {
        $("#view_" + op).remove();
      } else {
        $("#list_" + op).hide();
        $("#view_" + op).text(textMes).show().click(genOnClick(op));
      }
    }
  });

}).call(this);

//# sourceMappingURL=confirm.js.map
