from pydantic import BaseModel
import typing
from typing import List

class RetrieveDatasetsLeaderboard():
    def __init__(self, db_repo):
        self.db_repo = db_repo

    class Inputs(BaseModel):
        pass

    class Outputs(BaseModel):
        leaderboard: List[dict]

    def __call__(self, inputs: Inputs) -> Outputs:
        # retrieve top 5 user with more datasets
        users = self.db_repo.find_top('users', 'dataset_count', 5)
        leaderboard = [{
            'name': user['name'],
            'datasets': user['dataset_count']
        } for user in users]
        return self.Outputs(leaderboard=leaderboard)