/* Imports */

var L8 = ee.ImageCollection("LANDSAT/LC08/C01/T1"),
    RGB_viz = {"min":"6500","max":"11000","bands":["B4","B3","B2"]},
    Pseudo_viz = {"min":"5000","max":"15000","bands":["B5","B4","B3"]},
    NDWI_viz = {"min":"-0.2","max":"0.15","bands":"NDWI","palette":"yellow, green, lightblue, blue"},
    NDVI_viz = {"min":"-0.15","max":"0.55","bands":"NDVI","palette":"orangered, yellow, green"},
    NDVI_greenest_viz = {"min":"-0.15","max":"0.55","bands":"NDVI","palette":"orangered, yellow, green"},
    geometry = /* color: #23cba7 */ee.Geometry.MultiPoint();



/* End of Imports */




var drawingTools = Map.drawingTools();


//drawingTools.setShown(false);


while (drawingTools.layers().length() > 0) {
  var layer = drawingTools.layers().get(0);
  drawingTools.layers().remove(layer);
}

var dummyGeometry =
    ui.Map.GeometryLayer({geometries: null, name: 'geometry', color: '23cba7'});

drawingTools.layers().add(dummyGeometry);


function clearGeometry() {
  var layers = drawingTools.layers();
  var num_geoms = layers.get(0).geometries().length();
  if (num_geoms > 1){
    layers.get(0).geometries().remove(layers.get(0).geometries().get(num_geoms-1));
  }else{
    layers.get(0).geometries().remove(layers.get(0).geometries().get(0));
  }
}

function remove_layer() {
  var num_layers = Map.layers().length();
  if (num_layers > 0){
    Map.remove(Map.layers().get(num_layers - 1));
  }else{
    print('No layers to erase!');
  }
}


function drawRectangle() {
  clearGeometry();
  drawingTools.setShape('rectangle');
  drawingTools.draw();
}

function drawPolygon() {
  clearGeometry();
  drawingTools.setShape('polygon');
  drawingTools.draw();
}

// RGB Layer

function rgb(){
  var layers = drawingTools.layers();
  var num_geoms = layers.get(0).geometries().length();
  if (num_geoms === 0){
    print('Draw a geometry first!');
  }else{
    var aoi = drawingTools.layers().get(0).getEeObject();
    var unclouded_data = L8.filter(ee.Filter.lt('CLOUD_COVER', 20)).
    filter(ee.Filter.date('2019-01-01', '2019-12-31')).filter(ee.Filter.bounds(aoi)).median().clip(aoi);
    Map.addLayer(unclouded_data, RGB_viz, 'RGB color');
  }
}

// False Color Layer


function pseudo_color(){
  var layers = drawingTools.layers();
  var num_geoms = layers.get(0).geometries().length();
    if (num_geoms === 0){
    print('Draw a geometry first!');
  }else{
    var aoi = drawingTools.layers().get(0).getEeObject();
    var unclouded_data = L8.filter(ee.Filter.lt('CLOUD_COVER', 20)).
    filter(ee.Filter.date('2019-01-01', '2019-12-31')).filter(ee.Filter.bounds(aoi)).median().clip(aoi);
    Map.addLayer(unclouded_data, Pseudo_viz, 'Pseudo Color');
  }
}

// Median NDWI Layer

var addNDWI = function(image){
  var ndwi = image.normalizedDifference(['B3', 'B5']).rename('NDWI');
  return image.addBands(ndwi);
};

function ndwi(){
  var layers = drawingTools.layers();
  var num_geoms = layers.get(0).geometries().length();
  if (num_geoms === 0){
    print('Draw a geometry first!');
  }else{
    var aoi = drawingTools.layers().get(0).getEeObject();
    var unclouded_data = L8.filter(ee.Filter.lt('CLOUD_COVER', 20)).
    filter(ee.Filter.date('2019-01-01', '2019-12-31')).filter(ee.Filter.bounds(aoi)).map(addNDWI)
    .median().clip(aoi);
    Map.addLayer(unclouded_data, NDWI_viz, 'Median NDWI');
  }
}

// Median NDVI Layer

function ndvi() {
  var layers = drawingTools.layers();
  var num_geoms = layers.get(0).geometries().length();
    if (num_geoms === 0){
    print('Draw a geometry first!');
  }else{
    var aoi = drawingTools.layers().get(0).getEeObject();
    var unclouded_data = L8.filter(ee.Filter.lt('CLOUD_COVER', 20)).
    filter(ee.Filter.date('2019-01-01', '2019-12-31')).filter(ee.Filter.bounds(aoi)).map(addNDVI)
    .median().clip(aoi);
    Map.addLayer(unclouded_data, NDVI_viz, 'Median NDVI');
  }
}

// Greenest Layer

var addNDVI = function(image){
  // NDVI = (NIR - Red) / (NIR + Red)
  var ndvi = image.normalizedDifference(['B5', 'B4']).float().rename('NDVI');
  return image.addBands(ndvi);
};

function greenest() {
  var layers = drawingTools.layers();
  var num_geoms = layers.get(0).geometries().length();
  if (num_geoms === 0){
    print('Draw a geometry first!');
  }else{
    var aoi = drawingTools.layers().get(0).getEeObject();
    var unclouded_data = L8.filter(ee.Filter.lt('CLOUD_COVER', 20)).
    filter(ee.Filter.date('2019-01-01', '2019-12-31')).filter(ee.Filter.bounds(aoi)).map(addNDVI)
    .qualityMosaic('NDVI').clip(aoi);
    Map.addLayer(unclouded_data, NDVI_greenest_viz, 'Greenest on roi');
  }
}

var symbol = {
  rectangle: '⬛',
  polygon: '🔺',
};

var controlPanel = ui.Panel({
  widgets: [
    ui.Label('1. Draw a geometry.'),
    ui.Button({
      label: symbol.rectangle + ' Rectangle',
      onClick: drawRectangle,
      style: {stretch: 'horizontal'}
    }),
    ui.Button({
      label: symbol.polygon + ' Polygon',
      onClick: drawPolygon,
      style: {stretch: 'horizontal'}
    }),
    ui.Button({
      label: 'Erase Geometry',
      onClick: clearGeometry,
      style: {stretch: 'horizontal'}
    }),
    ui.Label('2. Choose Layer.'),
    ui.Button({
      label: 'RGB',
      onClick: rgb,
      style: {stretch: 'horizontal'}
    }),
    ui.Button({
      label: 'Greenest',
      onClick: greenest,
      style: {stretch: 'horizontal'}
    }),
    ui.Button({
      label: 'Median NDVI',
      onClick: ndvi,
      style: {stretch: 'horizontal'}
    }),
    ui.Button({
      label: 'Median NDWI',
      onClick: ndwi,
      style: {stretch: 'horizontal'}
    }),
    ui.Button({
      label: 'Pseudo color',
      onClick: pseudo_color,
      style: {stretch: 'horizontal'}
    }),
    ui.Button({
      label: 'Erase Layer',
      onClick: remove_layer,
      style: {stretch: 'horizontal'}
    })
    
  ],
  style: {position: 'bottom-left'},
  layout: null,
});


/*
 * Add a title and initialize
 */

// Create a title.
var title = ui.Label('Year 2019 Landsat 8 - Visualizations', {
  stretch: 'horizontal',
  textAlign: 'center',
  fontWeight: 'bold',
  fontSize: '24px'
});

// Add the maps and title to the ui.root.
Map.add(title);

Map.add(controlPanel);

