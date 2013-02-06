(function ($) {

AjaxSolr.theme.prototype.result = function (doc, snippet) {
  var output = '<div><h2><b>' + doc['alias'] + '</b></h2>';
  output += '<p id="links_' + doc['name'] + '" class="links"></p>';
  output += '<p>' + snippet + '</p></div>';
  return output;
};

AjaxSolr.theme.prototype.snippet = function (doc) {
  var output = '';
  //console.log(doc['session']);
  var graphId = AjaxSolr.Parameter.escapeValue(doc['session'][0]);
  var sessionId = delquote(graphId);
  var name = AjaxSolr.Parameter.escapeValue(doc['name']);
  name = delquote(name);
  /*
  if (doc['id'].length > 300) {
    output += doc['id'].substring(0, 300);
    output += '<span style="display:none;">' + doc['id'].substring(300);
    output += '</span> <a href="#" class="more">more</a>';
  }
  else {
    output += doc['id'];
  }
  */
  if (doc['timestamp']) output += '<b>last updated:</b> ' + doc['timestamp'] + '<br/>';
  if (doc['type']) output += '<b>type:</b> ' + doc['type'] + '<br/>';
  if (doc['entity_timestamp']) output += '<b>entity timestamp:</b> ' + doc['entity_timestamp'] + '<br/>';
  if (doc['session_alias']) {
    output += '<b>session:</b> ';
    if (doc['session_alias'].length > 1) {
      output += doc['session_alias'][0];
      output += '<span style="display:none;">';
      output += '<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;';
      output += doc['session_alias'].slice(1).join("<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;");
      output += '</span> <a href="#" class="more">more</a>';
    }
    else {
      output += doc['session_alias'];
    }
    output += '<br/>';
  }
  if (doc['agent_alias']) output += '<b>agent:</b> ' + doc['agent_alias'] + '<br/>';
  if (doc['instrument']) output += '<b>instrument:</b> ' + doc['instrument'] + '<br/>';
  if (doc['dataset']) output += '<b>dataset:</b> ' + doc['dataset'] + '<br/>';
  if (doc['version']) output += '<b>version:</b> ' + doc['version'] + '<br/>';
  if (doc['generated_alias']) {
    output += '<b>generatedBy:</b> ';
    if (doc['generated_alias'].length > 1) {
      output += doc['generated_alias'][0];
      output += '<span style="display:none;">';
      output += '<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;';
      output += doc['generated_alias'].slice(1).join("<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;");
      output += '</span>'; // <a href="#" class="more_generated">more</a>';
    }
    else {
      output += doc['generated_alias'];
    }
    output += '<br/>';
  }
  if (doc['used_alias']) {
    output += '<b>used:</b> ';
    if (doc['used_alias'].length > 1) {
      output += doc['used_alias'][0];
      output += '<span style="display:none;">';
      output += '<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;';
      output += doc['used_alias'].slice(1).join("<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;");
      output += '</span>'; // <a href="#" class="more_used">more</a>';
    }
    else {
      output += doc['used_alias'];
    }
    output += '<br/>';
  }
  var sessionIdEsc = encodeURIComponent(sessionId);
  output += '<a href="/wsgi/cdp/fdl?sessionId=' + sessionIdEsc + '" target="_blank">fdl</a>';
  output += ' | <a href="/wsgi/cdp/timeline?sessionId=' + sessionIdEsc + '&timeline-use-local-resources" target="_blank">timeline</a>';
  return output;
};

AjaxSolr.theme.prototype.tag = function (value, weight, handler) {
  return $('<a href="#" class="tagcloud_item"/><br/>').text(value).addClass('tagcloud_size_' + weight).click(handler);
};

AjaxSolr.theme.prototype.facet_link = function (value, handler) {
  return $('<a href="#"/>').text(value).click(handler);
};

AjaxSolr.theme.prototype.no_items_found = function () {
  return 'no items found in current selection';
};

})(jQuery);
