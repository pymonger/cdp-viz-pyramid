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
    <title>${title}</title>
    <link rel="stylesheet" type="text/css" href="${request.application_url}/ext-4.0.2a/resources/css/ext-all.css"/>
    <script type="text/javascript" src="${request.application_url}/ext-4.0.2a/ext-all-debug.js"></script>
    <script type="text/javascript" src="${request.application_url}/scripts/utils.js"></script>
  </head>
  <body>
    <div id="loading">
      <div class="loading-indicator">
        <img src="${request.application_url}/ext-4.0.2a/resources/themes/images/default/shared/large-loading.gif"
          width="32" height="32"
          style="margin-right:8px;float:left;vertical-align:top;"/>${title}<br />
          <span id="loading-msg">You will be redirected to the CVO interface. Waiting for EC2 instance...</span>
      </div>
    </div>
    <script type="text/javascript">
      Ext.Ajax.timeout = 180000; //3 minutes
      Ext.Ajax.request({
          url: 'reproduce/startInstance',
          params: {dlLink: "${dlLink}",
                   hash: "${hash}",
                   filename: "${filename}"},
          success: function(resp, opts) {
              var obj = Ext.JSON.decode(resp.responseText);
              window.location = obj.url;
          },
          failure: requestFailed
      });
    </script>
  </body>
</html>
