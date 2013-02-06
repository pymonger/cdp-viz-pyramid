<%inherit file="/base.mako" />

<%def name="head_tags()">
    <title>${title}</title>
    <link rel="stylesheet" type="text/css" href="${request.application_url}/ext-4.0.2a/resources/css/ext-all.css"/>
    <script type="text/javascript" src="${request.application_url}/ext-4.0.2a/ext-all-debug.js"></script>
    <script type="text/javascript" src="${request.application_url}/scripts/utils.js"></script>
    <script type="text/javascript" src="${request.application_url}/d3/d3.v2.js"></script>
    <style type="text/css">
    body {
      margin: 0;
      background: #eee;
    }
    path.link {
	  fill: none;
	  stroke: #666;
	  stroke-width: 1.5px;
	}
	
	marker#triggered {
	  fill: green;
	}
	
	path.link.triggered {
	  stroke: green;
	  stroke-width: 3;
	}
	
	marker#controlled {
	  fill: lime;
	}
	
	path.link.controlled {
	  stroke: lime;
	}
	
	marker#input {
	  fill: red;
	  opacity: .1;
	}
	
	path.link.input {
	  stroke: red;
	  stroke-opacity: .1;
	}
	
	marker#output {
	  fill: blue;
	  opacity: .1;
	}
	
	path.link.output {
	  stroke: blue;
	  stroke-opacity: .1;
	}
	
	marker#related {
      fill: #00BFFF;
    }
    
    path.link.related {
      stroke: #00BFFF;
      stroke-width: 3;
      stroke-dasharray: 8 3 2;
    }
	
	circle {
	  fill: #aec7e8;
	  stroke: #fff;
	  stroke-width: 1.5px;
	}
	
	rect.entity, use.entity {
	  fill: #ffbb78;
	  stroke: #fff;
	  stroke-width: 1.5px;
	}
	
	polygon {
	  fill: #1f77b4;
	  stroke: #fff;
	  stroke-width: 1.5px;
	}

	text {
	  font: 15px sans-serif;
	  pointer-events: none;
	}
	
	text.shadow {
	  stroke: #fff;
	  stroke-width: 3px;
	  stroke-opacity: .8;
	}
	
	text.hidden {
	  display: none;
	}

    </style>
</%def>

<script type="text/javascript">

// set canvas attributes
var w = document.body.clientWidth,
    h = document.body.clientHeight,
    r = 15,
    polyLength = 10,
    rectLength = 18;

// declare various evil but necessary globals
var win = null;
var force = null;
var svg = null;
var defs = null;
var nodes = [];
var links = [];
var pathGroup = null;
var agentGroup = null;
var textGroup = null;
var entsGroup = null;
var procsGroup = null;

var relatedSessionAdded = false;

// handler to set CSS class to show text shadow
function show(d, i) {
	if (i % 2 == 0) return "shadow";
	else return null;
}

// handler to set CSS class to hide text
function hide(d, i) {
	return "hidden";
}

// function that returns the svg text nodes that match current node
function getMatchedTextNodes(d) {
	// get text nodes for this entity
	return textGroup.selectAll("g text")
		.filter(function(e) {
			// match text node to the shape node that is currently selected
    		if ((d.nodeName == e.nodeName) && 
    		    d3.select(this).attr("node_idx") == d.index) return true;
    		return false;
    	});
}

// handler to show text on the current node
function showText(d) {
    getMatchedTextNodes(d).attr("class", show);
}

// handler to hide text on the current node
function hideText(d) {
    getMatchedTextNodes(d).attr("class", hide);
}

// handler to show info window of an node
function showInfo(d) {
    return "translate(480,480)scale(46)rotate(180)";
    //return "translate(" + ((document.body.clientWidth-460/2)-230) + ",480)scale(46)rotate(180)"; 
}

//var translateRegExp=/translate\(([-+]?\d+)(\s*[\s,]\s*)([-+]?\d+)\)\s*/;
var dblclickedNode = null;

