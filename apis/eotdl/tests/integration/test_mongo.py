import pytest
from bson.objectid import ObjectId

from ...src.repos.mongo.client import get_db
from ...src.repos.mongo import MongoRepo


@pytest.fixture
def db():
    db = get_db()
    ids = [ObjectId(), ObjectId()]
    data = [{"_id": ids[0], "name": "1"}, {"_id": ids[1], "name": "2"}]
    db["col"].insert_many(data)
    yield db, ids, data
    db.drop_collection("col")


def test_exists(db):
    db, ids, _ = db
    repo = MongoRepo()
    assert repo.exists("col", ids[0]) == True
    assert repo.exists("col", ids[1]) == True
    assert repo.exists("col", ObjectId()) == False


def test_persist(db):
    db, _, _ = db
    repo = MongoRepo()
    id = ObjectId()
    assert repo.persist("col", {"name": "3"}, id).inserted_id == id
    assert db["col"].find_one({"_id": id}) == {"_id": id, "name": "3"}
    new_id = repo.persist("col", {"name": "4"})
    assert db["col"].find_one({"_id": new_id}) == {"_id": new_id, "name": "4"}


def test_retrieve(db):
    db, ids, data = db
    repo = MongoRepo()
    _data = repo.retrieve("col")
    assert len(_data) == 2
    assert _data == data
    _data = repo.retrieve("col", sort="name", order=-1)
    assert _data == data[::-1]
    _data = repo.retrieve("col", sort="name", order=-1, limit=1)
    assert _data == data[-1:]
    _data = repo.retrieve("col", ids[0], "_id")
    assert _data == data[0]
    _data = repo.retrieve("col", ids[1], "_id")
    assert _data == data[1]
    _data = repo.retrieve("col", data[0]["name"], "name")
    assert _data == data[0]
