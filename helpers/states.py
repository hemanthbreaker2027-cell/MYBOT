from database.mongo import db

states_coll = db["states"] if db is not None else None

class States:
    # State management for conversations with MongoDB persistence
    @classmethod
    async def set_state(cls, user_id, state, data=None):
        if states_coll is not None:
            await states_coll.update_one(
                {"user_id": user_id},
                {"$set": {"state": state, "data": data or {}}},
                upsert=True
            )

    @classmethod
    async def get_state(cls, user_id):
        if states_coll is not None:
            doc = await states_coll.find_one({"user_id": user_id})
            if doc:
                return {"state": doc["state"], "data": doc["data"]}
        return {"state": None, "data": {}}

    @classmethod
    async def clear_state(cls, user_id):
        if states_coll is not None:
            await states_coll.delete_one({"user_id": user_id})

    @classmethod
    async def update_data(cls, user_id, **kwargs):
        if states_coll is not None:
            await states_coll.update_one(
                {"user_id": user_id},
                {"$set": {f"data.{k}": v for k, v in kwargs.items()}}
            )
