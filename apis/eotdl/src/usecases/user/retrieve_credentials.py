from ...repos import EOXRepo
from .check_user_exists import check_user_exists

def retrieve_user_credentials(user):
    eox_repo = EOXRepo()
    check_user_exists(user.uid)
    data, error = eox_repo.retrieve_credentials(user.email)
    if error:
        raise Exception(error)
    return data