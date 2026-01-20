<!-- omit from toc -->
# API

This document summarizes the API endpoints specific to the Pi Dashboard application.

## Base Server Infrastructure

The Pi Dashboard application is built from [python-template-server](https://github.com/javidahmed64592/python-template-server), which provides production-ready infrastructure including:

- **API Key Authentication**: All authenticated endpoints require the `X-API-Key` header with a SHA-256 hashed token
- **Rate Limiting**: Configurable request throttling (default: 100 requests/minute per IP)
- **Security Headers**: Automatic HSTS, CSP, and X-Frame-Options enforcement
- **Request Logging**: Comprehensive logging of all requests/responses with client IP tracking
- **Health Checks**: Standard `/api/health` endpoint for availability monitoring
- **HTTPS Support**: Built-in SSL certificate generation and management

For detailed information about these features, authentication token generation, server middleware, and base configuration, see the [python-template-server README](https://github.com/javidahmed64592/python-template-server/blob/main/README.md) and [python-template-server API documentation](https://github.com/javidahmed64592/python-template-server/blob/main/docs/API.md).

## Frontend Client

The project includes a Next.js frontend (`pi-dashboard-frontend/`) with a TypeScript API client (`src/lib/api.ts`) that handles:

- **Authentication**: Automatic API key injection via Axios interceptors
- **Error Handling**: Extracts FastAPI error details from response messages
- **Type Safety**: Full TypeScript support with Pydantic-aligned models (`src/lib/types.ts`)
- **Functions**: `getHealth()`, `login()`

<!-- omit from toc -->
## Table of Contents
- [Base Server Infrastructure](#base-server-infrastructure)
- [Frontend Client](#frontend-client)
- [API Documentation](#api-documentation)
  - [Swagger UI (/api/docs)](#swagger-ui-apidocs)
  - [ReDoc (/api/redoc)](#redoc-apiredoc)

## API Documentation

FastAPI automatically generates interactive API documentation.

### Swagger UI (/api/docs)

**URL**: `https://localhost:443/api/docs`

**Purpose**: Interactive API documentation with "Try it out" functionality

### ReDoc (/api/redoc)

**URL**: `https://localhost:443/api/redoc`

**Purpose**: Alternative API documentation with a clean, three-panel layout
