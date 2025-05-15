from datetime import datetime


def parse_date(field_name: str, values):
    date_value = values.get(field_name)
    if not date_value:
        values[field_name] = None
        return values
    if isinstance(date_value, dict) and "$date" in date_value:
        date_value = date_value["$date"]
    if isinstance(date_value, str):
        values["field_name"] = datetime.fromisoformat(date_value.replace("Z", "+00:00"))
    return values