from api.db.migrate import migrate_database


def main() -> None:
    migrate_database()
