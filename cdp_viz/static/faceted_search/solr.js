var Manager;

function showWindow(id) {
    var width = Ext.getBody().getViewSize().width * 0.9;
    var height = Ext.getBody().getViewSize().height * 0.9;
    var x = (Ext.getBody().getViewSize().width - width)/2;
    var y = (Ext.getBody().getViewSize().height - height)/2;
    var win = Ext.getCmp('cdp_faceted_win');
    win.setSize(width, height);
    win.setPosition(x, y);
    win.show(id);

    (function ($) {
		  $(function () {
		    Manager = new AjaxSolr.Manager({
		      solrUrl: '/wsgi/cdp/solr/'
		    });
		    Manager.addWidget(new AjaxSolr.ResultWidget({
		      id: 'result',
		      target: '#docs'
		    }));
		    Manager.addWidget(new AjaxSolr.PagerWidget({
		      id: 'faceted-pager',
		      target: '#faceted-pager',
		      prevLabel: '&lt;',
		      nextLabel: '&gt;',
		      innerWindow: 1,
		      renderHeader: function (perPage, offset, total) {
		        $('#faceted-pager-header').html($('<span/>').text('displaying ' + Math.min(total, offset + 1) + ' to ' + Math.min(total, offset + perPage) + ' of ' + total));
		      }
		    }));
		    var fields = [['sessions', 'session_alias'],
		                  ['types', 'type'],
		                  ['instruments', 'instrument'],
		                  ['datasets', 'dataset'],
		                  ['versions', 'version'],
		                  ['agents', 'agent_alias']
		                  ];
		    var facetFields = [];
		    for (var i = 0, l = fields.length; i < l; i++) {
		      Manager.addWidget(new AjaxSolr.TagcloudWidget({
		        id: fields[i][0],
		        target: '#' + fields[i][0],
		        field: fields[i][1]
		      }));
		      facetFields.push(fields[i][1]);
		    }
		    Manager.addWidget(new AjaxSolr.CurrentSearchWidget({
		      id: 'currentsearch',
		      target: '#selection'
		    }));
		    Manager.addWidget(new AjaxSolr.AutocompleteWidget({
		      id: 'text',
		      target: '#search',
		      field: 'text',
		      fields: [ 'name',
		                'session' ]
		    }));
		    /*
		    Manager.addWidget(new AjaxSolr.CountryCodeWidget({
		      id: 'countries',
		      target: '#countries',
		      field: 'countryCodes'
		    }));
		    Manager.addWidget(new AjaxSolr.CalendarWidget({
		      id: 'calendar',
		      target: '#calendar',
		      field: 'date'
		    }));
		    */
		    Manager.init();
		    Manager.store.addByValue('q', '*:*');
		    var params = {
		      facet: true,
		      'facet.field': facetFields,
		      'facet.limit': 20,
		      'facet.mincount': 1,
		      'f.topics.facet.limit': 50,
		      /*
		      'f.countryCodes.facet.limit': -1,
		      'facet.date': 'timestamp',
		      'facet.date.start': '1987-02-26T00:00:00.000Z/DAY',
		      'facet.date.end': '1987-10-20T00:00:00.000Z/DAY+1DAY',
		      'facet.date.gap': '+1DAY',
		      */
		      'json.nl': 'map'
		    };
		    for (var name in params) {
		      Manager.store.addByValue(name, params[name]);
		    }
		    Manager.doRequest();
		  });
		
		  $.fn.showIf = function (condition) {
		    if (condition) {
		      return this.show();
		    }
		    else {
		      return this.hide();
		    }
		  }
		
		})(jQuery);
}
