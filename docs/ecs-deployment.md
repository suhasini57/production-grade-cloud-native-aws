# ECS and Fargate Deployment Documentation

## 1. Project Overview

This document explains how the AWS Cloud Dashboard Flask application was deployed on Amazon Elastic Container Service (ECS) using AWS Fargate.

The deployment uses:

- **GitHub Actions** for Continuous Integration and Continuous Deployment (CI/CD).
- **Amazon ECR** for Docker image storage.
- **Amazon ECS** for container orchestration.
- **AWS Fargate** for serverless container execution.
- **Amazon CloudWatch** for application logging.

The objective is to automate application deployment and verify that the container runs successfully in AWS.

## 2. Deployment Architecture

The deployment follows this workflow:

```text
Developer
    |
    v
GitHub Repository
    |
    v
GitHub Actions
    |
    +--> Run Automated Tests
    |
    +--> Build Docker Image
    |
    v
Configure AWS Credentials using OIDC
    |
    v
Amazon ECR
    |
    v
Push Docker Image
    |
    v
ECS Task Definition
    |
    v
ECS Service
    |
    v
AWS Fargate
    |
    v
Flask Application
    |
    +--> /health
    |
    +--> /
    |
    v
Amazon CloudWatch
```

The workflow automates testing, Docker image publishing, ECS deployment, and application logging.

## 3. AWS Configuration

The following configuration was used during deployment:

| Component | Configuration |
|---|---|
| AWS Region | `ap-south-2` |
| ECS Cluster | `aws-cloud-dashboard-cluster` |
| ECS Service | `aws-cloud-dashboard-service` |
| Task Definition Family | `aws-cloud-dashboard-task` |
| Verified Task Definition Revision | `2` |
| Launch Type | Fargate |
| Operating System | Linux |
| CPU Architecture | X86_64 |
| CPU | 256 (0.25 vCPU) |
| Memory | 512 MB |
| Network Mode | `awsvpc` |
| Container Name | `aws-cloud-dashboard` |
| Container Port | `5000` |
| ECR Repository | `aws-cloud-dashboard` |

## 4. Docker Image and Amazon ECR

The Flask application was packaged as a Docker image and stored in Amazon Elastic Container Registry (ECR).

**ECR Repository URI:**

```text
989445685277.dkr.ecr.ap-south-2.amazonaws.com/aws-cloud-dashboard
```

The GitHub Actions workflow publishes two image tags:

- **Git commit SHA:** Uniquely identifies the application version.
- **latest:** Identifies the most recently published image.

The verified deployment image used the following commit:

```text
319d4e32cc7408b56edf9618468211472a1c000f
```

Using a commit SHA as an image tag makes it possible to identify the exact application version deployed.

## 5. GitHub Actions and Automated ECS Deployment

The CI/CD workflow automates the following activities:

1. Checks out the GitHub repository.
2. Installs Python dependencies.
3. Executes Flask application tests.
4. Builds the Docker image.
5. Authenticates to AWS using GitHub OpenID Connect (OIDC).
6. Authenticates with Amazon ECR.
7. Publishes the Docker image to ECR.
8. Renders the ECS task definition with the new image.
9. Registers a new ECS task definition revision.
10. Updates the ECS service to use the new task definition.

The workflow uses IAM permissions scoped to the required ECR repository and ECS service, including permission to pass the ECS task execution role.

**Successful GitHub Actions execution:**

https://github.com/suhasini57/production-grade-cloud-native-aws/actions/runs/44585518945

**Deployment commit:**

```text
319d4e3

Add automated ECS deployment pipeline
```

## 6. ECS Task Definition

An ECS task definition is a blueprint that specifies how a container should run.

It defines:

- Docker image location.
- CPU and memory allocation.
- Container name and port mapping.
- Fargate compatibility.
- Network mode.
- CloudWatch logging configuration.

The task definition is maintained in:

```text
ecs/task-definition.json
```

The automated deployment successfully registered task definition revision `2`.

## 7. Networking and Security

The Fargate task used the following network configuration during live testing:

| Setting | Value |
|---|---|
| VPC | `vpc-0a46d69ec2491d725` |
| Subnet | `subnet-0d0d4481c0d182dac` |
| Security Group | `aws-cloud-dashboard-sg` |
| Public IP Assignment | Enabled |
| Application Port | TCP `5000` |

During initial testing, the security group allowed public IPv4 and IPv6 access on port `5000`.

Those broad access rules were subsequently removed and replaced with a restricted IPv4 inbound rule:

```text
49.205.103.203/32
```

This allowed HTTP testing only from the test machine's public IPv4 address at that time.

**Important:** This IP address was a temporary testing restriction, not a permanent application access configuration. A production deployment should use an appropriate network design, such as an Application Load Balancer with restricted security group access.

No Application Load Balancer was used for this direct connectivity test.

## 8. Live Fargate Deployment Verification

