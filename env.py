import os
import sys
from logging.config import fileConfig
from alembic import context
from tortoise.contrib import generate_schema_for_client
from tortoise.backends.asyncpg import AsyncpgDBClient
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models import Business, Product, ScrapedProduct
from business.schemas import UserBusiness, UserProduct
from retail.schemas import RetailBusiness, RetailProduct, RetailScrapedProduct
from wholesale.schemas import WholesaleBusiness, WholesaleProduct, WholesaleScrapedProduct


config = context.config
fileConfig(config.config_file_name)
target_metadata = generate_schema_for_client(AsyncpgDBClient(), [
    Business, UserBusiness, WholesaleBusiness, RetailBusiness,
    Product, UserProduct, RetailProduct, WholesaleProduct,
    ScrapedProduct, RetailScrapedProduct, WholesaleScrapedProduct
])


def run_migrations_offline():
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = AsyncpgDBClient().get_connection(
        url=config.get_main_option("sqlalchemy.url")
    )

    with connectable.cursor() as cursor:
        cursor.execute("SELECT 1")

    with connectable:
        with context.begin_transaction(connectable=connectable):
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
