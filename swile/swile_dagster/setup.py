from setuptools import find_packages, setup

setup(
    name="swile_dagster",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "dagster",
        "dagster-cloud",
        "dagster-dbt",
        "dbt-core>=1.4.0",
        "dbt-postgres",
        "sqlalchemy",
        "requests",
        "minio",
    ],
    extras_require={
        "dev": [
            "dagster-webserver",
        ]
    },
)
