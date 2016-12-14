(function() {
  var setParamNoRepeat;

  setParamNoRepeat = function(paramName, newVal) {
    var sel;
    sel = $("#map_form input[name=\"" + paramName + "\"]");
    if (sel.length) {
      return sel.val(JSON.stringify(newVal));
    } else {
      return $('#map_form').append(function() {
        return $('<input>').attr('type', 'hidden').attr('name', paramName).val(JSON.stringify(newVal));
      });
    }
  };

  $(document).ready(function() {
    $('#submit_map').click(function() {
      var classDict, sel;
      classDict = {};
      $('.classe-def').each(function() {
        var imf, ref, to;
        imf = $(this).children('label').text();
        to = $(this).children('select').val();
        if (((ref = classDict[to]) != null ? ref.push(imf) : void 0) == null) {
          classDict[to] = [imf];
        }
      });
      sel = $('#map_form input[name="res"]');
      setParamNoRepeat('res', classDict);
      setParamNoRepeat('delete', $('#delete_missing').prop('checked'));
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
  });

}).call(this);

//# sourceMappingURL=classnames.js.map
