from .auth import Auth0Repo as AuthRepo
from .mongo import MongoRepo as DBRepo
from .mongo import MongoUserRepo as UserDBRepo
from .mongo import MongoTagsRepo as TagsDBRepo
from .mongo import MongoDatasetsRepo as DatasetsDBRepo
from .mongo import MongoModelsRepo as ModelsDBRepo
from .mongo import MongoFilesRepo as FilesDBRepo
from .minio import MinioRepo as OSRepo
from .boto3 import Boto3Repo as S3Repo
from .EOXRepo import EOXRepo
from .geodb import GeoDBRepo
from .mongo import MongoChangesRepo as ChangesDBRepo
from .mongo import MongoNotificationsRepo as NotificationsDBRepo
