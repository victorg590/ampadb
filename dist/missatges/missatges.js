(function() {
  var gen_on_click;

  gen_on_click = function(seccio, ctx) {
    return function() {
      if (ctx.tancats_current[seccio]) {
        $("#" + seccio + " tr.tancat").hide('fast');
        $("#tancats_" + seccio).text(text_veure_tancats);
        ctx.tancats_current[seccio] = false;
      } else {
        $("#" + seccio + " tr.tancat").show('fast');
        $("#tancats_" + seccio).text(text_amagar_tancats);
        ctx.tancats_current[seccio] = true;
      }
    };
  };

  $(document).ready(function() {
    $('#tancats_rebuts').text(text_veure_tancats).click(gen_on_click('rebuts', this));
    $('#rebuts tr.tancat').hide();
    $('#tancats_enviats').text(text_veure_tancats).click(gen_on_click('enviats', this));
    $('#enviats tr.tancat').hide();
    this.tancats_current = {
      rebuts: false,
      enviats: false
    };
  });

}).call(this);

//# sourceMappingURL=missatges.js.map
