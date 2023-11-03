from ...repos import UserDBRepo
from ...models import Limits
from ...errors import TierLimitError

from .retrieve_user import retrieve_user


def check_user_can_create_model(user):
    repo = UserDBRepo()
    user = retrieve_user(user.uid)
    data = repo.retrieve_tier(user.tier)
    limits = Limits(**data["limits"])
    usage = repo.retrieve_model_ingestion_usage(user.uid)
    if len(usage) + 1 >= limits.models.upload:
        raise TierLimitError(
            "You cannot create more than {} models per day".format(limits.models.upload)
        )
    if user.dataset_count + 1 > limits.models.count:
        raise TierLimitError(
            "You cannot have more than {} models".format(limits.models.count)
        )
    return True
