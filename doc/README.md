# Documentation Index

Complete documentation for the Data Uploader application.

## 📋 Table of Contents

### 🚀 Setup & Deployment

Get the application running in your environment.

- **[Quick Start Guide](guides/QUICKSTART.md)** - Get up and running in 5 minutes
- **[Deployment Guide](setup/DEPLOYMENT.md)** - Production deployment with Docker, security, scaling
- **[Build Guide](setup/BUILD_GUIDE.md)** - Building from source, development setup
- **[Stack Management](setup/STACK_MANAGEMENT.md)** - Managing Docker services, troubleshooting

### 📖 User Guides

Learn how to use the application.

- **[Backend Setup](guides/BACKEND_SETUP.md)** - Backend configuration, CLI usage, upload scripts

### 📚 API & Reference

Technical reference documentation.

- **[API Documentation](reference/API_DOCUMENTATION.md)** - REST API endpoints, authentication, examples
- **[Database Schema](reference/DATABASE_SCHEMA.md)** - Data model, relationships, entity descriptions
- **[Grafana Queries](reference/GRAFANA_QUERIES.md)** - Analytics queries, dashboard examples

### 🔧 Development

For developers contributing to the project.

- **[Architecture](development/ARCHITECTURE.md)** - System design, components, data flow
- **[Project Structure](development/PROJECT_STRUCTURE.md)** - Code organization, file layout
- **[Testing](development/TESTING.md)** - Running tests, writing tests
- **[Endpoint Integration](development/ENDPOINT_INTEGRATION.md)** - API integration patterns
- **[Claude Code Instructions](development/CLAUDE.md)** - AI assistant guidance for development

### 🔐 AWS Administration

Tools and scripts for AWS configuration.

- **[AWS Admin Tools](../aws-admin/README.md)** - S3 permissions, CORS configuration
- **[S3 CORS Script](../scripts/configure_s3_cors.py)** - Configure bucket CORS for browser uploads

## 🗂️ Documentation Structure

```
doc/
├── README.md                    # This file
├── setup/                       # Setup and deployment
│   ├── DEPLOYMENT.md
│   ├── BUILD_GUIDE.md
│   └── STACK_MANAGEMENT.md
├── guides/                      # User guides
│   ├── QUICKSTART.md
│   └── BACKEND_SETUP.md
├── reference/                   # API and technical reference
│   ├── API_DOCUMENTATION.md
│   ├── DATABASE_SCHEMA.md
│   └── GRAFANA_QUERIES.md
├── development/                 # Development docs
│   ├── ARCHITECTURE.md
│   ├── PROJECT_STRUCTURE.md
│   ├── TESTING.md
│   ├── ENDPOINT_INTEGRATION.md
│   └── CLAUDE.md
└── archive/                     # Historical/archived docs
    ├── README_ORIGINAL.md
    ├── DEMO_CREDENTIALS.md
    └── ...
```

## 🎯 Quick Links

### Common Tasks

- **Deploy to production** → [Deployment Guide](setup/DEPLOYMENT.md)
- **Configure AWS S3** → [AWS Admin Tools](../aws-admin/README.md)
- **Run tests** → [Testing Guide](development/TESTING.md)
- **Understand the database** → [Database Schema](reference/DATABASE_SCHEMA.md)
- **Call the API** → [API Documentation](reference/API_DOCUMENTATION.md)
- **Build dashboards** → [Grafana Queries](reference/GRAFANA_QUERIES.md)

### Troubleshooting

- **Upload fails with CORS error** → [AWS CORS Configuration](../scripts/configure_s3_cors.py)
- **403 Forbidden on S3 upload** → [IAM Permissions Setup](../aws-admin/README.md)
- **Service won't start** → [Stack Management](setup/STACK_MANAGEMENT.md#troubleshooting)
- **Database issues** → [Deployment Troubleshooting](setup/DEPLOYMENT.md#troubleshooting)

## 📝 Documentation Standards

When contributing to documentation:

1. **Use clear headers** - Organize content with hierarchical headers
2. **Include code examples** - Show, don't just tell
3. **Add navigation** - Link to related documents
4. **Keep it updated** - Update docs when code changes
5. **Use diagrams** - Visual aids for complex concepts
6. **Test commands** - Verify all command examples work

## 🤝 Contributing

Found an error in the documentation? Want to improve it?

1. Edit the relevant Markdown file
2. Test any code examples or commands
3. Update the table of contents if needed
4. Submit a pull request

## 📧 Support

- 🐛 Report documentation issues in the [Issue Tracker](https://github.com/your-org/data_uploader/issues)
- 💬 Ask questions in [Discussions](https://github.com/your-org/data_uploader/discussions)
- 📧 Contact the team at your-email@example.com

---

**Last Updated:** December 26, 2025
