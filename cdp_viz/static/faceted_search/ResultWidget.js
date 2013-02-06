(function ($) {

AjaxSolr.ResultWidget = AjaxSolr.AbstractWidget.extend({
  beforeRequest: function () {
    $(this.target).html($('<img/>').attr('src', '/wsgi/cdp/images/ajax-loader.gif'));
  },

  facetLinks: function (facet_field, facet_values) {
    var links = [];
    if (facet_values) {
      for (var i = 0, l = facet_values.length; i < l; i++) {
        links.push(AjaxSolr.theme('facet_link', facet_values[i], this.facetHandler(facet_field, facet_values[i])));
      }
    }
    return links;
  },

  facetHandler: function (facet_field, facet_value) {
    var self = this;
    return function () {
      self.manager.store.remove('fq');
      self.manager.store.addByValue('fq', facet_field + ':' + AjaxSolr.Parameter.escapeValue(facet_value));
      self.manager.doRequest(0);
      return false;
    };
  },

  afterRequest: function () {
    $(this.target).empty();
    for (var i = 0, l = this.manager.response.response.docs.length; i < l; i++) {
      var doc = this.manager.response.response.docs[i];
      $(this.target).append(AjaxSolr.theme('result', doc, AjaxSolr.theme('snippet', doc)));

      var items = [];
      items = items.concat(this.facetLinks('instruments',
                                           doc['CollectionMetaData/Platform/Instrument/InstrumentShortName']));
      items = items.concat(this.facetLinks('platforms',
                                           doc['CollectionMetaData/Platform/PlatformShortName']));
      items = items.concat(this.facetLinks('disciplines',
                                           doc['CollectionMetaData/DisciplineTopicParameters/DisciplineKeyword']));
      items = items.concat(this.facetLinks('topics',
                                           doc['CollectionMetaData/DisciplineTopicParameters/TopicKeyword']));
      items = items.concat(this.facetLinks('terms',
                                           doc['CollectionMetaData/DisciplineTopicParameters/TermKeyword']));
      items = items.concat(this.facetLinks('variables',
                                           doc['CollectionMetaData/DisciplineTopicParameters/VariableKeyword']));
      items = items.concat(this.facetLinks('parameters',
                                           doc['GranuleURMetaData/MeasuredParameter/MeasuredParameterContainer/ParameterName']));
      AjaxSolr.theme('list_items', '#links_' + doc.id, items);
    }
  },

  init: function () {
    $('a.more').livequery(function () {
      $(this).toggle(function () {
        $(this).parent().find('span').show();
        $(this).text('less');
        return false;
      }, function () {
        $(this).parent().find('span').hide();
        $(this).text('more');
        return false;
      });
    });
  }
});

})(jQuery);
