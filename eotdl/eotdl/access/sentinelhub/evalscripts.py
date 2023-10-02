'''
Evalscripts for Sentinel Hub requests
'''


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
    
    SENTINEL_2 = """
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
