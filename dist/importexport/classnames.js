(function() {
  $(document).ready(function() {
    $('#submit_map').click(function() {
      var c, class_dict, i, k, len, sel, v;
      class_dict = {};
      for (i = 0, len = classes.length; i < len; i++) {
        c = classes[i];
        class_dict[c] = [];
      }
      $('.classe-def').each(function() {
        var imf, to;
        imf = $(this).children('label').text();
        to = $(this).children('select').val();
        return class_dict[to].push(imf);
      });
      if ($('#delete_missing').is(':checked')) {
        for (k in class_dict) {
          v = class_dict[k];
          if (v.length === 0) {
            class_dict[k] = null;
          }
        }
      }
      sel = $('#map_form input[name="res"]');
      if (sel.length) {
        sel.val(JSON.stringify(class_dict));
      } else {
        $('#map_form').append(function() {
          return $('<input>').attr('type', 'hidden').attr('name', 'res').val(JSON.stringify(class_dict));
        });
      }
      $('#map_form').submit();
    });
    if ((typeof pre_data !== "undefined" && pre_data !== null) && Object.keys(pre_data).length > 0) {
      $('.classe-def').each(function() {
        var imf;
        imf = $(this).children('label').text();
        if (pre_data[imf] != null) {
          $(this).children('select').val(pre_data[imf]);
        }
      });
    }
    $('#delete_missing').prop('checked', pre_delete);
  });

}).call(this);

//# sourceMappingURL=classnames.js.map