The ECS service was temporarily configured with a desired task count of `1`.

The task was successfully launched on AWS Fargate.

**Verified task ID:**

```text
4a3a70717b764274b431006274b7f1a1
```

**Network interface:**

```text
eni-0f921564c2be367dc
```

**Temporary public IP:**

```text
18.60.233.86
```

### 8.1 Application Health Test

The `/health` endpoint was tested using:

```bash
curl -i http://18.60.233.86:5000/health
```

**Result:**

```http
HTTP/1.1 200 OK
Content-Type: application/json

{"status":"healthy"}
```

The HTTP `200 OK` response confirmed that the application health endpoint was responding successfully.

### 8.2 Dashboard Test

The dashboard endpoint was tested using:

```bash
curl -i http://18.60.233.86:5000/
```

**Result:**

```http
HTTP/1.1 200 OK
```

The dashboard HTML response confirmed that the Flask application was accessible from the test machine.

These results represent the successful live deployment test. The temporary public IP is not expected to remain assigned after the Fargate task stops.

## 9. CloudWatch Logging

Amazon CloudWatch collects application logs from the ECS container.

**Log Group:**

```text
/ecs/aws-cloud-dashboard-task
```

**Log Stream:**

```text
ecs/aws-cloud-dashboard/4a3a70717b764274b431006274b7f1a1
```

The retrieved logs confirmed:

- Flask application started successfully.
- Application listened on port `5000`.
- `/health` returned HTTP `200`.
- `/` returned HTTP `200`.
- A favicon request returned HTTP `404` because a favicon endpoint had not been implemented.

The logs also identified that the Flask built-in development server was being used.

**Planned production improvement:** Replace the Flask development server with Gunicorn.

## 10. Troubleshooting AWS CLI Parameters

During CloudWatch log retrieval, AWS CLI returned `InvalidParameterException` errors.

The troubleshooting process included:

1. Listing log groups without an optional prefix.
2. Retrieving the exact log group ARN.
3. Using the log group identifier without the trailing wildcard.
4. Retrieving available log streams.
5. Retrieving the actual log events.

The successful command for retrieving log events was:

```bash
aws logs get-log-events \
  --log-group-identifier "arn:aws:logs:ap-south-2:989445685277:log-group:/ecs/aws-cloud-dashboard-task" \
  --log-stream-name "ecs/aws-cloud-dashboard/4a3a70717b764274b431006274b7f1a1" \
  --region ap-south-2 \
  --start-from-head
```

**Key learning:** Read the exact error, identify the failing parameter, verify the resource identifier, and simplify the command before making changes to AWS resources.

## 11. Cost Management and Cleanup

The Fargate task was used temporarily for live application verification.

After successful testing, the ECS service desired count was changed back to zero.

The command used was:

```bash
aws ecs update-service \
  --cluster aws-cloud-dashboard-cluster \
  --service aws-cloud-dashboard-service \
  --desired-count 0 \
  --region ap-south-2
```

The service was verified with the following status after cleanup:

| Setting | Verified Value |
|---|---:|
| Desired Tasks | 0 |
| Running Tasks | 0 |
| Pending Tasks | 0 |

This stopped Fargate task compute usage while preserving the ECS service, cluster, task definitions, ECR repository, and stored logs.

**Cost considerations:**

- Scaling the service to zero stops Fargate task compute usage when no tasks are running.
- The ECS service and cluster can remain available for future deployment.
- ECR image storage may continue to incur charges.
- CloudWatch log storage and ingestion may incur charges.
- Other retained AWS resources, including networking resources, may also incur charges.

Scaling to zero does not mean that every AWS resource associated with the project is free.

## 12. Deployment Outcome

The deployment was successfully verified on AWS Fargate.

### Completed Activities

- GitHub Actions automated CI/CD.
- GitHub OIDC authentication to AWS.
- Automated Docker image publishing to ECR.
- ECS task definition registration.
- ECS service update.
- Fargate container launch.
- Live Flask application verification.
- HTTP health check with status `200`.
- Dashboard endpoint verification with status `200`.
- CloudWatch application log retrieval.
- ECS service scaled down to zero after testing.

## 13. Future Enhancements

The following improvements are planned and have not yet been implemented as part of this deployment:

1. Replace the Flask development server with Gunicorn.
2. Implement AWS infrastructure using Terraform.
3. Integrate an Application Load Balancer.
4. Configure Amazon RDS PostgreSQL.
5. Secure database credentials using AWS Secrets Manager.
6. Configure CloudWatch alarms and monitoring.
7. Implement Route 53, CloudFront, and AWS WAF.
8. Explore Kubernetes and Amazon EKS.

---

**Project:** Production-Grade Cloud-Native Application on AWS

**Repository:** https://github.com/suhasini57/production-grade-cloud-native-aws

**Deployment Status:** Successfully deployed and verified on AWS Fargate. ECS service scaled down to zero after testing.