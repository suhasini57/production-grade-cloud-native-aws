# ECS and Fargate Deployment Documentation

## 1. Project Overview

This document explains how the AWS Cloud Dashboard Flask application was deployed on Amazon ECS using AWS Fargate.

The deployment uses GitHub Actions for CI/CD, Amazon ECR for Docker image storage, Amazon ECS for container orchestration, and AWS Fargate for serverless container execution.

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

The workflow automates testing, image publishing, ECS deployment and application logging.

## 3. AWS Configuration

| Component | Configuration |

|---|---|

| AWS Region | ap-south-2 |

| ECS Cluster | aws-cloud-dashboard-cluster |

| ECS Service | aws-cloud-dashboard-service |

| Task Definition Family | aws-cloud-dashboard-task |

| Verified Revision | 2 |

| Launch Type | Fargate |

| Operating System | Linux |

| CPU Architecture | X86\_64 |

| CPU | 256 (0.25 vCPU) |

| Memory | 512 MB |

| Network Mode | awsvpc |

| Container Name | aws-cloud-dashboard |

| Container Port | 5000 |

| ECR Repository | aws-cloud-dashboard |

## 4. Docker Image and Amazon ECR

The Flask application was packaged as a Docker image and stored in Amazon Elastic Container Registry (ECR).

ECR Repository:

```text

989445685277.dkr.ecr.ap-south-2.amazonaws.com/aws-cloud-dashboard

```

The GitHub Actions workflow publishes two tags:

\- Git commit SHA: uniquely identifies the application version.

\- latest: identifies the most recently published image.

The verified deployment image used commit:

```text

319d4e32cc7408b56edf9618468211472a1c000f

```

## 5. GitHub Actions and Automated ECS Deployment

The CI/CD workflow automates the following activities:

1\. Checks out the GitHub repository.

2\. Installs Python dependencies.

3\. Executes Flask application tests.

4\. Builds the Docker image.

5\. Authenticates to AWS using GitHub OIDC.

6\. Authenticates with Amazon ECR.

7\. Publishes the Docker image to ECR.

8\. Renders the ECS task definition with the new image.

9\. Registers a new ECS task definition revision.

10\. Updates the ECS service.

The workflow uses IAM permissions scoped to the required ECR repository and ECS service, with permission to pass the ECS task execution role.

The successful GitHub Actions execution:

https://github.com/suhasini57/production-grade-cloud-native-aws/actions/runs/44585518945

Commit:

```text

319d4e3

Add automated ECS deployment pipeline

```

## 6. ECS Task Definition

The ECS task definition specifies:

\- Docker image location.

\- CPU and memory allocation.

\- Container name and port mapping.

\- Fargate compatibility.

\- Network mode.

\- CloudWatch logging configuration.

The task definition is maintained in:

```text

ecs/task-definition.json

```

The automated deployment successfully registered revision 2.

## 7. Networking and Security

The Fargate task uses the following network configuration:

| Setting | Value |

|---|---|

| VPC | vpc-0a46d69ec2491d725 |

| Subnet | subnet-0d0d4481c0d182dac |

| Security Group | aws-cloud-dashboard-sg |

| Public IP Assignment | Enabled |

| Application Port | TCP 5000 |

During live testing, the security group initially allowed public IPv4 and IPv6 access on port 5000.

For security, those rules were removed and replaced with a restricted IPv4 rule:

```text

49.205.103.203/32

```

This allowed HTTP testing only from the test machine's public IPv4 address at that time.

No Application Load Balancer was used for this direct connectivity test.

## 8. Live Fargate Deployment Verification

The ECS service was temporarily configured with desired count 1.

The task was successfully launched on AWS Fargate.

Verified task ID:

```text

4a3a70717b764274b431006274b7f1a1

```

Network interface:

```text

eni-0f921564c2be367dc

```

Temporary public IP:

```text

18.60.233.86

```

### Application Health Test

