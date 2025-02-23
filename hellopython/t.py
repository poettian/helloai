from datetime import datetime, timezone

print(datetime.now(tz=timezone.utc).isoformat())