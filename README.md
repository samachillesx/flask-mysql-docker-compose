# Flask + MySQL Two-Tier Application | Docker Compose & AWS EC2

A containerized Flask web application backed by MySQL, deployed to an AWS EC2 instance using Docker Compose and Nginx as a reverse proxy.

This project demonstrates the deployment and operation of a multi-container application, including service communication, environment-based configuration, persistent database storage, application health checks, and Linux server administration.

## Project Overview

The application is a simple task manager that allows users to create, view, complete, and delete tasks. Flask handles application logic and HTTP requests, while MySQL stores task records persistently.

Docker Compose manages the application and database containers. Nginx serves as the public entry point, forwarding incoming HTTP requests to the Flask application running inside Docker.

The application was deployed successfully to an AWS EC2 instance and verified through its public IP address.

## Architecture

```text
                         User / Browser
                               |
                               | HTTP :80
                               v
                    AWS EC2 Security Group
                               |
                               v
                         Nginx (EC2)
                         Reverse Proxy
                               |
                               | 127.0.0.1:5000
                               v
                    Flask Application
                       Docker Container
                               |
                               | Docker Network
                               v
                      MySQL Database
                       Docker Container
                               |
                               v
                       Named Volume
                     Persistent Storage
```

### Architecture Components

| Component | Responsibility |
|---|---|
| AWS EC2 | Hosts the application and supporting services |
| Docker | Packages the application and database into containers |
| Docker Compose | Defines and manages the multi-container stack |
| Flask | Handles application routes and business logic |
| MySQL | Stores task data |
| Nginx | Receives HTTP requests and proxies them to Flask |
| Docker named volume | Persists MySQL data beyond container recreation |
| Environment variables | Configure database credentials and connection settings |

## Technology Stack

- **Cloud:** Amazon Web Services (AWS)
- **Compute:** Amazon EC2
- **Operating system:** Amazon Linux 2023
- **Application:** Python and Flask
- **Database:** MySQL 8.0
- **Containerization:** Docker
- **Container orchestration:** Docker Compose
- **Web server / reverse proxy:** Nginx
- **Application server:** Gunicorn
- **Version control:** Git and GitHub

## Repository Structure

