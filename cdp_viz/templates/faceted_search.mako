<%inherit file="/base_nosplash.mako" />

<%def name="head_tags()">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>${title}</title>
    
    <!-- <script type="text/javascript" src="http://maps.google.com/maps/api/js?sensor=false"></script> -->
    <link rel="stylesheet" type="text/css" href="${request.application_url}/ext-4.0.2a/examples/shared/example.css" />
    <link rel="stylesheet" type="text/css" href="${request.application_url}/ext-4.0.2a/examples/ux/css/CheckHeader.css" />
    <link rel="stylesheet" type="text/css" href="${request.application_url}/stylesheets/faceted.css" media="screen" />
    <script type="text/javascript" src="${request.application_url}/ajax/libs/jquery/1.3.2/jquery.min.js"></script>
    <script type="text/javascript" src="${request.application_url}/faceted_search/solr.js"></script>
    <script type="text/javascript" src="${request.application_url}/faceted_search/ajax-solr/core/Core.js"></script>
    <script type="text/javascript" src="${request.application_url}/faceted_search/ajax-solr/core/AbstractManager.js"></script>
    <script type="text/javascript" src="${request.application_url}/faceted_search/ajax-solr/managers/Manager.jquery.js"></script>
    <script type="text/javascript" src="${request.application_url}/faceted_search/ajax-solr/core/Parameter.js"></script>
    <script type="text/javascript" src="${request.application_url}/faceted_search/ajax-solr/core/ParameterStore.js"></script>
    <script type="text/javascript" src="${request.application_url}/faceted_search/ajax-solr/core/AbstractWidget.js"></script>
    <script type="text/javascript" src="${request.application_url}/faceted_search/ResultWidget.js"></script>
    <script type="text/javascript" src="${request.application_url}/faceted_search/ajax-solr/helpers/jquery/ajaxsolr.theme.js"></script>
    <script type="text/javascript" src="${request.application_url}/faceted_search/solr.theme.js"></script>
    <script type="text/javascript" src="${request.application_url}/faceted_search/jquery.livequery.js"></script>
    <script type="text/javascript" src="${request.application_url}/faceted_search/ajax-solr/widgets/jquery/PagerWidget.js"></script>
    <script type="text/javascript" src="${request.application_url}/faceted_search/ajax-solr/core/AbstractFacetWidget.js"></script>
    <script type="text/javascript" src="${request.application_url}/faceted_search/TagcloudWidget.js"></script>
    <script type="text/javascript" src="${request.application_url}/faceted_search/CurrentSearchWidget.9.js"></script>
    <link rel="stylesheet" type="text/css" href="${request.application_url}/stylesheets/jquery.autocomplete.css" media="screen" />
    <script type="text/javascript" src="${request.application_url}/faceted_search/jquery.autocomplete.js"></script>
    <script type="text/javascript" src="${request.application_url}/faceted_search/AutocompleteWidget.js"></script>
    <script type="text/javascript" src="${request.application_url}/faceted_search/ajax-solr/helpers/ajaxsolr.support.js"></script>
    <script type="text/javascript" src="${request.application_url}/faceted_search/ajax-solr/helpers/ajaxsolr.theme.js"></script>
    <script type="text/javascript" src="${request.application_url}/faceted_search/CountryCodeWidget.js"></script>
    <script type="text/javascript" src="${request.application_url}/ajax/libs/jqueryui/1.7.2/jquery-ui.min.js"></script>
    <link rel="stylesheet" type="text/css" href="${request.application_url}/stylesheets/jquery-ui.css" media="screen" />
    <link rel="stylesheet" type="text/css" href="${request.application_url}/stylesheets/ui.theme.css" media="screen" />
    <script type="text/javascript" src="${request.application_url}/faceted_search/CalendarWidget.js"></script>
    
    <!--
    <script type="text/javascript" src="${request.application_url}/faceted_search/GMapPanel3.js"></script>
    <script type="text/javascript" src="${request.application_url}/faceted_search/gmap.js"></script>
    <script type="text/javascript" src="${request.application_url}/faceted_search/bbox.js"></script>
    -->
    
    <script type="text/javascript" src="${request.application_url}/scripts/utils.js"></script>    
    <script type="text/javascript" src="${request.application_url}/faceted_search/app/view/ui/MyWindow.js"></script>
    <script type="text/javascript" src="${request.application_url}/faceted_search/app/view/MyWindow.js"></script>
    <script type="text/javascript" src="${request.application_url}/faceted_search/designer.js"></script>
    
    <script type="text/javascript">
        Ext.onReady(function() {
            Ext.getCmp('cdp_faceted_win').hide();
        });
    </script>
    
    <style type="text/css">
        .x-mask {
            background: none repeat scroll 0 0 #000000;
            opacity: .65;
        }
    </style>
</%def>

<div id="showLink"><a href="javascript:showWindow('showLink');">show</a></div>