<html>
  <head>
    <title>${title}</title>
    <script src="${request.application_url}/timeline/timeline_js/timeline-api.js?bundle=true" type="text/javascript"></script>
    <link rel="stylesheet" type="text/css" href="${request.application_url}/ext-4.0.2a/resources/css/ext-all.css"/>
    <script type="text/javascript" src="${request.application_url}/ext-4.0.2a/ext-all-debug.js"></script>
    <script type="text/javascript" src="${request.application_url}/scripts/utils.js"></script>
 
    <link rel='stylesheet' href='${request.application_url}/resources/css/timeline/timeline_styles.css' type='text/css' /> <!-- load your css after Timeline's -->
    <script>
        var tl;
        function onLoad() {
        
        	// get session start time first then create timeline
        	Ext.Ajax.request({
		        url: "${request.application_url}/timeline/getSessionStartTime",
		        params: {sessionId: "${sessionId}"},
		        success: function(resp, opts) {
		        	var obj = Ext.JSON.decode(resp.responseText);

					var eventSource = new Timeline.DefaultEventSource(0);
		            
		            // Example of changing the theme from the defaults
		            // The default theme is defined in 
		            // http://simile-widgets.googlecode.com/svn/timeline/tags/latest/src/webapp/api/scripts/themes.js
		            var theme = Timeline.ClassicTheme.create();
		            theme.event.bubble.width = 350;
		            theme.event.bubble.height = 300;
		            
		            var d = Timeline.DateTime.parseIso8601DateTime(obj.startTime);
		            var bandInfos = [
		                Timeline.createBandInfo({
		                    width:          "80%", 
		                    intervalUnit:   Timeline.DateTime.SECOND, 
		                    intervalPixels: 200,
		                    eventSource:    eventSource,
		                    date:           d,
		                    theme:          theme,
		                    layout:         'original'  // original, overview, detailed
		                }),
		                Timeline.createBandInfo({
		                    width:          "20%", 
		                    intervalUnit:   Timeline.DateTime.MINUTE, 
		                    intervalPixels: 200,
		                    eventSource:    eventSource,
		                    date:           d,
		                    theme:          theme,
		                    layout:         'overview'  // original, overview, detailed
		                })
		            ];
		            bandInfos[1].syncWith = 0;
		            bandInfos[1].highlight = true;
		                        
		            tl = Timeline.create(document.getElementById("tl"), bandInfos, Timeline.HORIZONTAL);
		            tl.loadJSON("${request.application_url}/timeline/getSessionTimelineData?sessionId=" + "${sessionId_nopound}",
		            	function(json, url) {
		            		eventSource.loadJSON(json, "");
		            	});
		        },
		        failure: requestFailed
    		});
        }
        var resizeTimerID = null;
        function onResize() {
            if (resizeTimerID == null) {
                resizeTimerID = window.setTimeout(function() {
                    resizeTimerID = null;
                    tl.layout();
                }, 500);
            }
        }
    </script>

    <style type="text/css">
      /* These css rules are used to modify the display of events with classname attribute */
      /* In a production system, the rules should be in an external css file to enable     */
      /* shared use and caching                                                            */
      .special_event {font-variant: small-caps; font-weight: bold;}
    </style>
  </head>
  <body onload="onLoad();" onresize="onResize();">
    <div id="content">
      <div id="tl" class="timeline-default" style="height: 550px;"></div>
    </div>
  </body>
</html>
