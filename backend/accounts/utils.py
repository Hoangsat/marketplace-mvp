def normalize_email_address(value):
    if value is None:
        return ""
    return str(value).strip().lower()
