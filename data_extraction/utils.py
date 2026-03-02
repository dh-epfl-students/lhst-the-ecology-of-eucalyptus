# Source - https://stackoverflow.com/a/6330109
# Posted by Artsiom Rudzenka, modified by community. See post 'Timeline' for change history
# Retrieved 2026-02-18, License - CC BY-SA 3.0

def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default

