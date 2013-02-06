<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <link rel="stylesheet" type="text/css" href="${request.application_url}/ext-4.0.2a/resources/css/ext-all.css"/>
    <style type="text/css">
      #loading{
          position:absolute;
          left:45%;
          top:45%;
          padding:2px;
          z-index:20001;
          height:auto;
          border:1px solid #ccc;
      }
      #loading a {
          color:#225588;
      }
      #loading .loading-indicator{
          background:white;
          color:#444;
          font:bold 13px tahoma,arial,helvetica;
          padding:10px;
          margin:0;
          height:auto;
      }
      #loading-msg {
          font: normal 10px arial,tahoma,sans-serif;
      }
    </style>
    ${self.head_tags()}
  </head>
  <body onload="Ext.get('loading').fadeOut({remove: true});">
    <div id="loading">
      <div class="loading-indicator">
        <img src="${request.application_url}/ext-4.0.2a/resources/themes/images/default/shared/large-loading.gif"
          width="32" height="32"
          style="margin-right:8px;float:left;vertical-align:top;"/>${title}<br />
          <span id="loading-msg">Loading styles and images...</span>
      </div>
    </div>
    ${self.body()}
  </body>
</html>
