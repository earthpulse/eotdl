from ...repos import DatasetsDBRepo


def deactivate_dataset(dataset_name: str):
    repo = DatasetsDBRepo()
    dataset = repo.find_one_by_name(dataset_name)
    if dataset.get("active") is False:
        raise Exception(f"Dataset {dataset_name} is already deactivated.")
    repo.deactivate_dataset(dataset_name)
    return f"Dataset {dataset_name} has been deactivated."