// handler to open up info window of a node
function dblclick(d) {
    dblclickedNode = d3.select(this);
/*
    // add info node
    var use = d3.select("svg").append("use").data([{x:0, y:0}])
        .attr("xlink:href", "#info")
        .attr("transform", "translate(" + d.x + "," + d.y + ")")
        .attr("class", "entity");
            
    // animate showing of info node
    use.transition()
        .duration(750)
        .attr("transform", showInfo)
        .style("fill", "#fff")
        .style("stroke", "#ffbb78")
        .style("stroke-width", ".05px")
        .each("end", function(e) {
            // add svg for new coordinate system
            var newsvg = use.append("svg")
                .attr("width", 480)
                .attr("height", 480)
                .attr("preserveAspectRatio", "xMaxYMax meet")
                .attr("viewBox", "0 0 480 480")
                .attr("transform", "translate(" + d.x + "," + d.y + ")");
                
            // append content to node info
            newsvg.append("foreignObject")
               .attr("width", 480)
               .attr("height", 480)
               .attr("x", 0)
               .attr("y", 0)
               .append("xhtml:body")
                   .html("<h1>This is a test</h1>");
        });
        
    // add handler to close node info
    use.on("dblclick", function (e) {
        d3.select(this).transition()
            //.delay(1500)
            .duration(750)
            .attr("transform", "translate(" + d.x + "," + d.y + ")scale(0)rotate(180)")
            .style("fill", "#ffbb78")
            .style("stroke", "#fff")
            .style("stroke-width", "1.5px")
            .style("fill-opacity", 0)
            .remove();
        });
*/

    win = new parent.Ext.Window({
        title: d.nodeName,
        width: 777,
        height: 700,
        constrain: true,
        layout: 'fit',
        modal: true,
        autoDestroy: true,
        animateTarget: this,
        html: ''
    });
    Ext.Ajax.request({
        url: "${request.application_url}/fdl/getNodeInfo",
        params: {nodeName: d.nodeName, uri: d.uri, dlLink: d.dlLink, sessionURI: "${sessionId}"},
        success: function(respNI, optsNI) {
            win.update(respNI.responseText);
        },
        failure: requestFailed
    });
    win.show();
}

// function to retrieve viz data for a session and visualize
function addSessionViz(sessionId, entityURI) {
    if(win) {
        win.close();
        relatedSessionAdded = true;
        svg.transition().duration(500)
            .attr("viewBox", "-1000 0 " + (w + 2000) + " " + h);
    }
    Ext.Ajax.request({
        url: "${request.application_url}/fdl/getSessionVizData",
        params: {sessionId: sessionId},
        success: function(resp, opts) {
            var json = Ext.JSON.decode(resp.responseText);
            var numCurNodes = nodes.length;
            var matchedIdx = null;
            var count = 0;
            json.nodes.forEach(function(n) {
                if (n.uri == entityURI) matchedIdx = count;
                if (relatedSessionAdded) {
                    n.gv_y += 200;
                    n.gv_x += 200;
                }
                nodes.push(n);
                count += 1;
            });
            
            // adjust source and target indexes
            var matchedIdxType = "input";
            json.links.forEach(function(l) {
                // determine if matched node is an input type
                if (matchedIdx !== null && l.target == matchedIdx) matchedIdxType = "output";
                l.source += numCurNodes;
                l.target += numCurNodes;
                links.push(l);
            });
            
            // connect the related nodes
            if (dblclickedNode && matchedIdx !== null) {
                dblclickedNode.each(function(d) {
                    if (matchedIdxType == "output") {
                        links.push({
                            source: matchedIdx + numCurNodes,
                            target: d,
                            type: "related"
                        });
                    }else {
                        links.push({
                            source: d,
                            target: matchedIdx + numCurNodes,
                            type: "related"
                        });
                    }
                });
            }
            
            restart();
        },
        failure: requestFailed
    });
}

