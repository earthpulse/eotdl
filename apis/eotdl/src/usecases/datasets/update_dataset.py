def update_dataset():
    # TODO
    return
    # print("iepa")
    # # retrieve dataset
    # data = self.db_repo.retrieve("datasets", inputs.dataset_id, "id")
    # if data is None:
    #     raise DatasetDoesNotExistError()
    # dataset = Dataset(**data) if data["quality"] == 0 else STACDataset(**data)
    # # check if user owns dataset
    # if dataset.uid != inputs.uid:
    #     raise UserUnauthorizedError()
    # if inputs.name:
    #     # check dataset does not exists already
    #     data2 = self.db_repo.find_one_by_name("datasets", inputs.name)
    #     if data2:
    #         raise DatasetAlreadyExistsError()
    # # validate tags
    # if inputs.tags:
    #     tags_data = self.db_repo.retrieve("tags")
    #     tags = [tag["name"] for tag in tags_data]
    #     for tag in inputs.tags:
    #         if tag not in tags:
    #             raise InvalidTagError()
    # # update dataset

    # print("hola")
    # data.update(
    #     updatedAt=datetime.now(),
    #     description=inputs.description
    #     if inputs.description is not None
    #     else dataset.description,
    #     tags=inputs.tags if inputs.tags is not None else dataset.tags,
    # )
    # if data["quality"] == 0:
    #     data.update(
    #         name=inputs.name if inputs.name is not None else dataset.name,
    #         authors=inputs.authors
    #         if inputs.authors is not None
    #         else dataset.authors,
    #         source=inputs.source if inputs.source is not None else dataset.source,
    #         license=inputs.license
    #         if inputs.license is not None
    #         else dataset.license,
    #     )
    # updated_dataset = (
    #     Dataset(**data) if data["quality"] == 0 else STACDataset(**data)
    # )
    # # update dataset in db
    # self.db_repo.update("datasets", inputs.dataset_id, updated_dataset.dict())
    # return self.Outputs(dataset=updated_dataset)
