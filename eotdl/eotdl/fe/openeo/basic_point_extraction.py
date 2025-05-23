from .dataframe_utils import *
import openeo
from openeo.extra.job_management import MultiBackendJobManager, CsvJobDatabase

def start_job(row: pd.Series, connection: openeo.Connection, s1_weekly_statistics_url: str, s2_weekly_statistics_url: str, **kwargs) -> openeo.BatchJob:
        temporal_extent = row["temporal_extent"]
        # set up load url in order to allow non-latlon feature collections for spatial filtering
        geometry = row["geometry"]
        #run the s1 and s2 udp
        s1 = connection.datacube_from_process(
                "s1_weekly_statistics",
                namespace=s1_weekly_statistics_url,
                temporal_extent=temporal_extent,
        )
        s2 = connection.datacube_from_process(
                "s2_weekly_statistics",
                namespace=s2_weekly_statistics_url,
                temporal_extent=temporal_extent,
        )
        #merge both cubes and filter across the feature collection
        merged = s2.merge_cubes(s1)
        result = merged.aggregate_spatial(geometries = geometry, reducer = "mean")
        #dedicated job settings to save the individual features within a collection seperately
        job = result.create_job(
                out_format="parquet",
        )
        return job

def point_extraction(
        gdf,
        s1_weekly_statistics_url,
        s2_weekly_statistics_url,
        start_date,
        nb_months,
        extra_cols=[],
        job_tracker = 'jobs.csv',
        parallel_jobs=2,
):
        """
        # Transform GeoDataFrame for MultiBackendJobManager

        This function processes an input GeoDataFrame and prepares it for use with openEO's **MultiBackendJobManager**. The job manager enables launching and tracking multiple openEO jobs simultaneously, which is essential for large-scale data extractions. 

        ### Note

        It is important to note, that for this simple example we have opted to not group the various geometries into feature collections. This utility is only illustrated in the more advanced example. The impact for this choice is that for each polygon, a singly openEO job will need to be launched, leading to a more time and cost extensive extraction workflow.


        ### Parameters

        #### Temporal Parameters:
        - **Start Date:** Start of the temporal extent (e.g., `"2020-01-01"`).  
        - **Number of Months:** Duration of the temporal extent in months.
        """
        job_df = process_geodataframe(gdf, start_date, nb_months, extra_cols)
        """
        # Start Job with Standardized UDPs and Feature Collection Filtering

        This function initializes an openEO batch job using standardized **User-Defined Processes (UDPs)** for Sentinel-1 and Sentinel-2 data processing. It employs a spatial aggregation in order to get a time series per polygon.

        ### Key Features

        1. **Use of Standardized UDPs**  
        - **S1 Weekly Statistics:** Computes weekly statistics from Sentinel-1 data.  
        - **S2 Weekly Statistics:** Computes weekly statistics from Sentinel-2 data.  
        - UDPs are defined in external JSON files.

        2. **Spatial aggregation across polygons**  
        - an average is calculated for each individual polygon

        3. **Cube Merging**  
        - Merges Sentinel-1 and Sentinel-2 datacubes for combined analysis.

        4. **Job Configuration**  
        - Outputs results in **parquet** format with filenames derived
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
        manager.run_jobs(start_job=start_job, job_db=job_db, s1_weekly_statistics_url=s1_weekly_statistics_url, s2_weekly_statistics_url=s2_weekly_statistics_url)