// Use elliptical arc path segments to doubly-encode directionality.
function tick() {
    pathGroup.selectAll("path").attr("d", function(d) {
        if (d.type == "output") {
            var dx = d.target.x - d.source.x,
                dy = d.target.y - d.source.y,
                dr = Math.sqrt(dx * dx + dy * dy);
            // specify source and target of paths taking into account offsets to get to node center
            //return "M" + Math.max(rectLength, Math.min(w - rectLength, d.source.x)) + "," + 
            //    Math.max(rectLength, Math.min(h - rectLength, d.source.y)) + "A" + dr + 
            //    "," + dr + " 0 0,1 " + (Math.max(rectLength, Math.min(w - rectLength, d.target.x)) + 5) + 
            //    "," + (Math.max(rectLength, Math.min(h - rectLength, d.target.y)) + 5);
            return "M" + Math.max(rectLength, Math.min(w - rectLength, d.source.x)) + "," + 
                Math.max(rectLength, Math.min(h - rectLength, d.source.y)) + "L" +
                (Math.max(rectLength, Math.min(w - rectLength, d.target.x)) + 5) + 
                "," + (Math.max(rectLength, Math.min(h - rectLength, d.target.y)) + 5);
        }
        if (d.type == "input") {
            var dx = d.target.x - d.source.x,
                dy = d.target.y - d.source.y,
                dr = Math.sqrt(dx * dx + dy * dy);
            // specify source and target of paths taking into account offsets to get to node center
            //return "M" + (Math.max(rectLength, Math.min(w - rectLength, d.source.x)) + 5) + "," + 
            //    (Math.max(rectLength, Math.min(h - rectLength, d.source.y)) + 5) + "A" + dr + 
            //    "," + dr + " 0 0,1 " + Math.max(rectLength, Math.min(w - rectLength, d.target.x)) + 
            //    "," + Math.max(rectLength, Math.min(h - rectLength, d.target.y));
            return "M" + (Math.max(rectLength, Math.min(w - rectLength, d.source.x)) + 5) + "," + 
                (Math.max(rectLength, Math.min(h - rectLength, d.source.y)) + 5) + "L" +
                Math.max(rectLength, Math.min(w - rectLength, d.target.x)) + 
                "," + Math.max(rectLength, Math.min(h - rectLength, d.target.y));
        }
        if (d.type == "triggered") {
            var dx = d.target.x - d.source.x,
                dy = d.target.y - d.source.y,
                dr = Math.sqrt(dx * dx + dy * dy);
            return "M" + Math.max(rectLength, Math.min(w - rectLength, d.source.x)) + "," + 
                Math.max(rectLength, Math.min(h - rectLength, d.source.y)) + "A" + dr + 
                "," + dr + " 0 0,1 " + Math.max(rectLength, Math.min(w - rectLength, d.target.x)) + 
                "," + Math.max(rectLength, Math.min(h - rectLength, d.target.y));
        }
        if (d.type == "controlled") {
            var dx = d.target.x - d.source.x,
                dy = d.target.y - d.source.y,
                dr = Math.sqrt(dx * dx + dy * dy);
            return "M" + (Math.max(rectLength, Math.min(w - rectLength, d.source.x)) + polyLength) + 
                "," + (Math.max(rectLength, Math.min(h - rectLength, d.source.y)) + 16) + "A" + dr + 
                "," + dr + " 0 0,1 " + Math.max(rectLength, Math.min(w - rectLength, d.target.x)) + 
                "," + Math.max(rectLength, Math.min(h - rectLength, d.target.y));
        }
        if (d.type == "related") {
            var dx = d.target.x - d.source.x,
                dy = d.target.y - d.source.y,
                dr = Math.sqrt(dx * dx + dy * dy);
            // specify source and target of paths taking into account offsets to get to node center
            //return "M" + Math.max(rectLength, Math.min(w - rectLength, d.source.x)) + "," + 
            //    Math.max(rectLength, Math.min(h - rectLength, d.source.y)) + "A" + dr + 
            //    "," + dr + " 0 0,1 " + (Math.max(rectLength, Math.min(w - rectLength, d.target.x)) + 5) + 
            //    "," + (Math.max(rectLength, Math.min(h - rectLength, d.target.y)) + 5);
            return "M" + Math.max(rectLength, Math.min(w - rectLength, d.source.x)) + "," + 
                Math.max(rectLength, Math.min(h - rectLength, d.source.y)) + "L" +
                (Math.max(rectLength, Math.min(w - rectLength, d.target.x)) + 5) + 
                "," + (Math.max(rectLength, Math.min(h - rectLength, d.target.y)) + 5);
        }
    });
  
    agentGroup.selectAll("polygon").attr("transform", function(d) {
        var x = Math.max(rectLength, Math.min(w - rectLength, d.x));
        var y = Math.max(rectLength, Math.min(h - rectLength, d.y));
        return "translate(" + x + "," + y + ")";
    });

    procsGroup.selectAll("circle").attr("transform", function(d) {
        var x = Math.max(r, Math.min(w - r, d.x));
        var y = Math.max(r, Math.min(h - r, d.y));
        return "translate(" + x + "," + y + ")";
    });
  
    entsGroup.selectAll("rect").attr("transform", function(d) {
        var x = Math.max(rectLength, Math.min(w - rectLength, d.x));
        var y = Math.max(rectLength, Math.min(h - rectLength, d.y));
        return "translate(" + x + "," + y + ")";
    });

    textGroup.selectAll("g").attr("transform", function(d) {
        var x = Math.max(rectLength, Math.min(w - rectLength, d.x));
        var y = Math.max(rectLength, Math.min(h - rectLength, d.y));
        return "translate(" + x + "," + y + ")";
    });
}

