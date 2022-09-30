// IMPORTS
var l8 = ee.ImageCollection("LANDSAT/LC08/C01/T1_TOA"),
    aoi =
        /* color: #ff06db */
        /* shown: false */
        /* displayProperties: [
          {
            "type": "rectangle"
          }
        ] */
        ee.Geometry.Polygon(
            [[[22.167981530434947, 39.88956546831169],
            [22.167981530434947, 39.46679033875962],
            [22.986462975747447, 39.46679033875962],
            [22.986462975747447, 39.88956546831169]]], null, false),
    water =
        /* color: #aec3d4 */
        /* shown: false */
        /* displayProperties: [
          {
            "type": "rectangle"
          },
          {
            "type": "rectangle"
          }
        ] */
        ee.Geometry.MultiPolygon(
            [[[[22.808742141083965, 39.502764254564426],
            [22.808742141083965, 39.47732865085638],
            [22.850627517060527, 39.47732865085638],
            [22.850627517060527, 39.502764254564426]]],
            [[[22.921193509183556, 39.659993707477874],
            [22.921193509183556, 39.624038821007815],
            [22.976125149808556, 39.624038821007815],
            [22.976125149808556, 39.659993707477874]]]], null, false),
    cropland =
        /* color: #cdb33b */
        /* shown: false */
        /* displayProperties: [
          {
            "type": "rectangle"
          }
        ] */
        ee.Geometry.Polygon(
            [[[22.6917256766282, 39.54117596679023],
            [22.6917256766282, 39.513370676356814],
            [22.734984343620386, 39.513370676356814],
            [22.734984343620386, 39.54117596679023]]], null, false),
    forest =
        /* color: #387242 */
        /* shown: false */
        /* displayProperties: [
          {
            "type": "rectangle"
          }
        ] */
        ee.Geometry.Polygon(
            [[[22.75111645215788, 39.639330568005924],
            [22.75111645215788, 39.60468753476372],
            [22.8015848969821, 39.60468753476372],
            [22.8015848969821, 39.639330568005924]]], null, false),
    urban =
        /* color: #cc0013 */
        /* shown: false */
        /* displayProperties: [
          {
            "type": "rectangle"
          }
        ] */
        ee.Geometry.Polygon(
            [[[22.41138267974303, 39.642188317437],
            [22.41138267974303, 39.62686948051071],
            [22.432046417993764, 39.62686948051071],
            [22.432046417993764, 39.642188317437]]], null, false),
    barren =
        /* color: #f7e084 */
        /* shown: false */
        /* displayProperties: [
          {
            "type": "rectangle"
          }
        ] */
        ee.Geometry.Polygon(
            [[[22.229529548781247, 39.78055743048465],
            [22.229529548781247, 39.75495982564443],
            [22.26592176069531, 39.75495982564443],
            [22.26592176069531, 39.78055743048465]]], null, false);


// 2. SHOW TRUE AND FALSE COLOR IMAGES OF 2019

var outputURLs = false;
var urlParams = { region: aoi, dimensions: 1000, format: 'png' };

var mergeDicts = function (a, b) {
    var res = {};
    for (var x in a) {
        res[x] = a[x];
    }
    for (var y in b) {
        res[y] = b[y];
    }
    return res;
};

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

var leastCloudy2019 = l8
    .map(addQualityBands)
    .filterBounds(aoi)
    .filterDate(ee.Date('2019').getRange('year'))
    .sort('CLOUD_COVER', false)
    .mosaic();

var rgbVisParams = { bands: ['B4', 'B3', 'B2'], max: 0.3 };
var pseudVisParams = { bands: ['B5', 'B4', 'B3'], max: 0.3 };
var ndviVisParams = { bands: ['NDVI'], palette: ['blue', 'white', 'green'], min: -1, max: 1 };

Map.centerObject(aoi);
Map.addLayer(leastCloudy2019.clip(aoi), rgbVisParams, 'Clearest True RGB 2019');
Map.addLayer(leastCloudy2019.clip(aoi), pseudVisParams, 'Clearest Pseudo RGB 2019');
Map.addLayer(leastCloudy2019.clip(aoi), ndviVisParams, 'Clearest NDVI 2019');

if (outputURLs) {
    print('Clearest True RGB 2019', leastCloudy2019.getThumbURL(mergeDicts(rgbVisParams, urlParams)));
    print('Clearest Pseudo RGB 2019', leastCloudy2019.getThumbURL(mergeDicts(pseudVisParams, urlParams)));
    print('Clearest NDVI 2019', leastCloudy2019.getThumbURL(mergeDicts(ndviVisParams, urlParams)));
}


// 3. SHOW MAX NDVI for 2018 and 2019. ALSO SHOW THE DAY OF THE YEAR.

var addDOY = function (image) {
    var doy = image.date().getRelative('day', 'year');
    var doyBand = ee.Image.constant(doy).uint16().rename('DOY');
    return image.addBands(doyBand);
};

var doyVisParams = { bands: ['DOY'], palette: ['white', 'blue'], min: 0, max: 366 };

