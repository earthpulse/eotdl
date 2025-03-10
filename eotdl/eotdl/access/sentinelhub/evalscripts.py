"""
Evalscripts for Sentinel Hub requests
"""


class EvalScripts:
    """
    Class that defines the needed Sentinel Hub evalscripts
    """

    SENTINEL_1 = """
                //VERSION=3
                function setup() {
                    return {
                        input: [{
                            bands: ["VH", "VV"]
                        }],
                        output: {
                            id: "default",
                            bands: 2
                        }
                    };
                }

                function evaluatePixel(sample) {
                    return [sample.VH, sample.VV];
                }
                """

    SENTINEL_1_ENHANCED_VISUALIZATION = """
                //VERSION=3
                function setup() {
                return {
                    input: ["VV", "VH", "dataMask"],
                    output: { bands: 4 }
                }
                }

                function evaluatePixel(sample) {
                var water_threshold = 25; //lower means more water
                
                if (sample.VV / sample.VH > water_threshold) {
                    // watervis
                    return [sample.VV, 8 * sample.VV, 0.5 + 3 * sample.VV + 2000 * sample.VH, sample.dataMask];
                } else {
                    // landvis
                    return [3 * sample.VV, 1.1 * sample.VV + 8.75 * sample.VH, 1.75 * sample.VH, sample.dataMask];
                }
                }
                """

    SENTINEL_2_L1C = """
                //VERSION=3
                function setup() {
                    return {
                        input: [{
                            bands: ["B01",
                                    "B02",
                                    "B03",
                                    "B04",
                                    "B05",
                                    "B06",
                                    "B07",
                                    "B08",
                                    "B8A",
                                    "B09",
                                    "B10",
                                    "B11",
                                    "B12"],
                            units: "DN"
                        }],
                        output: {
                            bands: 13,
                            sampleType: "INT16"
                        }
                    };
                }

                function evaluatePixel(sample) {
                    return [sample.B01,
                            sample.B02,
                            sample.B03,
                            sample.B04,
                            sample.B05,
                            sample.B06,
                            sample.B07,
                            sample.B08,
                            sample.B8A,
                            sample.B09,
                            sample.B10,
                            sample.B11,
                            sample.B12];
                }
                """

    SENTINEL_2_L2A = """
                //VERSION=3
                function setup() {
                    return {
                        input: [{
                            bands: ["B01",
                                    "B02",
                                    "B03",
                                    "B04",
                                    "B05",
                                    "B06",
                                    "B07",
                                    "B08",
                                    "B8A",
                                    "B09",
                                    "B11",
                                    "B12"],
                            units: "DN"
                        }],
                        output: {
                            bands: 12,
                            sampleType: "INT16"
                        }
                    };
                }

                function evaluatePixel(sample) {
                    return [sample.B01,
                            sample.B02,
                            sample.B03,
                            sample.B04,
                            sample.B05,
                            sample.B06,
                            sample.B07,
                            sample.B08,
                            sample.B8A,
                            sample.B09,
                            sample.B11,
                            sample.B12];
                }
                """

    SENTINEL_2_L2A_TRUE_COLOR = """
        //VERSION=3
        let minVal = 0.0;
        let maxVal = 0.4;

        let viz = new HighlightCompressVisualizer(minVal, maxVal);

        function setup() {
        return {
            input: ["B04", "B03", "B02","dataMask"],
            output: { bands: 4 }
        };
        }

        function evaluatePixel(samples) {
            let val = [samples.B04, samples.B03, samples.B02,samples.dataMask];
            return viz.processList(val);
        }
        """

    DEM = """
        //VERSION=3

        function setup() {
            return {
                input: ["DEM"],
                output: { id: "default",
                        bands: 1,
                        sampleType: SampleType.FLOAT32
                },
            }
        }

        function evaluatePixel(sample) {
            return [sample.DEM]
        }
        """

    DEM_TOPOGRAPHIC = """
        //VERSION=3
        // To set custom max and min values, set
        // defaultVis to false and choose your max and
        // min values. The color map will then be scaled
        // to those max and min values
        const defaultVis = true
        const max = 9000
        const min = -9000

        function setup() {
            return {
                input: ["DEM", "dataMask"],
                output: [
                    { id: "default", bands: 4, sampleTYPE: 'AUTO' },
                    { id: "index", bands: 1, sampleType: 'FLOAT32' },
                    { id: "dataMask", bands: 1 }
                ]
            };
        }

        function updateMap(max, min) {
            const numIntervals = map.length
            const intervalLength = (max - min) / (numIntervals - 1);
            for (let i = 0; i < numIntervals; i++) {
                map[i][0] = max - intervalLength * i
            }
        }

        const map = [
            [8000, 0xffffff],
            [7000, 0xf2f2f2],
            [6000, 0xe5e5e5],
            [5500, 0x493811],
            [5000, 0x5e4c26],
            [4500, 0x726038],
            [4000, 0x87724c],
            [3500, 0x998760],
            [3000, 0xad9b75],
            [2500, 0xc1af89],
            [2000, 0xd6c49e],
            [1500, 0xead8af],
            [1000, 0xfcedbf],
            [900, 0xaadda0],
            [800, 0xa5d69b],
            [700, 0x96ce8e],
            [600, 0x84c17a],
            [500, 0x7aba70],
            [400, 0x72b266],
            [300, 0x5ea354],
            [200, 0x4c933f],
            [100, 0x3d873d],
            [75, 0x357c3a],
            [50, 0x2d722d],
            [25, 0x266821],
            [10, 0x1e5e14],
            [0.01, 0x165407]
        ];

        if (!defaultVis) updateMap(max, min);
        // add ocean color
        map.push([-10000, 0x0f0f8c])
        const visualizer = new ColorMapVisualizer(map);

        function evaluatePixel(sample) {
            let val = sample.DEM;
            let imgVals = visualizer.process(val)

            // Return the 4 inputs and define content for each one
            return {
                default: [...imgVals, sample.dataMask],
                index: [val],
                dataMask: [sample.dataMask]
            };
        }
        """

    HLS_FALSE_COLOR = """
        //VERSION=3

        function setup() {
        return {
            input: ["NIR_Narrow", "Red", "Green", "dataMask"],
            output: { bands: 3 }
        };
        }

        function evaluatePixel(sample) {
        return [2.5 * sample.NIR_Narrow, 2.5 * sample.Red, 2.5 * sample.Green, sample.dataMask];
        }
        """

    HLS_TRUE_COLOR = """
        //VERSION=3

        function setup() {
            return {
                input: ["Blue","Green","Red", "dataMask"],
                output: { bands: 4 }
            };
        }

        function evaluatePixel(sample) {
            return [2.5 * sample.Red, 2.5 * sample.Green, 2.5 * sample.Blue, sample.dataMask];
        }
        """

    HLS_NDVI = """
        //VERSION=3

        function setup() { 
            return {
                input: ["NIR_Narrow", "Red", "dataMask"],
                output: { bands: 4 }
            };
        }

        function evaluatePixel(sample) {
            var ndvi = (sample.NIR_Narrow - sample.Red) / (sample.NIR_Narrow + sample.Red)

            if (ndvi<-1.1) return [0,0,0, sample.dataMask];
            else if (ndvi<-0.2) return [0.75,0.75,0.75, sample.dataMask];
            else if (ndvi<-0.1) return [0.86,0.86,0.86, sample.dataMask];
            else if (ndvi<0) return [1,1,0.88, sample.dataMask];
            else if (ndvi<0.025) return [1,0.98,0.8, sample.dataMask];
            else if (ndvi<0.05) return [0.93,0.91,0.71, sample.dataMask];
            else if (ndvi<0.075) return [0.87,0.85,0.61, sample.dataMask];
            else if (ndvi<0.1) return [0.8,0.78,0.51, sample.dataMask];
            else if (ndvi<0.125) return [0.74,0.72,0.42, sample.dataMask];
            else if (ndvi<0.15) return [0.69,0.76,0.38, sample.dataMask];
            else if (ndvi<0.175) return [0.64,0.8,0.35, sample.dataMask];
            else if (ndvi<0.2) return [0.57,0.75,0.32, sample.dataMask];
            else if (ndvi<0.25) return [0.5,0.7,0.28, sample.dataMask];
            else if (ndvi<0.3) return [0.44,0.64,0.25, sample.dataMask];
            else if (ndvi<0.35) return [0.38,0.59,0.21, sample.dataMask];
            else if (ndvi<0.4) return [0.31,0.54,0.18, sample.dataMask];
            else if (ndvi<0.45) return [0.25,0.49,0.14, sample.dataMask];
            else if (ndvi<0.5) return [0.19,0.43,0.11, sample.dataMask];
            else if (ndvi<0.55) return [0.13,0.38,0.07, sample.dataMask];
            else if (ndvi<0.6) return [0.06,0.33,0.04, sample.dataMask];
            else return [0,0.27,0, sample.dataMask];
        }
        """

    LANDSAT_OT_L2_TRUE_COLOR = """
        //VERSION=3

        let minVal = 0.0;
        let maxVal = 0.4;

        let viz = new DefaultVisualizer(minVal, maxVal);

        function evaluatePixel(samples) {
            let val = [samples.B04, samples.B03, samples.B02, samples.dataMask];
            return viz.processList(val);
        }

        function setup() {
            return {
                input: [{
                bands: [ "B02", "B03", "B04", "dataMask" ]
                }],
                output: { bands: 4 }  }
            }
        """
    LANDSAT_OT_L2_NDVI = """
        //VERSION=3
        
        function setup() {
        return {
            input: ["B03", "B04", "B05", "dataMask"],
            output: [
            { id: "default", bands: 4 },
            { id: "index", bands: 1, sampleType: "FLOAT32" },
            { id: "eobrowserStats", bands: 2 },
            { id: "dataMask", bands: 1 },
            ],
        };
        }

        function evaluatePixel(samples) {
        let val = index(samples.B05, samples.B04);
        let imgVals = null;
        // The library for tiffs works well only if there is only one channel returned.
        // So we encode the "no data" as NaN here and ignore NaNs on frontend.
        const indexVal = samples.dataMask === 1 && val >= -1 && val <= 1 ? val : NaN;

        if (val < -1.1) imgVals = [0, 0, 0, samples.dataMask];
        else if (val < -0.2) imgVals = [0.75, 0.75, 0.75, samples.dataMask];
        else if (val < -0.1) imgVals = [0.86, 0.86, 0.86, samples.dataMask];
        else if (val < 0) imgVals = [1, 1, 0.88, samples.dataMask];
        else if (val < 0.025) imgVals = [1, 0.98, 0.8, samples.dataMask];
        else if (val < 0.05) imgVals = [0.93, 0.91, 0.71, samples.dataMask];
        else if (val < 0.075) imgVals = [0.87, 0.85, 0.61, samples.dataMask];
        else if (val < 0.1) imgVals = [0.8, 0.78, 0.51, samples.dataMask];
        else if (val < 0.125) imgVals = [0.74, 0.72, 0.42, samples.dataMask];
        else if (val < 0.15) imgVals = [0.69, 0.76, 0.38, samples.dataMask];
        else if (val < 0.175) imgVals = [0.64, 0.8, 0.35, samples.dataMask];
        else if (val < 0.2) imgVals = [0.57, 0.75, 0.32, samples.dataMask];
        else if (val < 0.25) imgVals = [0.5, 0.7, 0.28, samples.dataMask];
        else if (val < 0.3) imgVals = [0.44, 0.64, 0.25, samples.dataMask];
        else if (val < 0.35) imgVals = [0.38, 0.59, 0.21, samples.dataMask];
        else if (val < 0.4) imgVals = [0.31, 0.54, 0.18, samples.dataMask];
        else if (val < 0.45) imgVals = [0.25, 0.49, 0.14, samples.dataMask];
        else if (val < 0.5) imgVals = [0.19, 0.43, 0.11, samples.dataMask];
        else if (val < 0.55) imgVals = [0.13, 0.38, 0.07, samples.dataMask];
        else if (val < 0.6) imgVals = [0.06, 0.33, 0.04, samples.dataMask];
        else imgVals = [0, 0.27, 0, samples.dataMask];

        return {
            default: imgVals,
            index: [indexVal],
            eobrowserStats: [val, isCloud(samples) ? 1 : 0],
            dataMask: [samples.dataMask],
        };
        }

        function isCloud(samples) {
        const NGDR = index(samples.B03, samples.B04);
        const bRatio = (samples.B03 - 0.175) / (0.39 - 0.175);
        return bRatio > 1 || (bRatio > 0 && NGDR > 0);
        }
        """