// set node locations according to graphviz
function setGraphVizLocs() {
    agentGroup.selectAll("polygon").transition().duration(500)
        .attr("transform", function(d) {
            var x = Math.max(rectLength, Math.min(w - rectLength, d.gv_x));
            var y = Math.max(rectLength, Math.min(h - rectLength, d.gv_y));
            return "translate(" + x + "," + y + ")";
    });

    procsGroup.selectAll("circle").transition().duration(500)
        .attr("transform", function(d) {
            var x = Math.max(r, Math.min(w - r, d.gv_x));
            var y = Math.max(r, Math.min(h - r, d.gv_y));
            return "translate(" + x + "," + y + ")";
    });
  
    entsGroup.selectAll("rect").transition().duration(500)
        .attr("transform", function(d) {
            var x = Math.max(rectLength, Math.min(w - rectLength, d.gv_x));
            var y = Math.max(rectLength, Math.min(h - rectLength, d.gv_y));
            return "translate(" + x + "," + y + ")";
    });

    textGroup.selectAll("g").transition().duration(500)
        .attr("transform", function(d) {
            var x = Math.max(rectLength, Math.min(w - rectLength, d.gv_x));
            var y = Math.max(rectLength, Math.min(h - rectLength, d.gv_y));
            return "translate(" + x + "," + y + ")";
    });
    
    pathGroup.selectAll("path").transition().duration(500)
        .attr("d", function(d) {
        var src_x = d.source.gv_x;
        var src_y = d.source.gv_y;
        var tgt_x = d.target.gv_x;
        var tgt_y = d.target.gv_y;
        if (d.type == "output") {
            var dx = tgt_x - src_x,
                dy = tgt_y - src_y,
                dr = Math.sqrt(dx * dx + dy * dy);
            // specify source and target of paths taking into account offsets to get to node center
            //return "M" + Math.max(rectLength, Math.min(w - rectLength, src_x)) + "," + 
            //    Math.max(rectLength, Math.min(h - rectLength, src_y)) + "A" + dr + 
            //    "," + dr + " 0 0,1 " + (Math.max(rectLength, Math.min(w - rectLength, tgt_x)) + 5) + 
            //    "," + (Math.max(rectLength, Math.min(h - rectLength, tgt_y)) + 5);
            return "M" + Math.max(rectLength, Math.min(w - rectLength, src_x)) + "," + 
                Math.max(rectLength, Math.min(h - rectLength, src_y)) + "L" +
                (Math.max(rectLength, Math.min(w - rectLength, tgt_x)) + 5) + 
                "," + (Math.max(rectLength, Math.min(h - rectLength, tgt_y)) + 5);
        }
        if (d.type == "input") {
            var dx = tgt_x - src_x,
                dy = tgt_y - src_y,
                dr = Math.sqrt(dx * dx + dy * dy);
            // specify source and target of paths taking into account offsets to get to node center
            //return "M" + (Math.max(rectLength, Math.min(w - rectLength, src_x)) + 5) + "," + 
            //    (Math.max(rectLength, Math.min(h - rectLength, src_y)) + 5) + "A" + dr + 
            //    "," + dr + " 0 0,1 " + Math.max(rectLength, Math.min(w - rectLength, tgt_x)) + 
            //    "," + Math.max(rectLength, Math.min(h - rectLength, tgt_y));
            return "M" + (Math.max(rectLength, Math.min(w - rectLength, src_x)) + 5) + "," + 
                (Math.max(rectLength, Math.min(h - rectLength, src_y)) + 5) + "L" +
                Math.max(rectLength, Math.min(w - rectLength, tgt_x)) + 
                "," + Math.max(rectLength, Math.min(h - rectLength, tgt_y));
        }
        if (d.type == "triggered") {
            var dx = tgt_x - src_x,
                dy = tgt_y - src_y,
                dr = Math.sqrt(dx * dx + dy * dy);
            return "M" + Math.max(rectLength, Math.min(w - rectLength, src_x)) + "," + 
                Math.max(rectLength, Math.min(h - rectLength, src_y)) + "A" + dr + 
                "," + dr + " 0 0,1 " + Math.max(rectLength, Math.min(w - rectLength, tgt_x)) + 
                "," + Math.max(rectLength, Math.min(h - rectLength, tgt_y));
        }
        if (d.type == "controlled") {
            var dx = tgt_x - src_x,
                dy = tgt_y - src_y,
                dr = Math.sqrt(dx * dx + dy * dy);
            return "M" + (Math.max(rectLength, Math.min(w - rectLength, src_x)) + polyLength) + 
                "," + (Math.max(rectLength, Math.min(h - rectLength, src_y)) + 16) + "A" + dr + 
                "," + dr + " 0 0,1 " + Math.max(rectLength, Math.min(w - rectLength, tgt_x)) + 
                "," + Math.max(rectLength, Math.min(h - rectLength, tgt_y));
        }
        if (d.type == "related") {
            var dx = tgt_x - src_x,
                dy = tgt_y - src_y,
                dr = Math.sqrt(dx * dx + dy * dy);
            // specify source and target of paths taking into account offsets to get to node center
            //return "M" + Math.max(rectLength, Math.min(w - rectLength, src_x)) + "," + 
            //    Math.max(rectLength, Math.min(h - rectLength, src_y)) + "A" + dr + 
            //    "," + dr + " 0 0,1 " + (Math.max(rectLength, Math.min(w - rectLength, tgt_x)) + 5) + 
            //    "," + (Math.max(rectLength, Math.min(h - rectLength, tgt_y)) + 5);
            return "M" + Math.max(rectLength, Math.min(w - rectLength, src_x)) + "," + 
                Math.max(rectLength, Math.min(h - rectLength, src_y)) + "L" +
                (Math.max(rectLength, Math.min(w - rectLength, tgt_x)) + 5) + 
                "," + (Math.max(rectLength, Math.min(h - rectLength, tgt_y)) + 5);
        }
    });
}

