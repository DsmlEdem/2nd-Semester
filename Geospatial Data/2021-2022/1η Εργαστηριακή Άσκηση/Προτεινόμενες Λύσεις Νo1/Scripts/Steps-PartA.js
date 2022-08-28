/* Imports */

var L8 = ee.ImageCollection("LANDSAT/LC08/C01/T1"),
    RuralPoly = /* color: #ffc82d */ee.Geometry.Polygon(
        [[[22.228811310219662, 39.58725757508273],
          [22.22760968058099, 39.57918731172176],
          [22.225034759926693, 39.57283627984354],
          [22.22760968058099, 39.55033836230569],
          [22.237394379067318, 39.54702922948955],
          [22.248380707192318, 39.55073544763807],
          [22.251642273354427, 39.5565591047423],
          [22.26434521524896, 39.563705652095315],
          [22.337129639077084, 39.58434709664977],
          [22.336614654946224, 39.61106598837618],
          [22.290609405922787, 39.6019403972742],
          [22.2858028873681, 39.61423982510321],
          [22.23035626261224, 39.60418884296668],
          [22.223318146157162, 39.59413640177958]]]),
    UrbanPoly = 
    /* color: #0b4a8b */
    /* shown: false */
    ee.Geometry.Polygon(
        [[[23.680978445530734, 38.02355664896413],
          [23.824487356663546, 37.953204589538075],
          [23.83341374826511, 38.03978215776635]]]);






/*  Part 1 of Lab 1 Steps 1-6   */

/*  Data for the year 2019      */

/*  Visualizations */

var RGB_viz = {min: '6500', max: '11000', bands: ['B4', 'B3', 'B2']};  // RGB visualization

var Pseudo_viz = {min: '6500', max: '15000', bands: ['B5', 'B4', 'B3']}; // Pseudo visualization

var NDVI_viz = {min: '-0.1', max: '0.35', bands: 'NDVI',
palette: 'orangered, yellow, green'}; // NDVI visualization

var NDWI_viz = {min : '-0.15', max: '0.25', bands : 'NDWI',
palette: 'orangered,yellow,green,lightblue,blue'};

var EVI_viz = {min: '-3', max: '1', bands: 'EVI', palette: 'brown, yellow, green'};

var NDVI_greenest_viz = {min: '-0.15', max: '0.55', bands: 'NDVI',
palette: 'orangered, yellow, green'}; 

var Season_viz = {min: '0', max: '366', bands: 'doy',
  palette: 'lightblue, green, F37637, orangered'
};

// Keep data with cloud cover <= 20 for year 2019

var unclouded_data = L8.filter(ee.Filter.lt('CLOUD_COVER', 20)).
filter(ee.Filter.date('2019-01-01', '2019-12-31'));

// Display unclouded data with RGB

Map.addLayer(unclouded_data, RGB_viz, 'RGB data 2019');

// Step 3 -  Keep data only on ROI

var unclouded_data_roi = unclouded_data.filter(ee.Filter.bounds(RuralPoly));

Map.addLayer(unclouded_data_roi, RGB_viz, 'RGB roi 2019');

print('The total number of images on roi is', unclouded_data_roi.size());
print('The JSON file of roi is the following', unclouded_data_roi);

// Step 4 - Image with lowest cloud cover

var unclouded_image = ee.Image(unclouded_data_roi.sort('CLOUD_COVER').first());

// Function to calculate NDVI

var addNDVI = function(image){
  // NDVI = (NIR - Red) / (NIR + Red)
  var ndvi = image.normalizedDifference(['B5', 'B4']).float().rename('NDVI');
  return image.addBands(ndvi);
};

var unclouded_image = addNDVI(unclouded_image);

Map.addLayer(unclouded_image, RGB_viz, 'Clearest Img RGB');
Map.addLayer(unclouded_image, Pseudo_viz, 'Clearest Img Pseudo');
Map.addLayer(unclouded_image, NDVI_viz, 'Clearest Img NDVI');

// Step 5 - Calculate EVI, NDWI indices

// A function to calculate all indices NDVI, NDWI, EVI

var calculate_indices = function(image){
  
  // EVI = 2.5*(NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1)
  var nir = image.select('B5');
  var red = image.select('B4');
  var blue = image.select('B2');
  var evi = (nir.multiply(2.5).subtract(red.multiply(2.5)).divide(nir.add(red.multiply(6)).
    add(blue.multiply(-7.5)).add(1))).rename('EVI');
  
  var ndvi = image.normalizedDifference(['B5', 'B4']).float().rename('NDVI');
  var ndwi = image.normalizedDifference(['B5', 'B6']).rename('NDWI');
  
  return image.addBands(ndvi).addBands(ndwi).addBands(evi);
};


