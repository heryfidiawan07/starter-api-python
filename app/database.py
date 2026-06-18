from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings


def get_database_url() -> str:
    d = settings.db_driver
    h, p, n = settings.db_host, settings.db_port, settings.db_name
    u, pw = settings.db_user, settings.db_pass
    match d:
        case "postgres":
            return f"postgresql+psycopg2://{u}:{pw}@{h}:{p}/{n}"
        case "sqlserver":
            return (
                f"mssql+pyodbc://{u}:{pw}@{h}:{p}/{n}"
                "?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"
            )
        case "sqlite":
            return f"sqlite:///{n}.db"
        case _:
            return f"mysql+pymysql://{u}:{pw}@{h}:{p}/{n}?charset=utf8mb4"


engine = create_engine(get_database_url(), echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
