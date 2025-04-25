from ...models.user import User
from .retrieve_dataset import retrieve_owned_dataset
from ...repos import DatasetsDBRepo


def make_dataset_private(dataset_id: str, user: User):
    """
    Make a dataset private.
    """
    dataset = retrieve_owned_dataset(dataset_id, user.uid)
    repo = DatasetsDBRepo()
    if user.uid in dataset.allowedUsers:
        raise Exception("This dataset is already private")
    repo.allow_user_to_dataset(dataset_id, user.uid)
    return f"Dataset {dataset.name} has been made private."


def allow_user_to_private_dataset(
    dataset_id: str,
    user: User,
    user_id: str,
):
    """
    Allow a user to access a private dataset.
    """
    dataset = retrieve_owned_dataset(dataset_id, user.uid)
    repo = DatasetsDBRepo()
    if not user.uid in dataset.allowedUsers:
        raise Exception("This is not a private dataset")
    repo.allow_user_to_dataset(dataset_id, user_id)
    return f"User {user_id} has been allowed to access the private dataset {dataset.name}."
