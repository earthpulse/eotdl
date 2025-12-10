# MCP

MCP server for the EOTDL. Search for datasets, models, and pipelines in the EOTDL database.

The MCP exposes a tool that performs a RAG search on the EOTDL database based on a query.

The implementation can be found in the `server.py` file.

## Vector Database

The following commands can be used to populate/clear the vector database:

```bash
uv run clear_vector_db.py
uv run populate_vector_db.py
```
