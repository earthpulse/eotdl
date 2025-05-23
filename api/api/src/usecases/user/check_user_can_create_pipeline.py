from ...repos import UserDBRepo
from ...models import Limits
from ...errors import TierLimitError

from .retrieve_user import retrieve_user


def check_user_can_create_pipeline(user):
    repo = UserDBRepo()
    user = retrieve_user(user.uid)
    data = repo.retrieve_tier(user.tier)
    limits = Limits(**data["limits"])
    usage = repo.retrieve_pipeline_ingestion_usage(user.uid)
    if len(usage) + 1 >= limits.pipelines.upload:
        raise TierLimitError(
            "You cannot create more than {} pipelines per day".format(limits.pipelines.upload)
        )
    if user.dataset_count + 1 > limits.pipelines.count:
        raise TierLimitError(
            "You cannot have more than {} pipelines".format(limits.pipelines.count)
        )
    return True
