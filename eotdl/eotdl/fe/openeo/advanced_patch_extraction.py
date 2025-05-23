from .dataframe_utils import *
import openeo
from openeo.extra.job_management import MultiBackendJobManager, CsvJobDatabase
from .s3proxy_utils import upload_geoparquet_file
import geojson

def start_job(row: pd.Series, connection: openeo.Connection, **kwargs) -> openeo.BatchJob:

        temporal_extent = eval(row["temporal_extent"])
        crs = row['crs']

        # set up load url in order to allow non-latlon feature collections for spatial filtering
        geometry = geojson.loads(row["geometry"])
        features = gpd.GeoDataFrame.from_features(geometry).set_crs(crs)
        url = upload_geoparquet_file(features,connection)

        #run the s1 and s2 udp
        s1 = connection.datacube_from_process(
                "s1_weekly_statistics",
                namespace="https://raw.githubusercontent.com/earthpulse/eotdl/refs/heads/hv_openeoexample/tutorials/notebooks/openeo/s1_weekly_statistics.json",
                temporal_extent=temporal_extent,
                )
        
        s2 = connection.datacube_from_process(
                "s2_weekly_statistics",
                namespace="https://raw.githubusercontent.com/earthpulse/eotdl/refs/heads/hv_openeoexample/tutorials/notebooks/openeo/s2_weekly_statistics.json",
                temporal_extent=temporal_extent,
                )
        
        #merge both cubes and filter across the feature collection
        merged = s2.merge_cubes(s1)
        result = merged.filter_spatial(connection.load_url(url, format="Parquet"))
        
        #dedicated job settings to save the individual features within a collection seperately
        job = result.create_job(
                out_format="NetCDF",
                sample_by_feature = True,
                feature_id_property="id",
                filename_prefix = "eotdl"
        )

        return job

def patch_extraction(
        gdf,
        start_date,
        nb_months,
        pixel_size = 64,
        resolution = 10,
        max_points = 5,
        job_tracker = 'jobs.csv',
        parallel_jobs=2
):
        """
        # Transform GeoDataFrame for MultiBackendJobManager

        This function processes an input GeoDataFrame and prepares it for use with openEO's **MultiBackendJobManager**. The job manager enables launching and tracking multiple openEO jobs simultaneously, which is essential for large-scale data extractions. 

        ### Example Use Case
        The function creates patches (e.g., 64x64 pixels) around polygon centers. These patches are suitable for machine learning applications, such as training convolutional neural networks (CNNs).  
        By combining patches into Sentinel-2 grid collections, the workflow ensures cost efficiency and optimized data extraction.

        ### Workflow

        1. **Process the GeoDataFrame**  
        - Create patches with a fixed size around the center of polygon geometries.  
        - Calculate temporal extents for each geometry.  

        2. **Combine Features Using Sentinel-2 Tiling**  
        - Group buffered geometries into collections based on the Sentinel-2 tiling grid.  
        - Minimize redundant openEO cost.  

        3. **Generate Job Metadata DataFrame**  
        - Convert processed data into a DataFrame, ready for the MultiBackendJobManager.

        ### Parameters

        #### Spatial Parameters:
        - **Buffer Distance:** Buffer size (e.g., 320 meters for a 64x64 patch around polygon centers).  
        - **Resolution:** Spatial alignment resolution in meters.

        #### Temporal Parameters:
        - **Start Date:** Start of the temporal extent (e.g., `"2020-01-01"`).  
        - **Number of Months:** Duration of the temporal extent in months.

        #### Job Splitting Parameters:
        - **Max Points Per Job:** Maximum number of features per job batch.
        """
        job_df = process_and_create_advanced_patch_jobs(
                gdf, start_date, nb_months, pixel_size, resolution, max_points=max_points
        )
        """
        # Start Job with Standardized UDPs and Feature Collection Filtering

        This function initializes an openEO batch job using standardized **User-Defined Processes (UDPs)** for Sentinel-1 and Sentinel-2 data processing. It employs a spatial filter designed for non-lat/lon feature collections to ensure precise patch sizes in UTM coordinates.

        ### Key Features

        1. **Use of Standardized UDPs**  
        - **S1 Weekly Statistics:** Computes weekly statistics from Sentinel-1 data.  
        - **S2 Weekly Statistics:** Computes weekly statistics from Sentinel-2 data.  
        - UDPs are defined in external JSON files.

        2. **Spatial Filtering with `load_url`**  
        - Accepts feature collections in **UTM coordinates** to guarantee patches with exact dimensions (e.g., 64x64 meters).  
        - Features are uploaded as a GeoParquet file to an creodias S3 bucket, enabling spatial filtering directly on the server.

        3. **Cube Merging**  
        - Merges Sentinel-1 and Sentinel-2 datacubes for combined analysis.

        4. **Job Configuration**  
        - Saves each feature in the collection as a separate file.  
        - Outputs results in **NetCDF** format with filenames derived
        """
        # Authenticate and add the backend
        connection = openeo.connect(url="openeo.dataspace.copernicus.eu").authenticate_oidc()
        # initialize the job manager
        manager = MultiBackendJobManager()
        manager.add_backend("cdse", connection=connection, parallel_jobs=parallel_jobs)
        job_db = CsvJobDatabase(path=job_tracker)
        if not job_db.exists():
            df = manager._normalize_df(job_df)
            job_db.persist(df)
        manager.run_jobs(start_job=start_job, job_db=job_db)