from bson import ObjectId
from models.user import User
from models.inventory import InventoryItem
from pymongo import IndexModel
import re


class BaseRepository:
    def __init__(self, collection, model_translator, default_scope, indicies):
        self.collection = collection
        self.model_translator = model_translator
        self.default_scope = default_scope
        self.__configure_indicies(indicies)

    def create(self, model):
        document = self.model_translator.to_document(model)
        document.pop("_id")
        return self.collection.insert_one(document).inserted_id

    def update(self, model):
        document = self.model_translator.to_document(model)
        self.collection.update_one({"_id": ObjectId(model.id)}, {"$set": document})

    def delete(self, model):
        self.collection.delete_one({"_id": ObjectId(model.id)})

    def delete_all(self):
        self.collection.delete_many({})

    def find_by_id(self, model_id):
        object_id = self._parse_object_id(model_id)
        pipeline = [{"$match": {"_id": object_id}}]
        return self._find_one_by_aggregation(pipeline + self.default_scope)

    def find_by_ids_list(self, ids_list) -> list:
        ids = [self._parse_object_id(arg_id) for arg_id in ids_list]
        pipeline = [{"$match": {"_id": {"$in": ids}}}]
        return self._find_by_aggregation(pipeline + self.default_scope)

    def get_page(self, skip, limit) -> list:
        return self._find_by_aggregation(
            self.default_scope + [{"$skip": skip}, {"$limit": limit}]
        )

    def get_list(self):
        pipeline = [{"$match": {}}]
        return self._find_by_aggregation(pipeline + self.default_scope)

    def _find_by_aggregation(self, pipeline) -> list:
        cursor = self.collection.aggregate(pipeline)
        result = [self.model_translator.from_document(d) for d in cursor]
        return result

    def _find_one_by_aggregation(self, pipeline):
        result = self._find_by_aggregation(pipeline)
        if not result:
            return None
        return result[0]

    def _count_by_aggregation(self, pipeline) -> int:
        group_step = {"$group": {"_id": None, "count": {"$sum": 1}}}
        project_step = {"$project": {"_id": 0}}

        cursor = self.collection.aggregate(pipeline + [group_step, project_step])
        result = [item.get("count") for item in cursor]
        if not result:
            return 0
        return result[0]

    def _parse_object_id(self, model_id) -> ObjectId or None:
        if isinstance(model_id, ObjectId):
            return model_id
        if ObjectId.is_valid(model_id):
            return ObjectId(model_id)
        return None

    def __configure_indicies(self, index_columns) -> None:
        indicies = [
            IndexModel(
                [(column.name, column.sorting_order)], background=True, name=column.name
            )
            for column in index_columns
        ]
        existing_indicies = self.collection.index_information()
        new_indicies = [
            index for index in indicies if index not in existing_indicies.keys()
        ]
        if new_indicies:
            self.collection.create_indexes(new_indicies)


class MongoColumnFactory:
    def ascending(self, column_name):
        return MongoColumn(column_name, 1)

    def descending(self, column_name):
        return MongoColumn(column_name, -1)


class MongoColumn:
    def __init__(self, name, sorting_order):
        self.name = name
        self.sorting_order = sorting_order


class UsersRepository(BaseRepository):
    def __init__(self, collection, user_translator, indicies) -> None:
        super().__init__(collection, user_translator, [], indicies)

    def get_page(self, skip, limit, role):
        sort = {"$sort": {"_id": -1}}
        match_step = {"$match": {}}
        skip_step = {"$skip": skip}
        limit_step = {"$limit": limit}
        if role:
            match_step["$match"] = {"role": role}

        pipeline = [sort, match_step, skip_step, limit_step]
        return self._find_by_aggregation(self.default_scope + pipeline)

    def count(self, role):
        find_filter = {}
        if role:
            find_filter["role"] = role
        pipeline = [{"$match": find_filter}]
        return self._count_by_aggregation(self.default_scope + pipeline)

    def find_by_email(self, email: str) -> list or None:
        escaped_email = re.escape(email)
        find_attrs = {"email": {"$regex": f"^{escaped_email}$", "$options": "i"}}
        pipeline = [{"$match": find_attrs}]
        return self._find_one_by_aggregation(self.default_scope + pipeline)

    def find_password_reset(self, code) -> User or None:
        find_attrs = {"password_reset_requests": {"$elemMatch": {"code": code}}}
        pipeline = [{"$match": find_attrs}]
        return self._find_one_by_aggregation(self.default_scope + pipeline)

    def delete_all(self):
        super().delete_all()


class TokensRepository(BaseRepository):
    def __init__(self, collection, token_pair_translator, indicies):
        super().__init__(collection, token_pair_translator, [], indicies)

    def find_access(self, access_token):
        pipeline = [{"$match": {"access_token": access_token}}]
        return self._find_one_by_aggregation(self.default_scope + pipeline)

    def find_refresh(self, refresh_token):
        pipeline = [{"$match": {"refresh_token": refresh_token}}]
        return self._find_one_by_aggregation(self.default_scope + pipeline)


class InventoryRepository(BaseRepository):
    def __init__(self, collection, model_translator, indicies):
        super().__init__(collection, model_translator, [], indicies)

    def get_alert_violations(self):
        pipeline = [
            {
                "$match": {
                    "alert": {"$ne": None},
                    "$expr": {
                        "$lt": ["$quantity", "$alert.quantity"]
                    }
                }
            }
        ]
        return self._find_by_aggregation(self.default_scope + pipeline)