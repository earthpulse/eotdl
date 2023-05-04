from pydantic import BaseModel

from ...errors import DatasetDoesNotExistError
from ...models import User 

class LikeDataset():
    def __init__(self, db_repo):
        self.db_repo = db_repo

    class Inputs(BaseModel):
        id: str
        uid: str

    class Outputs(BaseModel):
        message: str

    def __call__(self, inputs: Inputs) -> Outputs:
        # check dataset exists
        if not self.db_repo.exists('datasets', inputs.id):
            raise DatasetDoesNotExistError()
        # toggle like
        data = self.db_repo.retrieve('users', inputs.uid, 'uid')
        user = User(**data)
        print("hola", user)
        if inputs.id in user.liked_datasets:
            print("ei")
            self.db_repo.increase_counter('datasets', '_id', inputs.id, 'likes', -1)
            self.db_repo.remove_from_list('users', 'uid', inputs.uid, 'liked_datasets', inputs.id)
        else:
            print("eo")
            self.db_repo.increase_counter('datasets', '_id', inputs.id, 'likes', 1)
            self.db_repo.append_to_list('users', 'uid', inputs.uid, 'liked_datasets', inputs.id)
        return self.Outputs(message="Dataset liked")