// set node locations according to graphviz
var enableForceCalled = false;
function enableForce() {
    agentGroup.selectAll("polygon").call(force.drag).transition().duration(750)
        .attr("transform", function(d) {
            var x = Math.max(rectLength, Math.min(w - rectLength, d.x));
            var y = Math.max(rectLength, Math.min(h - rectLength, d.y));
            return "translate(" + x + "," + y + ")";
    });

    procsGroup.selectAll("circle").call(force.drag).transition().duration(750)
        .attr("transform", function(d) {
            var x = Math.max(r, Math.min(w - r, d.x));
            var y = Math.max(r, Math.min(h - r, d.y));
            return "translate(" + x + "," + y + ")";
    });
  
    entsGroup.selectAll("rect").call(force.drag).transition().duration(750)
        .attr("transform", function(d) {
            var x = Math.max(rectLength, Math.min(w - rectLength, d.x));
            var y = Math.max(rectLength, Math.min(h - rectLength, d.y));
            return "translate(" + x + "," + y + ")";
    });

    textGroup.selectAll("g").transition().duration(750)
        .attr("transform", function(d) {
            var x = Math.max(rectLength, Math.min(w - rectLength, d.x));
            var y = Math.max(rectLength, Math.min(h - rectLength, d.y));
            return "translate(" + x + "," + y + ")";
    });
    
    pathGroup.selectAll("path").transition().duration(750)
        .attr("d", function(d) {
        var src_x = d.source.x;
        var src_y = d.source.y;
        var tgt_x = d.target.x;
        var tgt_y = d.target.y;
        if (d.type == "output") {
            var dx = tgt_x - src_x,
                dy = tgt_y - src_y,
                dr = Math.sqrt(dx * dx + dy * dy);
            // specify source and target of paths taking into account offsets to get to node center
            //return "M" + Math.max(rectLength, Math.min(w - rectLength, src_x)) + "," + 
            //    Math.max(rectLength, Math.min(h - rectLength, src_y)) + "A" + dr + 
            //    "," + dr + " 0 0,1 " + (Math.max(rectLength, Math.min(w - rectLength, tgt_x)) + 5) + 
            //    "," + (Math.max(rectLength, Math.min(h - rectLength, tgt_y)) + 5);
            return "M" + Math.max(rectLength, Math.min(w - rectLength, src_x)) + "," + 
                Math.max(rectLength, Math.min(h - rectLength, src_y)) + "L" +
                (Math.max(rectLength, Math.min(w - rectLength, tgt_x)) + 5) + 
                "," + (Math.max(rectLength, Math.min(h - rectLength, tgt_y)) + 5);
        }
        if (d.type == "input") {
            var dx = tgt_x - src_x,
                dy = tgt_y - src_y,
                dr = Math.sqrt(dx * dx + dy * dy);
            // specify source and target of paths taking into account offsets to get to node center
            //return "M" + (Math.max(rectLength, Math.min(w - rectLength, src_x)) + 5) + "," + 
            //    (Math.max(rectLength, Math.min(h - rectLength, src_y)) + 5) + "A" + dr + 
            //    "," + dr + " 0 0,1 " + Math.max(rectLength, Math.min(w - rectLength, tgt_x)) + 
            //    "," + Math.max(rectLength, Math.min(h - rectLength, tgt_y));
            return "M" + (Math.max(rectLength, Math.min(w - rectLength, src_x)) + 5) + "," + 
                (Math.max(rectLength, Math.min(h - rectLength, src_y)) + 5) + "L" +
                Math.max(rectLength, Math.min(w - rectLength, tgt_x)) + 
                "," + Math.max(rectLength, Math.min(h - rectLength, tgt_y));
        }
        if (d.type == "triggered") {
            var dx = tgt_x - src_x,
                dy = tgt_y - src_y,
                dr = Math.sqrt(dx * dx + dy * dy);
            return "M" + Math.max(rectLength, Math.min(w - rectLength, src_x)) + "," + 
                Math.max(rectLength, Math.min(h - rectLength, src_y)) + "A" + dr + 
                "," + dr + " 0 0,1 " + Math.max(rectLength, Math.min(w - rectLength, tgt_x)) + 
                "," + Math.max(rectLength, Math.min(h - rectLength, tgt_y));
        }
        if (d.type == "controlled") {
            var dx = tgt_x - src_x,
                dy = tgt_y - src_y,
                dr = Math.sqrt(dx * dx + dy * dy);
            return "M" + (Math.max(rectLength, Math.min(w - rectLength, src_x)) + polyLength) + 
                "," + (Math.max(rectLength, Math.min(h - rectLength, src_y)) + 16) + "A" + dr + 
                "," + dr + " 0 0,1 " + Math.max(rectLength, Math.min(w - rectLength, tgt_x)) + 
                "," + Math.max(rectLength, Math.min(h - rectLength, tgt_y));
        }
        if (d.type == "related") {
            var dx = tgt_x - src_x,
                dy = tgt_y - src_y,
                dr = Math.sqrt(dx * dx + dy * dy);
            // specify source and target of paths taking into account offsets to get to node center
            //return "M" + Math.max(rectLength, Math.min(w - rectLength, src_x)) + "," + 
            //    Math.max(rectLength, Math.min(h - rectLength, src_y)) + "A" + dr + 
            //    "," + dr + " 0 0,1 " + (Math.max(rectLength, Math.min(w - rectLength, tgt_x)) + 5) + 
            //    "," + (Math.max(rectLength, Math.min(h - rectLength, tgt_y)) + 5);
            return "M" + Math.max(rectLength, Math.min(w - rectLength, src_x)) + "," + 
                Math.max(rectLength, Math.min(h - rectLength, src_y)) + "L" +
                (Math.max(rectLength, Math.min(w - rectLength, tgt_x)) + 5) + 
                "," + (Math.max(rectLength, Math.min(h - rectLength, tgt_y)) + 5);
        }
    });
}

