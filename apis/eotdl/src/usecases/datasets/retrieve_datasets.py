def retrieve_datasets():
    # TODO
    return
    # data = self.db_repo.retrieve(
    #     "datasets", limit=inputs.limit, sort="createdAt", order=-1
    # )
    # datasets = []
    # for d in data:
    #     if d["quality"] == 0:
    #         datasets.append(Dataset(**d))
    #     else:
    #         datasets.append(STACDataset(**d))
    # return self.Outputs(datasets=datasets)


def retrieve_liked_datasets():
    # TODO
    return
    # data = self.db_repo.retrieve("users", inputs.uid, "uid")
    # if data is None:
    #     raise UserDoesNotExistError()
    # user = User(**data)
    # data = self.db_repo.retrieve_many("datasets", user.liked_datasets)
    # datasets = []
    # for d in data:
    #     if d["quality"] == 0:
    #         datasets.append(Dataset(**d))
    #     else:
    #         datasets.append(STACDataset(**d))
    # return self.Outputs(datasets=datasets)


def retrieve_popular_datasets():
    # TODO
    return
    # data = self.db_repo.find_top("datasets", "likes", inputs.limit)
    # datasets = []
    # for d in data:
    #     if d["quality"] == 0:
    #         datasets.append(Dataset(**d))
    #     else:
    #         datasets.append(STACDataset(**d))
    # return self.Outputs(datasets=datasets)


def retrieve_datasets_leaderboard():
    # TODO
    return
    # users = self.db_repo.find_top("users", "dataset_count", 5)
    # leaderboard = [
    #     {"name": user["name"], "datasets": user["dataset_count"]} for user in users
    # ]
    # return self.Outputs(leaderboard=leaderboard)
