\# Amazon CloudWatch – Monitoring and Observability



\## 1. Project Overview



Amazon CloudWatch is an AWS monitoring and observability service. It collects metrics, logs, and other monitoring data from AWS resources and applications.



In this project, CloudWatch is used to monitor EC2 CPU utilization, evaluate alarms, inspect ECS application logs, and troubleshoot monitoring issues.



\## 2. Learning Objectives



\- Understand metrics, namespaces, dimensions, statistics, and periods.

\- Understand CloudWatch alarm states and thresholds.

\- Learn about log groups, log streams, and log events.

\- Understand ECS logging and the CloudWatch Agent.

\- Compare CloudWatch, CloudTrail, and AWS Config.

\- Use AWS CLI commands to inspect metrics and alarms.

\- Apply troubleshooting and cost-control practices.



\## 3. CloudWatch Architecture



The typical monitoring workflow is:



1\. AWS resources and applications generate metrics and logs.

2\. CloudWatch collects and stores the monitoring data.

3\. Users inspect metrics through graphs and dashboards.

4\. CloudWatch alarms evaluate metrics against configured conditions.

5\. Configured alarm actions can send notifications or initiate supported actions.



\## 4. Important CloudWatch Concepts



\### 4.1 Metrics



A metric is a time-ordered collection of measurements.



Examples:

\- EC2 CPU utilization

\- Network traffic

\- Application error counts

\- Request counts



This project uses the EC2 `CPUUtilization` metric.



\### 4.2 Namespace



A namespace groups related metrics.



Example: `AWS/EC2`



\### 4.3 Dimensions



Dimensions identify the resource associated with a metric.



Example:

\- Dimension: `InstanceId`

\- Value: `i-0bebcc23fc903f975`



\### 4.4 Statistics



Statistics summarize metric measurements.



Common statistics include:

\- Average

\- Minimum

\- Maximum

\- Sum

\- SampleCount



The EC2 CPU alarm uses the `Average` statistic.



\### 4.5 Period



A period specifies the time interval over which metric data is aggregated.



The CPU alarm in this project uses a 300-second period, equivalent to five minutes.



\## 5. CloudWatch Alarms



CloudWatch alarms evaluate metrics against configured conditions.



\### Alarm States



\- `OK`: The evaluated metric does not breach the alarm condition.

\- `ALARM`: The configured alarm condition has been met.

\- `INSUFFICIENT\_DATA`: There is insufficient data to evaluate the condition.



\### Important Alarm Settings



\- Metric and namespace

\- Dimensions

\- Statistic and period

\- Threshold

\- Evaluation periods

\- Datapoints to alarm

\- Missing-data treatment

\- Alarm actions



An alarm's state depends on its evaluation configuration and available datapoints.



\## 6. Practical Exercise: EC2 CPU Alarm



\### Existing Configuration



| Setting | Value |

|---|---|

| Alarm name | `EC2-High-CPU-Alarm` |

| Region | `ap-south-2` |

| Namespace | `AWS/EC2` |

| Metric | `CPUUtilization` |

| Instance ID | `i-0bebcc23fc903f975` |

| Statistic | `Average` |

| Period | 300 seconds |

| Evaluation periods | 1 |

| Datapoints to alarm | 1 |

| Threshold | Greater than 70% |

| Alarm actions | None configured |



\### Inspect the Alarm



```bash

aws cloudwatch describe-alarms \\

&#x20; --alarm-names EC2-High-CPU-Alarm \\

&#x20; --region ap-south-2 \\

&#x20; --query "MetricAlarms\[0].{Name:AlarmName,State:StateValue,Reason:StateReason,Threshold:Threshold}" \\

&#x20; --output table

```



\### Discover the CPU Metric



```bash

aws cloudwatch list-metrics \\

&#x20; --namespace AWS/EC2 \\

&#x20; --metric-name CPUUtilization \\

&#x20; --dimensions Name=InstanceId,Value=i-0bebcc23fc903f975 \\

&#x20; --region ap-south-2

```



\### Retrieve CPU Statistics



Example query for October 15, 2026:



```bash

aws cloudwatch get-metric-statistics \\

&#x20; --namespace AWS/EC2 \\

&#x20; --metric-name CPUUtilization \\

&#x20; --dimensions Name=InstanceId,Value=i-0bebcc23fc903f975 \\

&#x20; --start-time 2026-10-15T00:00:00Z \\

&#x20; --end-time 2026-10-16T00:00:00Z \\

&#x20; --period 300 \\

&#x20; --statistics Average \\

&#x20; --region ap-south-2

```



This command retrieves available datapoints for the specified UTC time range.



\### Results Observed



\- The CPU metric was successfully discovered.

\- One query returned a CPU utilization average of approximately `0.1216%`.

\- The alarm later returned the state `OK`.

\- Its evaluation reason reported a separate datapoint of approximately `0.00166%`, below the 70% threshold.



These values came from different timestamps.



