
class UserContext:
    def __init__(self):
        self.context_data = {}

    def set(self, user_id, key, data):
        """Set data for a specific user under a specific key."""
        if user_id not in self.context_data:
            self.context_data[user_id] = {}
        self.context_data[user_id][key] = data

    def get(self, user_id, key):
        """Retrieve data for a specific user under a specific key."""
        return self.context_data.get(user_id, {}).get(key)

    def get_all(self, user_id):
        """Retrieve all data for a specific user."""
        return self.context_data.get(user_id, {})
    
    def get_context_data(self):
        """Retrieve whole context data"""
        return self.context_data

    def clear(self, user_id, key):
        """Clears sepcific data for a specific user."""
        if user_id in self.context_data:
            del self.context_data[user_id][key]

    def clear_user(self, user_id):
        """Clears all data for a specific user."""
        if user_id in self.context_data:
            del self.context_data[user_id]

    def clear_all(self):
        """Clears all data for all users."""
        self.context_data.clear()

