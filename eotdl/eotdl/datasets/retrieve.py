from ..repos import DatasetsAPIRepo


def retrieve_datasets(name=None, limit=None):
    api_repo = DatasetsAPIRepo()
    data, error = api_repo.retrieve_datasets(name, limit)
    if data and not error:
        datasets = [d["name"] for d in data] if data else []
        return datasets
    return []


# def list_datasets(pattern=None):
#     datasets = retrieve_datasets()
#     if pattern:
#         regex = re.compile(rf".*{re.escape(pattern)}.*", re.IGNORECASE)
#         names = list(datasets.keys())
#         valid = [name for name in names if regex.search(name)]
#         return {name: datasets[name] for name in valid}
#     return datasets

# def retrieve_dataset(name):
#     api_repo = APIRepo()
#     retrieve = RetrieveDataset(api_repo)
#     inputs = retrieve.Inputs(name=name)
#     outputs = retrieve(inputs)
#     return outputs.dataset
