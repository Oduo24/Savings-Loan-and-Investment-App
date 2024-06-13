def format_numbers_in_json(data):
    if isinstance(data, dict):
        return {k: format_numbers_in_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [format_numbers_in_json(item) for item in data]
    elif isinstance(data, (int, float)):
        return '{:,}'.format(data)
    else:
        return data