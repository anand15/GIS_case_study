// import roi to be used in classification
var aoi = ee.FeatureCollection("projects/shaurabh-urban-growth/assets/locations_buffer");

// A function that scales and masks Landsat 8 (C2) surface reflectance images.
function prepSrL8(image) {
  // Develop masks for unwanted pixels (fill, cloud, cloud shadow).
  var qaMask = image.select('QA_PIXEL').bitwiseAnd(parseInt('11111', 2)).eq(0);
  var saturationMask = image.select('QA_RADSAT').eq(0);

  // Apply the scaling factors to the appropriate bands.
  var getFactorImg = function(factorNames) {
    var factorList = image.toDictionary().select(factorNames).values();
    return ee.Image.constant(factorList);
  };
  var scaleImg = getFactorImg([
    'REFLECTANCE_MULT_BAND_.|TEMPERATURE_MULT_BAND_ST_B10']);
  var offsetImg = getFactorImg([
    'REFLECTANCE_ADD_BAND_.|TEMPERATURE_ADD_BAND_ST_B10']);
  var scaled = image.select('SR_B.|ST_B10').multiply(scaleImg).add(offsetImg);

  // Replace original bands with scaled bands and apply masks.
  return image.addBands(scaled, null, true)
    .updateMask(qaMask).updateMask(saturationMask);
}

// Landsat 8 Collection 2 surface reflectance images of interest for the year 2024
var col24 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
  .filterBounds(aoi)
  .filterDate('2024-01-01', '2024-04-30')
  .map(prepSrL8)
  .select('SR.*')
  .median();

print(col24)

var aoi_landsat24 = col24.clip(aoi)


// Select the bands to use for classification (Landsat 8)
var bands = ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7'];  // Adjust based on your needs
var image = aoi_landsat24.select(bands);

// Make the training dataset.
var training = image.sample({
  region: aoi,
  scale: 30,
  numPixels: 5000
});

// Instantiate the clusterer and train it.
var clusterer = ee.Clusterer.wekaKMeans(15).train(training);

// Cluster the input using the trained clusterer.
var result = image.cluster(clusterer);

// Export the classified image to Google Drive
Export.image.toDrive({
  image: result,
  description: 'filename',
  scale: 30,  // Landsat resolution (30 meters)
  region: aoi,
  maxPixels: 1e13,
  crs: 'EPSG:32644'
});
