class States:
    # State management for conversations
    user_states = {}

    @classmethod
    def set_state(cls, user_id, state, data=None):
        cls.user_states[user_id] = {"state": state, "data": data or {}}

    @classmethod
    def get_state(cls, user_id):
        return cls.user_states.get(user_id, {"state": None, "data": {}})

    @classmethod
    def clear_state(cls, user_id):
        cls.user_states.pop(user_id, None)

    @classmethod
    def update_data(cls, user_id, **kwargs):
        if user_id in cls.user_states:
            cls.user_states[user_id]["data"].update(kwargs)
