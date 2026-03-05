from api.db.migrate import migrate_database
from api.messagebus.migrate import migrate_kafka


def main() -> None:
    migrate_database()
    migrate_kafka()
