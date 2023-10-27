from ...repos import UserDBRepo
from ...models import Limits
from ...errors import TierLimitError

from .retrieve_user import retrieve_user


def check_user_can_download_dataset(user):
    repo = UserDBRepo()
    user = retrieve_user(user.uid)
    data = repo.retrieve_tier(user.tier)
    limits = Limits(**data["limits"])
    usage = repo.retrieve_dataset_download_usage(user.uid)
    if len(usage) + 1 >= limits.datasets.download:
        raise TierLimitError(
            "You cannot download more than {} files per day".format(
                limits.datasets.download
            )
        )
    return True
