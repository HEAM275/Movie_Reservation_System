def get_user_fullname(user):
    if not user or not user.is_authenticated:
        return None
    full_name = f"{user.first_name} {user.last_name}".strip()
    return full_name or user.username