['2018', '2019'].forEach(function (year) {
    var greenest = l8
        .map(addQualityBands)
        .filterBounds(aoi)
        .filter(ee.Filter.lt('CLOUD_COVER', 20))
        .map(addDOY)
        .filterDate(ee.Date(year).getRange('year'))
        .qualityMosaic('NDVI');
    Map.addLayer(greenest.clip(aoi), rgbVisParams, 'Greenest True RGB ' + year);
    Map.addLayer(greenest.clip(aoi), ndviVisParams, 'Max NDVI ' + year);
    Map.addLayer(greenest.clip(aoi), doyVisParams, 'DOY ' + year);

    if (outputURLs) {
        print('Greenest True RGB ' + year, greenest.getThumbURL(mergeDicts(rgbVisParams, urlParams)));
        print('Max NDVI ' + year, greenest.getThumbURL(mergeDicts(ndviVisParams, urlParams)));
        print('DOY ' + year, greenest.getThumbURL(mergeDicts(doyVisParams, urlParams)));
    }
});


// 4. PLOT NDVI TIME SERIES ALONGSIDE WITH THE FITTED HARMONICS

var addConstant = function (image) {
    return image.addBands(ee.Image(1).rename('constant'));
};

var addTime = function (image) {
    var date = image.date();
    var years = date.difference(ee.Date('1970-01-01'), 'year');
    var timeRadians = ee.Image(years.multiply(2 * Math.PI));
    return image.addBands(timeRadians.rename('t').float());
};

var getNames = function (base, nHarmonics) {
    // returns base_1, base_2, ..., base_nHarmonics
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

var nHarmonics = 3;
var dependent = 'NDVI';

var fitted = fitHarmonics(
    l8
        .filter(ee.Filter.lt('CLOUD_COVER', 20))
        .map(addQualityBands)
        .map(addConstant).map(addTime).map(addHarmonics(nHarmonics)),
    nHarmonics,
    dependent
);

var makeChart = function (region, name) {
    return ui.Chart.image
        .series(
            fitted.select(['fitted', dependent]),
            region, ee.Reducer.mean(), 30)
        .setOptions({
            title: name + ' ' + dependent + ' (' + nHarmonics + ' harmonics)',
            hAxis: { title: 'Date' },
            vAxis: { title: dependent },
            lineWidth: 1,
            pointSize: 3
        });
};

var d = { 'Forest': forest, 'Cropland': cropland, 'Barren': barren, 'Urban': urban };
for (var key in d) {
    var chart = makeChart(d[key], key);
    print(chart);
}


// 5. CLASSIFY REGIONS

var image = l8
    .map(addQualityBands)
    .filterDate(ee.Date('2019').getRange('year'))
    .filterBounds(aoi)
    .filter(ee.Filter.lt('CLOUD_COVER', 20))
    .median();

var trainPolygons = [water, cropland, forest, urban, barren];  // classes 0, 1, ... , K
var colors = ['aec3d4', 'cdb33b', '387242', 'cc0013', 'f7e084'];
var addClass = function (i) { return function (feature) { return feature.set({ 'class': i }) } };
var fcs = [];
trainPolygons.forEach(function (polygon, i) {
    var fc = ee.FeatureCollection.randomPoints(polygon, 1000, 42).map(addClass(i));
    fcs.push(fc);
});
var points = ee.FeatureCollection(fcs).flatten();
var bands = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B10'];
var training = image.select(bands).sampleRegions({
    collection: points,
    properties: ['class'],
    scale: 30
});

var svm = ee.Classifier.libsvm({
    kernelType: 'RBF',
    gamma: 0.5,
    cost: 10
});
svm = svm.train(training, 'class', bands);
print('SVM confusion matrix:', svm.confusionMatrix());
var svmPred = image.classify(svm);

var rf = ee.Classifier.smileRandomForest(10);
rf = rf.train(training, 'class', bands);
print('Random Forest confusion matrix:', rf.confusionMatrix());
print('Random Forest explanation:', rf.explain());
var rfPred = image.classify(rf);

var classVisParams = { min: 0, max: (colors.length - 1), palette: colors };
Map.addLayer(image.clip(aoi),
    rgbVisParams,
    'Median True RGB 2019');
Map.addLayer(svmPred.clip(aoi),
    classVisParams,
    'SVM Predictions 2019');
Map.addLayer(rfPred.clip(aoi),
    classVisParams,
    'Random Forest Predictions 2019');

var corineLC = ee.Image('COPERNICUS/CORINE/V20/100m/2018').select('landcover');
Map.addLayer(corineLC.clip(aoi), {}, 'CORINE Landcover 2018');

if (outputURLs) {
    print('Median True RGB 2019', image.getThumbURL(mergeDicts(rgbVisParams, urlParams)));
    print('SVM Predictions 2019', svmPred.getThumbURL(mergeDicts(classVisParams, urlParams)));
    print('Random Forest Predictions 2019', rfPred.getThumbURL(mergeDicts(classVisParams, urlParams)));
}

