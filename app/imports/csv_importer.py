import csv


def read_titles_csv(path: str):
    with open(path, newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))
