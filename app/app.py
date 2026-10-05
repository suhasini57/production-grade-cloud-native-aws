from flask import Flask

app = Flask(__name__)


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)