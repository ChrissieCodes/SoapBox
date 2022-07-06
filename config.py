import os

basedir = os.path.abspath(os.path.dirname(__file__))

def get_sqlite_memory_uri():
    return f"sqlite:///:memory:"


def get_sqlite_file_url():
    """
    gets the fully-qualified path to the recommendations.db file
    """
    return f"sqlite:///{os.path.join(basedir, 'recommendations.db')}"


def get_api_url():
    host = os.environ.get("API_HOST", "localhost")
    port = 5000 if host == "localhost" else 80
    return f"http://{host}:{port}"


def get_redis_host_and_port():
    host = os.environ.get("REDIS_HOST", "localhost")
    port = 63791 if host == "localhost" else 6379
    return dict(host=host, port=port)


def get_email_host_and_port():
    host = os.environ.get("EMAIL_HOST", "localhost")
    port = 11025 if host == "localhost" else 1025
    http_port = 18025 if host == "localhost" else 8025
    return dict(host=host, port=port, http_port=http_port)