/*!
 * Ext JS Library 3.4.0
 * Copyright(c) 2006-2011 Sencha Inc.
 * licensing@sencha.com
 * http://www.sencha.com/license
 */
var mapwin;
var overlaysArray = [];
var showGmapCalled = false;

Ext.onReady(function() {
    
    // create the window on the first click and reuse on subsequent clicks
    if(!mapwin){

        mapwin = new Ext.Window({
            id: 'gmapwin',
            resizable: false,
            modal: true,
            layout: 'fit',
            title: 'GMap Window',
            closable: true,
            closeAction: 'hide',
            width:600,
            height:575,
            items: {
                xtype: 'gmappanel',
                region: 'center',
                zoomLevel: 2,
                gmapType: 'map',
                id: 'gmappanel',
                mapConfOpts: ['enableScrollWheelZoom','enableDoubleClickZoom','enableDragging'],
                mapControls: ['GSmallMapControl','GMapTypeControl','NonExistantControl'],
                setCenter: {
                    lat: 1,
                    lng: 1
                },
                buttons: [{
                    text: 'Close',
                    handler: function(){
                                Ext.get('gmapwin').fadeOut(
                                    {
                                        callback: function() {
                                            Ext.getCmp('gmapwin').hide();
                                        }
                                    });
                    }
                }],
                listeners: {
                    resize: function(t){
                      if (window.google && window.google.maps){
                        t.geoCodeLookup('4 Yawkey Way, Boston, MA, 02215-3409, USA', undefined, false, true, undefined);
                      }
                    }
                }
            }
        });
    }

    // show very quickly to render map then hide; should not see it
    mapwin.show();
    mapwin.hide();
});
    
// A Rectangle is a simple overlay that outlines a lat/lng bounds on the
// map. It has a border of the given weight and color and can optionally
// have a semi-transparent background color.
function Rectangle(map, bounds, opt_weight, opt_color) {
    this.bounds_ = bounds;
    this.weight_ = opt_weight || 2;
    this.color_ = opt_color || "yellow";
    this.map_ = map;
    this.div_ = null;
    this.setMap(map);
}

Rectangle.prototype = new google.maps.OverlayView();

// Creates the DIV representing this rectangle.
Rectangle.prototype.onAdd = function() {
    // Create the DIV representing our rectangle
    var div = document.createElement("div");
    div.style.border = this.weight_ + "px solid " + this.color_;
    div.style.position = "absolute";

    // set the overlay's div_ property to this div
    this.div_ = div;

    // Our rectangle is flat against the map, so we add our selves to the
    // MAP_PANE pane, which is at the same z-index as the map itself (i.e.,
    // below the marker shadows)
    var panes = this.getPanes();
    panes.overlayManager.appendChild(div);
}

Rectangle.prototype.draw = function() {
    var overlayProjection = this.getProjection();
    var sw = overlayProjection.fromLatLngToDivPixel(this.bounds_.getSouthWest());
    var ne = overlayProjection.fromLatLngToDivPixel(this.bounds_.getNorthEast());
    var div = this.div_;
    div.style.left = sw.x + 'px';
    div.style.top = ne.y + 'px';
    div.style.width = (ne.x - sw.x) + 'px';
    div.style.height = (sw.y - ne.y) + 'px';
}

// Remove the main DIV from the map pane
Rectangle.prototype.onRemove = function() {
    this.div_.parentNode.removeChild(this.div_);
    this.div_ = null;
}

function showGmap() {
    // show gmap window
    var gmapWin = Ext.getCmp('gmapwin');
    gmapWin.show();
    if(!Ext.isIE) Ext.get('gmapwin').fadeIn();

    // enable KeyDragZoom(bbox)
    var gmapPanel = Ext.getCmp('gmappanel');
    if (!showGmapCalled) {
        gmapPanel.gmap.enableKeyDragZoom({
            visualEnabled: true,
            visualPosition: google.maps.ControlPosition.LEFT,
            visualTips: { off: "Turn on bbox draw mode",
                          on: "Turn off bbox draw mode" }
        });
        
        // Application instance for showing user-feedback messages.
        //var App = new Ext.App({});
        //App.setAlert(App.STATUS_HELP, "Click on the bbox control " +
                     //"<img src='search_collections/dragzoom_btn_single.png'/> " +
                     //"below the zoom controls to enter \"bbox draw mode\" then " +
                     //"drag the crosshair cursor to draw the bounding box.");
    }
    showGmapCalled = true;
}
