from flask import Flask
import os

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


app = Flask(__name__)


# Read database configuration from environment variables
DB_HOST = os.getenv("DB_HOST", "cloud-postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "cloudops")
DB_USER = os.getenv("DB_USER", "clouduser")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# Build PostgreSQL connection URL
DATABASE_URL = (
    f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


# Create SQLAlchemy database engine
engine = create_engine(DATABASE_URL)


@app.route("/")
def home():
    return """
    <html>
        <head>
            <title>AWS Cloud Operations Dashboard</title>
        </head>
        <body>
            <h1>AWS Cloud Operations Dashboard</h1>

            <h2>Application Status: HEALTHY</h2>

            <p><strong>Environment:</strong> Development</p>
            <p><strong>Container:</strong> Docker</p>
            <p><strong>Cloud Platform:</strong> AWS</p>

            <h3>AWS Components</h3>

            <ul>
                <li>VPC - Planned</li>
                <li>ECS Fargate - Planned</li>
                <li>Application Load Balancer - Planned</li>
                <li>RDS - Planned</li>
                <li>CloudWatch - Planned</li>
                <li>Secrets Manager - Planned</li>
            </ul>
        </body>
    </html>
    """


@app.route("/health")
def health():
    return {
        "status": "healthy"
    }


@app.route("/deployments")
def deployments():
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text(
                    """
                    SELECT id, application, environment, status
                    FROM deployments
                    ORDER BY id
                    """
                )
            )

            deployments_data = [
                {
                    "id": row.id,
                    "application": row.application,
                    "environment": row.environment,
                    "status": row.status
                }
                for row in result
            ]

        return deployments_data

    except SQLAlchemyError as error:
        return {
            "status": "error",
            "message": "Database connection failed"
        }, 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)