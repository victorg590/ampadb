(function() {
  var genOnClick;

  genOnClick = function(seccio, ctx) {
    return function() {
      if (ctx.tancatsCurrent[seccio]) {
        $("#" + seccio + " tr.tancat").hide('fast');
        $("#tancats_" + seccio).text(textAmagarTancats);
        ctx.tancatsCurrent[seccio] = false;
      } else {
        $("#" + seccio + " tr.tancat").show('fast');
        $("#tancats_" + seccio).text(textVeureTancats);
        ctx.tancatsCurrent[seccio] = true;
      }
    };
  };

  $(document).ready(function() {
    $('#tancats_rebuts').text(textVeureTancats).click(genOnClick('rebuts', this));
    $('#rebuts tr.tancat').hide();
    $('#tancats_enviats').text(textVeureTancats).click(genOnClick('enviats', this));
    $('#enviats tr.tancat').hide();
    this.tancatsCurrent = {
      rebuts: false,
      enviats: false
    };
  });

}).call(this);

//# sourceMappingURL=missatges.js.map