Command:

```bash

curl -i http://18.60.233.86:5000/health

```

Result:

```http

HTTP/1.1 200 OK

Content-Type: application/json

{"status":"healthy"}

```

### Dashboard Test

Command:

```bash

curl -i http://18.60.233.86:5000/

```

Result:

```http

HTTP/1.1 200 OK

```

The dashboard HTML response confirmed that the Flask application was accessible from the test machine.

## 9. CloudWatch Logging

CloudWatch collects application logs from the ECS container.

Log Group:

```text

/ecs/aws-cloud-dashboard-task

```

Log Stream:

```text

ecs/aws-cloud-dashboard/4a3a70717b764274b431006274b7f1a1

```

The retrieved logs confirmed:

\- Flask application started successfully.

\- Application listened on port 5000.

\- `/health` returned HTTP 200.

\- `/` returned HTTP 200.

\- A favicon request returned HTTP 404 because a favicon endpoint was not implemented.

The logs also identified that Flask's built-in development server was being used.

Production improvement planned: replace the Flask development server with Gunicorn.

## 10. Troubleshooting AWS CLI Parameters

During CloudWatch log retrieval, AWS CLI returned InvalidParameterException errors.

The troubleshooting process included:

1\. Listing log groups without an optional prefix.

2\. Retrieving the exact log group ARN.

3\. Using the log group identifier without the trailing wildcard.

4\. Retrieving available log streams.

5\. Retrieving the actual log events.

The successful command for retrieving log events used:

```bash

aws logs get-log-events \\

  --log-group-identifier "arn:aws:logs:ap-south-2:989445685277:log-group:/ecs/aws-cloud-dashboard-task" \\

  --log-stream-name "ecs/aws-cloud-dashboard/4a3a70717b764274b431006274b7f1a1" \\

  --region ap-south-2 \\

  --start-from-head

```

Key lesson: Read the exact error, identify the failing parameter, verify the resource identifier and simplify the command before changing AWS resources.

## 11. Cost Management and Cleanup

The Fargate task was used temporarily for live verification.

After successful testing, the ECS service desired count was changed back to zero.

Command:

```bash

aws ecs update-service \\

  --cluster aws-cloud-dashboard-cluster \\

  --service aws-cloud-dashboard-service \\

  --desired-count 0 \\

  --region ap-south-2

```

Final verified service status:

| Setting | Value |

|---|---:|

| Desired Tasks | 0 |

| Running Tasks | 0 |

| Pending Tasks | 0 |

This stops Fargate task compute usage while preserving the ECS service, cluster, task definitions, ECR repository and stored logs.

Other AWS resources, including log storage and networking resources, may still incur charges.

## 12. Deployment Outcome

The deployment was successfully verified.

Completed:

\- GitHub Actions automated CI/CD.

\- GitHub OIDC authentication to AWS.

\- Automated Docker image publishing to ECR.

\- ECS task definition registration.

\- ECS service update.

\- Fargate container launch.

\- Live Flask application verification.

\- HTTP health check with status 200.

\- Dashboard endpoint verification with status 200.

\- CloudWatch application log retrieval.

\- ECS service scaled down to zero after testing.

## 13. Future Enhancements

Planned improvements:

1\. Replace Flask development server with Gunicorn.

2\. Implement AWS infrastructure using Terraform.

3\. Integrate Application Load Balancer.

4\. Configure RDS PostgreSQL.

5\. Secure database credentials using AWS Secrets Manager.

6\. Configure CloudWatch alarms and monitoring.

7\. Implement Route 53, CloudFront and AWS WAF.

8\. Explore Kubernetes and Amazon EKS.

\---

\*\*Project:\*\* Production-Grade Cloud-Native Application on AWS

\*\*Repository:\*\* https://github.com/suhasini57/production-grade-cloud-native-aws

\*\*Deployment Status:\*\* Successfully verified on AWS Fargate.