The exercise verified the metric and alarm. It did not involve deliberately generating high CPU utilization.



\## 7. CloudWatch Logs



CloudWatch Logs centralizes logs from applications and AWS services.



\### Components



\- \*\*Log group:\*\* A collection of related log streams.

\- \*\*Log stream:\*\* A sequence of log events from a source.

\- \*\*Log event:\*\* An individual timestamped log entry.



\### Inspect Log Groups



```bash

aws logs describe-log-groups \\

&#x20; --region ap-south-2

```



Log groups discovered during the project:



\- `/ecs/aws-cloud-dashboard-task`

\- `/ecs/aws-learning-web-task`



The first log group contained stored data when inspected. A log group's existence does not guarantee that new events are currently arriving.



\### ECS Logging



The ECS task definition uses the `awslogs` logging driver to send container standard output and standard error to CloudWatch Logs.



Application logs help investigate:

\- Startup failures

\- Runtime errors

\- Database connection problems

\- Container behavior



Never log passwords, access keys, or other sensitive information.



\## 8. CloudWatch Agent



The CloudWatch Agent can collect additional system-level metrics and logs from supported environments.



Depending on its configuration, it can collect:

\- Memory utilization

\- Disk utilization

\- Additional system metrics

\- Application log files



Standard EC2 monitoring provides metrics such as CPU utilization, network traffic, and disk I/O. The agent can provide additional operating-system metrics, such as memory utilization.



The agent was studied conceptually in this project, but its installation on the EC2 instance was not verified.



\## 9. Custom Metrics and Metric Filters



\### Custom Metrics



Applications can publish their own metrics.



Examples:

\- Failed deployment count

\- Application error count

\- Business transaction failures

\- Queue processing delays



Custom metrics help monitor application behavior that infrastructure metrics alone cannot describe.



\### Metric Filters



Metric filters identify patterns in incoming log events and can publish matching counts or values as CloudWatch metrics.



Example: count application error messages and create an alarm when the error count increases.



No metric filters were configured in the log groups inspected during this exercise.



\## 10. CloudWatch vs. CloudTrail vs. AWS Config



| Service | Purpose | Example |

|---|---|---|

| Amazon CloudWatch | Monitoring metrics, logs, and alarms | Monitor EC2 CPU utilization |

| AWS CloudTrail | Recording AWS API activity | Investigate who stopped an EC2 instance |

| AWS Config | Tracking resource configurations and changes | Review security group configuration changes |



These services complement each other but serve different purposes.



\## 11. Troubleshooting



\### Problem: No Metric Datapoints



Possible causes:

\- Incorrect AWS Region

\- Incorrect resource ID

\- Requested time range contains no available datapoints

\- Metrics have not yet been published

\- Metric is inactive or unavailable for the selected interval



Troubleshooting steps:

1\. Verify the resource ID and Region.

2\. Run `list-metrics`.

3\. Check the UTC start and end times.

4\. Query an appropriate recent time range.

5\. Check the resource state and monitoring configuration.



\### Problem: Alarm Is INSUFFICIENT\_DATA



Possible causes:

\- Insufficient datapoints

\- Missing metric measurements

\- A recently created or reconfigured alarm

\- Missing-data handling affecting evaluation



Inspect the alarm's state reason before changing its configuration.



\### Problem: ECS Logs Are Missing



Check:

\- Task definition logging configuration

\- Log group and Region

\- ECS task execution role permissions

\- Whether the task ran and generated output

\- Task stopped reason and application startup logs



\## 12. Cost and Security Best Practices



\- Stop EC2 instances when they are not needed.

\- Remember that EBS storage can still incur charges while EC2 is stopped.

\- Avoid unnecessary dashboards, alarms, log groups, and custom metrics.

\- Review log retention settings to manage storage costs.

\- Check CloudWatch pricing before enabling additional monitoring features.

\- Use least-privilege IAM permissions.

\- Avoid using the AWS root account for routine administration.

\- Never commit credentials or secrets to GitHub.

\- Avoid enabling automated remediation during initial learning exercises.



\## 13. Learning Outcomes



This exercise demonstrated how to:



\- Discover EC2 metrics using the AWS CLI.

\- Retrieve CPU statistics for a selected time range.

\- Inspect an existing CloudWatch alarm.

\- Interpret alarm states.

\- Discover CloudWatch log groups.

\- Understand ECS container logging.

\- Identify common monitoring issues and cost considerations.



The exercise verified the existing EC2 metric and alarm. It did not configure notification actions or verify installation of the CloudWatch Agent.



\## 14. Interview Summary



Amazon CloudWatch is an AWS monitoring and observability service that collects metrics and logs from AWS resources and applications. Metrics can be visualized in dashboards and evaluated by alarms. Alarms can trigger configured actions when their conditions are met. CloudWatch Logs supports centralized troubleshooting, while the CloudWatch Agent collects additional system-level metrics and logs. CloudWatch is commonly used with EC2 and ECS to improve application visibility and operational reliability.



