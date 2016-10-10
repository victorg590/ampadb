(function() {
  var gen_on_click;

  gen_on_click = function(op) {
    return function() {
      var list;
      list = $("#list_" + op);
      if (list.is(':hidden')) {
        list.show();
        $(this).text(text_menys);
      } else {
        list.hide();
        $(this).text(text_mes);
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
        $("#view_" + op).text(text_mes).show().click(gen_on_click(op));
      }
    }
  });

}).call(this);

//# sourceMappingURL=confirm.js.map
