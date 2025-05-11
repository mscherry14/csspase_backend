from pydantic_mongo import AsyncAbstractRepository
from ..models.user import UserDB

class UsersRepository(AsyncAbstractRepository[UserDB]):
    class Meta:
        collection_name = "users"

"""
AsyncAbstractRepository[T]
async delete
async delete_by_id
async find_by
async find_by_with_output_type
async find_one_by
async find_one_by_id
get_collection()
async paginate
async paginate_with_output_type
async save
async save_many

see docs in https://pydantic-mongo.readthedocs.io/en/latest/api/async_abstract_repository.html
"""