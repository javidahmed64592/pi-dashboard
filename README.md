[![python](https://img.shields.io/badge/Python-3.13-3776AB.svg?style=flat&logo=python&logoColor=ffd343)](https://docs.python.org/3.13/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![CI](https://img.shields.io/github/actions/workflow/status/javidahmed64592/pi-dashboard/ci.yml?branch=main&style=flat-square&label=CI&logo=github)](https://github.com/javidahmed64592/pi-dashboard/actions/workflows/ci.yml)
[![Build](https://img.shields.io/github/actions/workflow/status/javidahmed64592/pi-dashboard/build.yml?branch=main&style=flat-square&label=Build&logo=github)](https://github.com/javidahmed64592/pi-dashboard/actions/workflows/build.yml)
[![Docker](https://img.shields.io/github/actions/workflow/status/javidahmed64592/pi-dashboard/docker.yml?branch=main&style=flat-square&label=Docker&logo=github)](https://github.com/javidahmed64592/pi-dashboard/actions/workflows/docker.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<!-- omit from toc -->
# Pi Dashboard

A FastAPI-based dashboard for monitoring on a Raspberry Pi.

<!-- omit from toc -->
## Table of Contents
- [Quick Start - From Source](#quick-start---from-source)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Generate API Token](#generate-api-token)
  - [Build the UI](#build-the-ui)
  - [Run the Server](#run-the-server)
- [Links](#links)
- [Documentation](#documentation)
- [License](#license)

## Quick Start - From Source

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```sh
# Clone the repository
git clone https://github.com/javidahmed64592/pi-dashboard.git
cd pi-dashboard

# Install dependencies
uv sync --extra dev
```

### Generate API Token

```sh
uv run generate-new-token
# ⚠️ Save the displayed token - you'll need it for API requests!
```

### Build the UI

```sh
cd pi-dashboard-frontend
npm install
npm run build
cp -r out ../static
```

### Run the Server

```sh
# Start the server
uv run pi-dashboard
```

## Links

- Access the web application: https://localhost:443
- Server runs at: https://localhost:443/api
- Swagger UI: https://localhost:443/api/docs
- Redoc: https://localhost:443/api/redoc

## Documentation

- **[API Documentation](./docs/API.md)**: API architecture and endpoints
- **[Software Maintenance Guide](./docs/SMG.md)**: Development setup, configuration
- **[Workflows](./docs/WORKFLOWS.md)**: CI/CD pipeline details

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
