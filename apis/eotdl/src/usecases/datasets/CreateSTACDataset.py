from pydantic import BaseModel

from ...models import STACDataset, User
# from .CreateDataset import CreateDataset


# class CreateSTACDataset(CreateDataset):
#     def __init__(self, db_repo, geodb_repo, retrieve_user_credentials):
#         super().__init__(db_repo)
#         self.retrieve_user_credentials = retrieve_user_credentials
#         self.geodb_repo = geodb_repo

#     class Inputs(BaseModel):
#         name: str
#         uid: str
#         user: User

#     def create_dataset(self, id, inputs):
#         return STACDataset(
#             uid=inputs.uid,
#             id=id,
#             name=inputs.name,
#         )

#     def __call__(self, inputs: Inputs):
#         # retrieve user geodb creds
#         credentials = self.retrieve_user_credentials(inputs.user)
#         self.geodb_repo(credentials)  # validate credentials
#         return super().__call__(inputs)
