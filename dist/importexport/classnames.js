(function() {
  $(document).ready(function() {
    $('#submit_map').click(function() {
      var c, classDict, k, sel, v;
      classDict = {};
      for (c in classes) {
        classDict[c] = [];
      }
      $('.classe-def').each(function() {
        var imf, to;
        imf = $(this).children('label').text();
        to = $(this).children('select').val();
        return classDict[to].push(imf);
      });
      if ($('#delete_missing').is(':checked')) {
        for (k in classDict) {
          v = classDict[k];
          if (v.length === 0) {
            classDict[k] = null;
          }
        }
      }
      sel = $('#map_form input[name="res"]');
      if (sel.length) {
        sel.val(JSON.stringify(classDict));
      } else {
        $('#map_form').append(function() {
          return $('<input>').attr('type', 'hidden').attr('name', 'res').val(JSON.stringify(classDict));
        });
      }
      $('#map_form').submit();
    });
    if ((typeof preData !== "undefined" && preData !== null) && Object.keys(preData).length > 0) {
      $('.classe-def').each(function() {
        var imf;
        imf = $(this).children('label').text();
        if (preData[imf] != null) {
          $(this).children('select').val(preData[imf]);
        }
      });
    }
    $('#delete_missing').prop('checked', preDelete);
    $('.classe-def > select').each(function() {
      $(this).find('option').remove().end().append(function() {
        var k, results, v;
        results = [];
        for (k in classes) {
          v = classes[k];
          results.push($('<option>', {
            value: k,
            text: v
          }));
        }
        return results;
      });
    });
  });

}).call(this);

//# sourceMappingURL=classnames.js.map
