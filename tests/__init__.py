import os

if "rye" not in os.environ["PATH"]:
    os.environ["PATH"] += f":{os.path.expanduser('~')}/.rye/shims"