var unclouded_data_roi = unclouded_data_roi.map(calculate_indices);

// Adding Layers with all indices NDVI, NDWI, EVI

Map.addLayer(unclouded_data_roi.select('NDWI'), NDWI_viz, 'NDWI for year 2019');
Map.addLayer(unclouded_data_roi.select('NDVI'), NDVI_viz, 'NDVI for year 2019');
Map.addLayer(unclouded_data_roi.select('EVI'), EVI_viz, 'EVI for year 2019');


// Step 6 - Greenest Pixels + Day of Year

//DOY for max ndvi
var addDOY = function(image){
  var img_date = ee.Date(image.date());
  var img_doy = ee.Number.parse(img_date.format('D'));
  return image.addBands(ee.Image(img_doy).rename('doy').toInt());
};

var greenest_pixels = unclouded_data_roi.map(addDOY).qualityMosaic('NDVI').select('NDVI', 'doy');

Map.addLayer(greenest_pixels, NDVI_greenest_viz, 'Greenest pixels for year 2019');


var seasonality_mapping = greenest_pixels.select('doy');

Map.addLayer(seasonality_mapping, Season_viz, 'Seasonality Mapping');


// Step 7 - all data - synthetic data

var all_data_ndvi = L8.filter(ee.Filter.bounds(RuralPoly)).
filter(ee.Filter.lt('CLOUD_COVER', 20)).map(addNDVI);



// Plot a time series of NDVI at a single location.
var l8Chart = ui.Chart.image.series(all_data_ndvi.select('NDVI'), RuralPoly)
    .setChartType('ScatterChart')
    .setOptions({
      title: 'Landsat 8 NDVI time series at ROI',
      trendlines: {0: {
        color: 'CC0000'
      }},
      lineWidth: 1,
      pointSize: 3,
    });
print(l8Chart);



// This field contains UNIX time in milliseconds.
var timeField = 'system:time_start';

// Use this function to add variables for NDVI, time and a constant
// to Landsat 8 imagery.
var addVariables = function(image) {
  // Compute time in fractional years since the epoch.
  var date = ee.Date(image.get(timeField));
  var years = date.difference(ee.Date('1970-01-01'), 'year');
  // Return the image with the added bands.
  return image
    // Add a time band.
    .addBands(ee.Image(years).rename('t').float())
    // Add a constant band.
    .addBands(ee.Image.constant(1));
};

var all_data_ndvi = all_data_ndvi.map(addVariables);


var print_harmonic_model = function(data, poly){ // A function to generate harmonic plot
  // Harmonic trend ----------------------------------------------------------------
  // Use these independent variables in the harmonic regression.
  var harmonicIndependents = ee.List(['constant', 't', 'cos', 'sin']);
  // Add harmonic terms as new image bands.
  var harmonicLandsat = data.map(function(image) {
    var timeRadians = image.select('t').multiply(2 * Math.PI);
    return image
      .addBands(timeRadians.cos().rename('cos'))
      .addBands(timeRadians.sin().rename('sin'));
  });
  
  // The output of the regression reduction is a 4x1 array image.
  var harmonicTrend = harmonicLandsat
    .select(harmonicIndependents.add('NDVI'))
    .reduce(ee.Reducer.linearRegression(harmonicIndependents.length(), 1));

  // Turn the array image into a multi-band image of coefficients.
  var harmonicTrendCoefficients = harmonicTrend.select('coefficients')
    .arrayProject([0])
    .arrayFlatten([harmonicIndependents]);
    
  // Compute fitted values.
  var fittedHarmonic = harmonicLandsat.map(function(image) {
    return image.addBands(
      image.select(harmonicIndependents)
        .multiply(harmonicTrendCoefficients)
        .reduce('sum')
        .rename('fitted'));
    
  });
  
  // Plot the fitted model and the original data at the ROI.
  print(ui.Chart.image.series(
    fittedHarmonic.select(['fitted','NDVI']), poly, ee.Reducer.mean(), 30)
      .setSeriesNames(['NDVI', 'fitted'])
      .setOptions({
        title: 'Harmonic model: original and fitted values',
        lineWidth: 1,
        pointSize: 3,
  }));
};

print_harmonic_model(all_data_ndvi, RuralPoly);

var urban_ndvi = L8.filter(ee.Filter.bounds(UrbanPoly)).
filter(ee.Filter.lt('CLOUD_COVER', 20)).map(addNDVI).map(addVariables);

print_harmonic_model(urban_ndvi, UrbanPoly);
  

