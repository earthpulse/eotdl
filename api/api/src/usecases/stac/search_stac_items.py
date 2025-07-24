from typing import Any, Dict, List, Optional
import duckdb
from pydantic import BaseModel

from ..datasets.retrieve_dataset import retrieve_dataset_by_name
from ..models.retrieve_model import retrieve_model_by_name
from ..pipelines.retrieve_pipeline import retrieve_pipeline_by_name
from ...repos import OSRepo
from ...errors import DatasetDoesNotExistError, ModelDoesNotExistError

# TODO: versioning, spatial and temporal queries


class QueryFilter(BaseModel):
    eq: Optional[Any] = None
    gt: Optional[Any] = None
    lt: Optional[Any] = None
    # Extend as needed

class SearchRequest(BaseModel):
    collections: List[str]
    bbox: Optional[List[float]] = None
    datetime: Optional[str] = None
    query: Optional[Dict[str, QueryFilter]] = None
    limit: Optional[int] = 10
    

# TODO: versioning, spatial and temporal queries
def search_stac_items(search_request: SearchRequest, version=1):
    collection_name = search_request.collections[0]  # You can support multi later
    try:
        data = retrieve_dataset_by_name(collection_name)
    except DatasetDoesNotExistError:
        try:
            data = retrieve_model_by_name(collection_name)
        except ModelDoesNotExistError:
            data = retrieve_pipeline_by_name(collection_name)

    os_repo = OSRepo()
    catalog_url = os_repo.get_presigned_url(data.id, f"catalog.v{version}.parquet")

    con = duckdb.connect(database=":memory:")
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute("INSTALL spatial; LOAD spatial;")
    con.execute("SET s3_url_style='path';")

    where_clauses = []

    if search_request.query:
        for field, conditions in search_request.query.items():
            if conditions.eq is not None:
                where_clauses.append(f"{field} = '{conditions.eq}'")
            if conditions.gt is not None:
                where_clauses.append(f"{field} > '{conditions.gt}'")
            if conditions.lt is not None:
                where_clauses.append(f"{field} < '{conditions.lt}'")

    if search_request.datetime:
        start, end = search_request.datetime.split("/")
        where_clauses.append(f"datetime >= '{start}' AND datetime <= '{end}'")

    if search_request.bbox:
        minx, miny, maxx, maxy = search_request.bbox
        where_clauses.append(
            f"ST_Within(geometry, ST_MakeEnvelope({minx}, {miny}, {maxx}, {maxy}))"
        )

    where_clause = " AND ".join(where_clauses) if where_clauses else "TRUE"

    sql = f"""
    SELECT *
    FROM read_parquet('{catalog_url}')
    WHERE {where_clause}
    LIMIT {search_request.limit}
    """

    result = con.execute(sql).fetchdf()
    con.close()

    return {
        "type": "FeatureCollection",
        "features": result.to_dict(orient="records")
    }
