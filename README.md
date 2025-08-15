# AI Hub AI/ML Wrangler

> A sophisticated statistical data imputation and analysis tool with AI-powered recommendations for feature engineering, encoding, and imputation strategies.

## 🚀 Overview

AI Hub AI/ML Wrangler is a web-based application designed for data scientists and research scientists to handle missing data in large datasets intelligently. The system leverages OpenAI's API to provide context-aware suggestions and automates complex statistical operations through an intuitive interface that mirrors the familiar AI Hub Data Wrangler design.

## ✨ Key Features

- **🤖 AI-Powered Analysis**: Utilizes OpenAI API for intelligent dataset assessment and recommendations
- **📊 Comprehensive Imputation**: Supports statistical, ML-based, correlation-based, and time-series methods
- **📈 Correlation Analysis**: Generates publication-ready correlation matrices with visualization
- **📝 Detailed Reporting**: Produces comprehensive markdown reports with full transformation audit trails
- **⚡ Large Dataset Support**: Efficiently handles datasets >100MB with >1M rows
- **🔄 Interactive Configuration**: Real-time preview and comparison of imputation strategies
- **🎨 Familiar UI**: Consistent design with AI Hub Data Wrangler for seamless user experience

## 🛠️ Technology Stack

### Frontend
- React 18 with TypeScript
- Vite build tool
- Tailwind CSS
- Recharts & Plotly.js for visualizations
- Axios for API communication

### Backend
- FastAPI (Python 3.10+)
- Pandas, NumPy, Scikit-learn
- Celery with Redis for task queuing
- PostgreSQL database
- Docker containerization

## 📋 Prerequisites

- Node.js >= 18.0.0
- Python >= 3.10
- Docker and Docker Compose
- PostgreSQL 15
- Redis 7

## 🚀 Quick Start

### Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/[username]/aihub_ai_ml_wrangler.git
cd aihub_ai_ml_wrangler
```

2. **Install dependencies**
```bash
# Install npm packages
npm install

# Set up Python virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration (OpenAI API key, database credentials, etc.)
```

4. **Start with Docker Compose**
```bash
docker-compose -f docker-compose.dev.yml up
```

5. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Manual Development (without Docker)

**Backend:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

## 📁 Project Structure

```
aihub_ai_ml_wrangler/
├── frontend/                # React TypeScript application
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API service layer
│   │   └── stores/        # State management
├── backend/                # FastAPI Python application
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── services/      # Business logic
│   │   ├── ml_modules/    # ML implementations
│   │   └── models/        # Database models
├── docker/                 # Docker configurations
├── docs/                   # Documentation
└── sample_data/           # Sample datasets for testing
```

## 🔄 Workflow

1. **Import**: Upload Data Wrangler export files (CSV, JSON)
2. **Analyze**: AI-powered analysis of missing data patterns
3. **Configure**: Select imputation strategies with AI recommendations
4. **Preview**: Real-time preview of imputation results
5. **Apply**: Process data with selected strategies
6. **Export**: Download imputed data, correlation matrices, and reports

## 📊 Output Files

- `[filename]_imputed.csv` - Complete dataset with imputed values
- `[filename]_correlation.csv` - Correlation matrix in standard format
- `[filename]_ml_report.md` - Comprehensive analysis report
- `[filename]_ml_metadata.json` - Complete transformation audit trail

## 🧪 Testing

```bash
# Run all tests
npm test

# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e
```

## 📚 Documentation

- [User Guide](docs/user-guide.md)
- [API Reference](docs/api-reference.md)
- [Development Guide](docs/development.md)
- [Deployment Guide](docs/deployment.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [AI Hub Data Wrangler](https://github.com/dixonjohgithub/aihub_data_wrangler) - Data preparation and transformation tool
- [Research Pipeline](https://dev.hsrn.nyu.edu/ai-hub/research_pipeline) - Core ML modules

## 📧 Support

For issues and questions:
- Create an issue on [GitHub Issues](https://github.com/[username]/aihub_ai_ml_wrangler/issues)
- Contact the AI Hub team at support@aihub.example.com

## 🙏 Acknowledgments

- OpenAI for API integration
- The AI Hub Data Wrangler team for UI/UX patterns
- The Research Pipeline team for ML modules

---

Built with ❤️ by the AI Hub Team