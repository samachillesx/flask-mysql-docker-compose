import os

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "database": os.getenv("MYSQL_DATABASE", "taskdb"),
    "user": os.getenv("MYSQL_USER", "taskuser"),
    "password": os.getenv("MYSQL_PASSWORD", "taskpassword"),
}
