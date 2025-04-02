import duckdb

from ..datasets import retrieve_dataset_by_name
from ...repos import OSRepo

# TODO: versioning, spatial and temporal queries

def search_stac_items(collection_id, query):
    dataset = retrieve_dataset_by_name(collection_id)
    os_repo = OSRepo()
    catalog_presigned_url = os_repo.get_presigned_url(dataset.id, "catalog.v1.parquet")
    
    # Create a DuckDB connection and load required extensions
    con = duckdb.connect(database=':memory:')
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute("INSTALL spatial; LOAD spatial;")
    
    # Set request parameters for S3 presigned URL
    con.execute("SET s3_url_style='path';")
    
    # Read parquet file directly with DuckDB and execute query
    sql = f"""
    SELECT *
    FROM read_parquet('{catalog_presigned_url}')
    WHERE {query}
    """

    # Execute query and fetch results
    result = con.execute(sql).fetchdf()
    
    # Close the connection
    con.close()
    
    # Convert results to JSON
    items = result.to_json(orient='records')
    return items


def search_stac_columns(collection_id):
    dataset = retrieve_dataset_by_name(collection_id)
    os_repo = OSRepo()
    catalog_presigned_url = os_repo.get_presigned_url(dataset.id, "catalog.v1.parquet")
    con = duckdb.connect(database=':memory:')
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute("SET s3_url_style='path';")
    # Get schema information from parquet file
    result = con.execute(f"SELECT * FROM parquet_schema('{catalog_presigned_url}')").fetchdf()
    # Create dict with column name as key and type as value
    columns = {name: type_ for name, type_ in zip(result['name'], result['type'])}
    con.close()
    return columns
