from ...repos import UserDBRepo
from ...models import Limits
from ...errors import TierLimitError

from .retrieve_user import retrieve_user


def check_user_can_create_dataset(user):
    repo = UserDBRepo()
    user = retrieve_user(user.uid)
    data = repo.retrieve_tier(user.tier)
    if not data:
        raise TierLimitError(f"User tier: {user.tier} not found")
    limits = Limits(**data["limits"])
    usage = repo.retrieve_dataset_ingestion_usage(user.uid)
    if len(usage) + 1 >= limits.datasets.upload:
        raise TierLimitError(
            "You cannot create more than {} datasets per day".format(
                limits.datasets.upload
            )
        )
    if user.dataset_count + 1 > limits.datasets.count:
        raise TierLimitError(
            "You cannot have more than {} datasets".format(limits.datasets.count)
        )
    return True