```text
flask-mysql-docker-compose/
├── app/
│   ├── app.py
│   ├── config.py
│   ├── templates/
│   │   └── index.html
│   └── static/
│       └── style.css
├── mysql/
│   └── init.sql
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

The `.env` file is created locally or on the deployment server and is intentionally excluded from version control.

## Key Implementation Details

### 1. Containerized Application

A Dockerfile packages the Flask application and its Python dependencies into a reproducible image. Gunicorn runs the Flask application inside the container, rather than relying on Flask's development server for deployment.

### 2. Multi-Container Management

Docker Compose defines the Flask and MySQL services, their configuration, networking, restart policies, and storage.

The application connects to MySQL using the database service name on the Compose network. This allows internal service discovery without exposing MySQL directly to the public internet.

### 3. Persistent Database Storage

A Docker named volume stores MySQL data outside the database container's writable layer.

This ensures that task records can survive normal container replacement and recreation, provided the volume is retained.

### 4. Database Initialization

The `mysql/init.sql` script initializes the database schema and can insert initial records when MySQL initializes a fresh data directory.

The initialization script is not automatically rerun on an already initialized database volume. Subsequent schema changes require an appropriate database migration or administration process.

### 5. Health Checks and Startup Dependencies

The MySQL health check uses `mysqladmin ping` to monitor database availability.

Docker Compose uses the database health status to control when the Flask service starts. This helps prevent the application from starting before MySQL is ready to accept connections.

The Flask `/health` endpoint checks database connectivity and returns a healthy response when the application can reach MySQL.

### 6. Reverse Proxy Configuration

Nginx runs on the EC2 host and forwards incoming HTTP requests to the Flask service.

The Flask port is bound to the host's loopback interface, `127.0.0.1:5000`, so external clients access the application through Nginx rather than directly through the Flask port.

## Local Development

### Prerequisites

Install the following tools:

- Python 3.12 or a compatible version
- Docker Engine
- Docker Compose plugin
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/flask-mysql-docker-compose.git
cd flask-mysql-docker-compose
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Configure Environment Variables

Create a local environment file from the example:

```bash
cp .env.example .env
```

Update `.env` with appropriate values for the database configuration.

Example:

```dotenv
MYSQL_ROOT_PASSWORD=replace_with_a_strong_root_password
MYSQL_DATABASE=taskdb
MYSQL_USER=taskuser
MYSQL_PASSWORD=replace_with_a_strong_user_password
MYSQL_HOST=mysql
MYSQL_PORT=3306
```

Use strong credentials and do not commit `.env` to GitHub.

Ensure the values used by Docker Compose and the application are consistent.

### 3. Start the Application

```bash
docker compose up -d --build
```

This builds the application image, creates the required containers and network, and starts the services.

### 4. Verify the Containers

```bash
docker compose ps
```

Inspect application logs:

```bash
docker compose logs --tail=100 web
```

Inspect database logs:

```bash
docker compose logs --tail=100 mysql
```

### 5. Test the Application

Open:

```text
http://localhost:5000
```

Check application and database connectivity:

```bash
curl -i http://localhost:5000/health
```

A successful health check returns HTTP `200 OK` with a healthy status and database connectivity information.

## AWS EC2 Deployment

The application was deployed to an AWS EC2 instance running Amazon Linux 2023.

### Deployment Process

1. Provision an EC2 instance and configure SSH access.
2. Install the required tools, including Docker, Docker Compose, Git, and Nginx.
3. Retrieve the project source code from GitHub.
4. Create the server-side `.env` file with deployment-specific database credentials.
5. Build and start the application stack using Docker Compose.
6. Configure Nginx to forward HTTP traffic to `127.0.0.1:5000`.
7. Configure the EC2 security group to permit the required inbound traffic.
8. Validate the application through its public IP address and health endpoint.

### Network and Security Configuration

The intended deployment access model is:

| Port | Service | Access |
|---|---|---|
| 22 | SSH | Restricted to the administrator's IP address |
| 80 | HTTP / Nginx | Public web access |
| 443 | HTTPS | To be configured when a domain and TLS certificate are available |
| 5000 | Flask | Bound to host loopback; not intended for public access |
| 3306 | MySQL | Internal Docker network only |

Security group rules and host firewall settings should follow the same principle of limiting access to only what is required.

### Accessing the Deployed Application

Open the EC2 instance's public IPv4 address in a browser:

```text
http://EC2_PUBLIC_IP
```

Replace `EC2_PUBLIC_IP` with the instance's actual public IP address.

The application was successfully accessed through this endpoint after configuring Nginx to proxy requests to Flask.

**HTTPS status:** HTTPS is not yet configured because a domain name and TLS certificate have not been set up. The current deployment uses HTTP and should be treated as a demonstration environment, not a production-hardened public service.

For a subsequent deployment stage, configure a domain, point it to a stable public IP address (for example, an Elastic IP), and enable HTTPS with a trusted TLS certificate.

## Health Checks and Troubleshooting

### Application Health

```bash
curl -i http://127.0.0.1:5000/health
```

For a response through Nginx:

```bash
curl -i http://127.0.0.1/health
```

### Inspect Service Status

```bash
docker compose ps
```

### View Application Logs

```bash
docker compose logs -f web
```

### View Database Logs

```bash
docker compose logs -f mysql
```

### Validate Nginx Configuration

```bash
sudo nginx -t
```

### Check Nginx Service Status

```bash
sudo systemctl status nginx
```

### Common Issues

| Issue | Potential cause | Troubleshooting approach |
|---|---|---|
| Nginx welcome page appears | Default Nginx site is still serving requests | Inspect the active server block and verify `proxy_pass` |
| Flask cannot connect to MySQL | Incorrect credentials, hostname, or database readiness | Verify environment variables, Compose networking, and database logs |
| Health endpoint returns HTTP 503 | Application cannot connect to the database | Inspect Flask logs and MySQL health status |
| Application is unreachable publicly | Security group, Nginx, or host firewall configuration | Check inbound rules, Nginx status, and local connectivity |
| Tasks disappear after recreation | Volume not mounted correctly or data volume removed | Verify the named volume and its Compose configuration |
| Port binding fails | Another process already uses the requested port | Inspect listening services and container port mappings |

Avoid running `docker compose down -v` during routine troubleshooting because it removes the Compose-managed named volumes and can delete the database's persisted data.

## Security Considerations

The project incorporates several basic deployment practices:

- Configuration and database credentials are supplied through environment variables.
- The `.env` file is excluded from version control.
- MySQL is not intended to be publicly exposed.
- Flask is bound to the EC2 host's loopback interface.
- Nginx serves as the public HTTP entry point.
- SSH access should be restricted to trusted source IP addresses.
- Container logs and health checks provide useful operational visibility.

Further hardening is required before production use, including HTTPS, secure secret management, least-privilege access, system patching, backup and recovery procedures, and monitoring.

## Challenges and Lessons Learned

### Application-to-Database Connectivity

The Flask application must use the correct database hostname and credentials. Within a Compose network, the MySQL service name is used for service-to-service communication rather than `localhost`.

### Container Startup Order

Starting a container does not necessarily mean the service inside it is ready. A database health check and a health-based startup dependency help coordinate service startup.

### Persistent Data

Containers are replaceable, but application data must be stored separately. Docker named volumes provide persistent storage for MySQL data across normal container recreation.

### Nginx Reverse Proxy

A running Nginx service can still serve its default welcome page if the active server configuration does not route requests to the application. Inspecting the active configuration and testing the upstream application separately helps isolate the problem.

### Cloud Networking

Successful container startup does not guarantee public accessibility. The application, host-level services, port bindings, security group rules, and reverse proxy must all be configured consistently.

### HTTP and HTTPS

A public IP address can support an initial HTTP demonstration, but trusted HTTPS requires appropriate TLS configuration. A domain and certificate will be added in a later improvement stage.

## Future Improvements

- Configure HTTPS with a domain name and trusted TLS certificate.
- Store deployment secrets in a dedicated secret-management service.
- Introduce automated CI/CD using GitHub Actions.
- Add automated application and database integration tests.
- Implement database backup and restore procedures.
- Add centralized logging, monitoring, and alerting.
- Evaluate automated container image scanning and dependency vulnerability checks.
- Improve deployment repeatability through infrastructure as code.
- Establish a documented recovery procedure for application and database failures.

## Project Status

**Status: Deployed successfully to AWS EC2**

The Flask application and MySQL database run as Docker Compose services. Nginx forwards HTTP requests to Flask, and the application is accessible through the EC2 public IP address.

HTTPS and additional production hardening remain planned improvements.

## Author

**Sam Achilles**

Cloud Computing | DevOps | Infrastructure | Application Deployment

GitHub: [My GitHub Profile](https://github.com/samachillesx)

