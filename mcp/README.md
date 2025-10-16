# Vector Database Population

I tried to update existing items in the vector database, but it didn't work. So better to clear the database and repopulate it every time.

```bash
uv run clear_vector_db.py
uv run populate_vector_db.py
```