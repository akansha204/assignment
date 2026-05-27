import csv
from io import StringIO


def parse_utility_csv(uploaded_file):
    uploaded_file.seek(0)
    content = uploaded_file.read()

    if isinstance(content, bytes):
        content = content.decode("utf-8-sig", errors="replace")

    reader = csv.DictReader(StringIO(content))
    return list(reader)