var drag = d3.behavior.drag()
    .on("drag", function(d) {
        if (!enableForceCalled) {
            enableForce();
            enableForceCalled = true;
            setTimeout(force.start, 750);
            
            // reset viewBox
            svg.transition().duration(3000)
                .attr("viewBox", "0 0 " + w + " " + h);
        }
    })
    .on("dragend", function(d) {
        enableForceCalled = false;
    });

// function to draw and update visualization
function restart() {
    // create paths
    if (pathGroup == null) pathGroup = svg.append("g");
    var path = pathGroup.selectAll("path")
        .data(force.links())
      .enter().append("path")
        .attr("class", function(d) { return "link " + d.type; })
        .attr("marker-end", function(d) { return "url(#" + d.type + ")"; });
    
    // add agent node
    if (agentGroup == null) agentGroup = svg.append("g");
    var agent = agentGroup.selectAll("polygon")
        .data(force.nodes().filter(function(d) {
            if (d.nodeName.substring(0, 2) == "U_") return true;
            return false;
        }))
      .enter().append("polygon")
        .attr("points", "0,0 " + polyLength*2 + ",0 " + polyLength + "," + polyLength*2);
    //agentGroup.selectAll("polygon").call(drag);
    agentGroup.selectAll("polygon").call(d3.behavior.drag);
    
    // add process nodes
    if (procsGroup == null) procsGroup = svg.append("g");
    var procs = procsGroup.selectAll("circle")
        .data(force.nodes().filter(function(d) {
            if (d.nodeName.substring(0, 2) == "P_" || 
                d.nodeName.substring(0, 4) == "MCP_") return true;
            return false;
        }))
      .enter().append("circle")
        .attr("r", r)
        .on("dblclick", dblclick);
    //procsGroup.selectAll("circle").call(drag);
    procsGroup.selectAll("circle").call(d3.behavior.drag);
    
    // add entity nodes
    if (entsGroup == null) entsGroup = svg.append("g");
    var ents = entsGroup.selectAll("rect")
        .data(force.nodes().filter(function(d) {
            if (d.nodeName.substring(0, 2) != "P_" &&
                d.nodeName.substring(0, 2) != "U_" &&
                d.nodeName.substring(0, 4) != "MCP_") return true;
            return false;
        }))
      .enter().append("rect")
        .attr("class", "entity")
        .attr("width", rectLength)
        .attr("height", rectLength)
        .on("dblclick", dblclick)
        .on("mouseover", showText)
        .on("mouseout", hideText);
    //entsGroup.selectAll("rect").call(drag);
    entsGroup.selectAll("rect").call(d3.behavior.drag);
    
    // add groups to processes and agent for text nodes
    if (textGroup == null) textGroup = svg.append("g");
    var text = textGroup.selectAll("g")
        .data(force.nodes())
      .enter().append("g");
    
    // A copy of the text with a thick white stroke for legibility.
    text.append("text")
        .attr("x", 8)
        .attr("y", ".31em")
        .attr("class", "shadow")
        .attr("node_idx", function(d, i) { return i; })
        .text(function(d) { return d.nodeName; });
    
    text.append("text")
        .attr("x", 8)
        .attr("y", ".31em")
        .attr("node_idx", function(d, i) { return i; })
        .text(function(d) { return d.nodeName; });
        
    // hide text for all entitys
    text.each(function(d) {
        d3.selectAll("text")
            .filter(function(e) {
                if (e.nodeName.substring(0, 2) != "P_" &&
                    e.nodeName.substring(0, 2) != "U_" &&
                    e.nodeName.substring(0, 4) != "MCP_") return true;
                return false;
            })
            .attr("class", "hidden");
    });
    
    force.start();
    
    if (true) {
        if (relatedSessionAdded) {
            svg.transition().duration(500)
                .attr("viewBox", "0 0 " + w + " " + h);
        }
        setTimeout(function() {
            force.stop();
            setGraphVizLocs();
            /*if (relatedSessionAdded) {
                svg.transition().delay(500).duration(750)
                    .attr("viewBox", "400 0 " + w + " " + h);
                relatedSessionAdded = false;
            }*/
        }, 1000);
    }
}

