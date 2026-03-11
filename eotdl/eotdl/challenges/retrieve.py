from ..repos import ChallengesAPIRepo


def retrieve_challenges():
    repo = ChallengesAPIRepo()
    data, error = repo.list_challenges()
    if error:
        raise Exception(error)
    return data
