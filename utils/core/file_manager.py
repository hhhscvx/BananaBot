import json


def get_all_lines(filepath: str) -> list:
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    return [line.strip() for line in lines] if lines else []


def load_from_json(path: str) -> list | dict:
    with open(path, 'r', encoding='utf-8') as json_file:
        return json.load(json_file)


def save_to_json(path: str, new_data: dict) -> None:
    with open(path, 'r', encoding='utf-8') as json_file:
        data: list = json.load(json_file)

    data.append(new_data)
    with open(path, 'w') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)


def save_accounts_to_file(path: str, accounts: list) -> None:
    with open(path, 'w', encoding='utf-8') as file:
        for item in accounts:
            file.write(f"{item['session_name']}.session\n")
