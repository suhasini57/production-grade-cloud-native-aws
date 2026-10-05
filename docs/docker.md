\# Docker



\## Objective



Containerize the Flask-based AWS Cloud Operations Dashboard application.



\## Docker Concept



Docker packages an application together with its dependencies into a container.



This allows the application to run consistently across different environments.



\## Dockerfile



The project uses Python 3.12 slim as the base image.



The Dockerfile:



1\. Creates a Python environment

2\. Sets `/app` as the working directory

3\. Copies requirements.txt

4\. Installs Python dependencies

5\. Copies the Flask application

6\. Exposes port 5000

7\. Starts the Flask application



\## Build Docker Image



```bash

docker build -t aws-cloud-dashboard .

