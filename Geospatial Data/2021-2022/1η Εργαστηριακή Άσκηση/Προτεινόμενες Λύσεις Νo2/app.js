var geometry = /* color: #23cba7 */ee.Geometry.Point([25.211027123320363, 39.9235275258044]);

var addQualityBands = function (image) {
    var ndvi = image.normalizedDifference(['B5', 'B4']).rename('NDVI');
    var evi = image.expression(
      '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
      {
        'NIR': image.select('B5'),
        'RED': image.select('B4'),
        'BLUE': image.select('B2')
      }
    ).rename('EVI');
    var ndwi = image.normalizedDifference(['B3', 'B5']).rename('NDWI');
    return image.addBands([ndvi, evi, ndwi]);
  };
  
  var addConstant = function (image) {
    return image.addBands(ee.Image(1).rename('constant'));
  };
  
  var addTime = function (image) {
    // Compute time in fractional years since the epoch.
    var date = image.date();
    var years = date.difference(ee.Date('1970-01-01'), 'year');
    var timeRadians = ee.Image(years.multiply(2 * Math.PI));
    return image.addBands(timeRadians.rename('t').float());
  };
  
  var getNames = function (base, nHarmonics) {
    return ee.List.sequence(1, nHarmonics).map(function (i) {
      return ee.String(base).cat(ee.Number(i).int());
    });
  };
  
  var addHarmonics = function (nHarmonics) {
    var freqs = ee.List.sequence(1, nHarmonics);
    var cosNames = getNames('cos_', nHarmonics);
    var sinNames = getNames('sin_', nHarmonics);
    return function (image) {
      var freqBands = ee.Image.constant(freqs);  // one band for each freq
      var time = ee.Image(image).select('t');
      var cosines = time.multiply(freqBands).cos().rename(cosNames);
      var sines = time.multiply(freqBands).sin().rename(sinNames);
      return image.addBands(cosines).addBands(sines);
    };
  };
  
  
  var fitHarmonics = function (data, nHarmonics, dependent) {
    var cosNames = getNames('cos_', nHarmonics);
    var sinNames = getNames('sin_', nHarmonics);
    var independents = ee.List(['constant', 't']).cat(cosNames).cat(sinNames);
    var coeffs = data
      .select(independents.add(dependent))
      .reduce(ee.Reducer.linearRegression(independents.length(), 1))
      .select('coefficients')
      .arrayProject([0])
      .arrayFlatten([independents]);
    return data.map(function (image) {
      return image.addBands(
        image.select(independents)
          .multiply(coeffs)
          .reduce('sum')
          .rename('fitted'));
    });
  };
  
  
  // https://developers.google.com/earth-engine/tutorials/community/drawing-tools-region-reduction
  var drawingTools = Map.drawingTools();
  drawingTools.setShown(false);
  
  // Clear previous drawings
  while (drawingTools.layers().length() > 0) {
    var layer = drawingTools.layers().get(0);
    drawingTools.layers().remove(layer);
  }
  
  // Initialize a dummy GeometryLayer with null geometry to act as a placeholder for drawn geometries.
  var dummyGeometry =
    ui.Map.GeometryLayer({ geometries: null, name: 'geometry', color: '23cba7' });
  drawingTools.layers().add(dummyGeometry);
  
  // Callbacks
  function clearGeometry() {
    var layers = drawingTools.layers();
    layers.get(0).geometries().remove(layers.get(0).geometries().get(0));
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
  
  function drawPoint() {
    clearGeometry();
    drawingTools.setShape('point');
    drawingTools.draw();
  }
  
  // Create the pannel where the Chart is shown (invisible until the first chart is rendered)
  var chartPanel = ui.Panel({
    style:
      { height: '235px', width: '600px', position: 'bottom-right', shown: false }
  });
  Map.add(chartPanel);
  
  var bandSelector = ui.Select({
    items: ['NDVI', 'EVI', 'NDWI'],
    placeholder: 'Select a Quality Band',
    value: 'NDVI'
  });
  
  var harmonicsSelector = ui.Select({
    items: ['1', '2', '3', '4', '5'],
    placeholder: 'Select num harmonics',
    value: '3'
  });
  
  function chartTimeSeries() {
    // Make the chart panel visible the first time a geometry is drawn.
    if (!chartPanel.style().get('shown')) {
      chartPanel.style().set('shown', true);
    }
  
    // Get the drawn geometry; it will define the reduction region.
    var aoi = drawingTools.layers().get(0).getEeObject();
  
    // Set the drawing mode back to null; turns drawing off.
    drawingTools.setShape(null);
  
    // Reduction scale is based on map scale to avoid memory/timeout errors.
    var mapScale = Map.getScale();
    var scale = mapScale > 5000 ? mapScale * 2 : 5000;
  
    // Get the quality band to be plotted
    var dependent = bandSelector.getValue();
  
    // Get the number of harmonics to be fitted
    var nHarmonics = parseInt(harmonicsSelector.getValue(), 10);
  
    var data = ee.ImageCollection('LANDSAT/LC08/C01/T1')
      .filter(ee.Filter.lt('CLOUD_COVER', 20))
      .map(addQualityBands)
      .map(addConstant).map(addTime).map(addHarmonics(nHarmonics));
    data = fitHarmonics(data, nHarmonics, dependent);
  
    // Chart time series for the selected area of interest.
    var chart = ui.Chart.image
      .series(
        data.select(['fitted', dependent]),
        aoi, ee.Reducer.mean(), scale)
      .setOptions({
        title: 'Harmonic model: original and fitted values (' + nHarmonics + ' harmonics)',
        hAxis: { title: 'Date' },
        vAxis: { title: dependent },
        lineWidth: 1,
        pointSize: 3
      });
  
    // Replace the existing chart in the chart panel with the new chart.
    chartPanel.widgets().reset([chart]);
  }
  
  // Set listeners. Debounce makes the function to be called at most once every 500 ms
  drawingTools.onDraw(ui.util.debounce(chartTimeSeries, 500));
  drawingTools.onEdit(ui.util.debounce(chartTimeSeries, 500));
  var redrawIfDrawn = function () {
    if (chartPanel.style().get('shown')) chartTimeSeries();
  }
  bandSelector.onChange(redrawIfDrawn);
  harmonicsSelector.onChange(redrawIfDrawn);
  
  // User Interface
  var symbol = {
    rectangle: '⬛',
    polygon: '🔺',
    point: '📍',
  };
  
  var controlPanel = ui.Panel({
    widgets: [
      ui.Label('1. Select quality band'),
      bandSelector,
      ui.Label('2. Select harmonics'),
      harmonicsSelector,
      ui.Label('3. Select a drawing mode.'),
      ui.Button({
        label: symbol.rectangle + ' Rectangle',
        onClick: drawRectangle,
        style: { stretch: 'horizontal' }
      }),
      ui.Button({
        label: symbol.polygon + ' Polygon',
        onClick: drawPolygon,
        style: { stretch: 'horizontal' }
      }),
      ui.Button({
        label: symbol.point + ' Point',
        onClick: drawPoint,
        style: { stretch: 'horizontal' }
      }),
      ui.Label('4. Draw a geometry.'),
      ui.Label('5. Wait for chart to render.'),
      ui.Label(
        '6. Repeat 1-5 or edit/move\ngeometry for a new chart.',
        { whiteSpace: 'pre' }),
    ],
    style: { position: 'bottom-left' },
    layout: null,
  });
  
  Map.add(controlPanel);