from ...models.user import User
from .retrieve_dataset import retrieve_owned_dataset
from ...repos import DatasetsDBRepo, UserDBRepo


def make_dataset_private(dataset_id: str, user: User):
    """
    Make a dataset private.
    """
    dataset = retrieve_owned_dataset(dataset_id, user)
    repo = DatasetsDBRepo()
    if user.uid in dataset.allowed_users:
        raise Exception("This dataset is already private")
    repo.allow_user_to_dataset(dataset_id, user.uid)
    return f"Dataset {dataset.name} has been made private."


def allow_user_to_private_dataset(
    dataset_id: str,
    user: User,
    email: str = None,
    user_id: str = None,
):
    """
    Allow a user to access a private dataset.
    """
    dataset = retrieve_owned_dataset(dataset_id, user)
    if not dataset.visibility == "private":
        raise Exception("This is not a private dataset")
    if not email and not user_id:
        raise Exception("Either email or user_id must be provided")
    if email and not user_id:
        repo = UserDBRepo()
        _user = repo.find_one_user_by_email(email)
        if not _user:
            raise Exception("User not found")
        _user = User(**_user)
    if _user.id in dataset.allowed_users:
        raise Exception("This user is already allowed to access the dataset")
    repo = DatasetsDBRepo()
    repo.allow_user_to_dataset(dataset_id, _user.id)
    return f"User {_user.email} has been allowed to access the private dataset {dataset.name}."

def remove_user_from_private_dataset(
    dataset_id: str,
    user: User,
    email: str = None,
    user_id: str = None,
):
    """
    Remove a user from a private dataset.
    """
    dataset = retrieve_owned_dataset(dataset_id, user)
    if not dataset.visibility == "private":
        raise Exception("This is not a private dataset")
    if not email and not user_id:
        raise Exception("Either email or user_id must be provided")
    if email and not user_id:
        repo = UserDBRepo()
        _user = repo.find_one_user_by_email(email)
        if not _user:
            raise Exception("User not found")
        _user = User(**_user)
    if _user.id not in dataset.allowed_users:
        raise Exception("This user is not allowed to access the dataset")
    if _user.id == user.id:
        raise Exception("You cannot remove yourself from the dataset")
    repo = DatasetsDBRepo()
    repo.remove_user_from_dataset(dataset_id, _user.id)
    return f"User {_user.email} has been removed from the private dataset {dataset.name}."