// start visualization
Ext.onReady(function() {
    force = d3.layout.force()
        .nodes(nodes)
        .links(links)
        .size([w, h])
        .linkDistance(150)
        .charge(-500)
        .on("tick", tick);
    
    svg = d3.select("#chart").append("svg")
        .attr("width", w)
        .attr("height", h)
        .attr("viewBox", "0 0 " + w + " " + h);
    
    // Per-type markers, as they don't inherit styles.
    defs = svg.append("defs");
    
    // customize marker for input paths
    defs.append("marker")
        .attr("id", "input")
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 30)
        .attr("refY", -2.5)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
      .append("path")
        .attr("d", "M0,-5L10,0L0,5");
    
    // customize marker for output paths
    defs.append("marker")
        .attr("id", "output")
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 15)
        .attr("refY", -1)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
      .append("path")
        .attr("d", "M0,-5L10,0L0,5");
    
    // customize marker for triggered paths
    defs.append("marker")
        .attr("id", "triggered")
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 19)
        .attr("refY", -1.5)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
      .append("path")
        .attr("d", "M0,-5L10,0L0,5");
        
    // customize marker for controlled paths
    defs.append("marker")
        .attr("id", "controlled")
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 30)
        .attr("refY", -2.5)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
      .append("path")
        .attr("d", "M0,-5L10,0L0,5");
        
    // customize marker for related paths
    defs.append("marker")
        .attr("id", "related")
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 13)
        .attr("refY", -1)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
      .append("path")
        .attr("d", "M0,-5L10,0L0,5");
        
    // add def for info node
    defs.append("rect")
        .attr("id", "info")
        .attr("width", rectLength)
        .attr("height", rectLength);
    
    // add initial session viz
    addSessionViz("${sessionId}", null);
});

</script>

<div id="chart"/>
