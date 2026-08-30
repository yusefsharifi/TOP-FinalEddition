# TOP WorX ERP System

A comprehensive ERP system built with FastAPI and React.

## Features

- User Management and Authentication
- Role-Based Access Control
- Multi-language Support (English and Persian)
- Dashboard and Analytics
- Project Management
- Asset Management
- Inventory Management
- Financial Management
- Document Management
- Reporting System
- API Integration
- Real-time Notifications
- Mobile Responsive Design

## Tech Stack

### Backend
- FastAPI (Python web framework)
- SQL Server (Database)
- SQLAlchemy (ORM)
- Pydantic (Data validation)
- JWT (Authentication)
- Alembic (Database migrations)
- Redis (Caching)
- Celery (Task queue)
- OpenAI (AI features)

### Frontend
- React with TypeScript
- Material-UI
- Redux Toolkit
- React Query
- React Router
- i18next (Internationalization)
- Chart.js (Visualizations)
- Axios (HTTP client)

## Prerequisites

- Docker and Docker Compose
- Node.js 18.x or later
- Python 3.11 or later
- SQL Server 2022
- Redis

## Getting Started

### Using Docker (Recommended)

#### Development Environment

1. Clone the repository:
```bash
git clone https://github.com/yourusername/topworx-erp.git
cd topworx-erp
```

2. Create a `.env.dev` file:
```bash
cp .env.dev.example .env.dev
```

3. Build and start the development containers:
```bash
docker-compose -f docker-compose.dev.yml up --build
```

4. Access the applications:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Flower (Celery monitoring): http://localhost:5555

#### Production Environment

1. Clone the repository:
```bash
git clone https://github.com/yourusername/topworx-erp.git
cd topworx-erp
```

2. Create a `.env.prod` file:
```bash
cp .env.prod.example .env.prod
```

3. Build and start the production containers:
```bash
docker-compose -f docker-compose.prod.yml up --build
```

4. Access the applications:
- Frontend: https://www.topworx.com
- Backend API: https://api.topworx.com
- API Documentation: https://api.topworx.com/docs
- Flower (Celery monitoring): https://www.topworx.com/flower

### Manual Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/topworx-erp.git
cd topworx-erp
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
```

3. Set up the frontend:
```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with your configuration
```

4. Start the development servers:

Backend:
```bash
cd backend
uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm start
```

## Development

### Backend Development

1. Create a new branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and commit:
```bash
git add .
git commit -m "feat: your feature description"
```

3. Run tests:
```bash
pytest
```

4. Push your changes:
```bash
git push origin feature/your-feature-name
```

### Frontend Development

1. Create a new branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and commit:
```bash
git add .
git commit -m "feat: your feature description"
```

3. Run tests:
```bash
npm test
```

4. Push your changes:
```bash
git push origin feature/your-feature-name
```

## API Documentation

The API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Deployment

### Using Docker

1. Build the production images:
```bash
docker-compose -f docker-compose.prod.yml build
```

2. Start the production environment:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment

1. Backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

2. Frontend:
```bash
cd frontend
npm install
npm run build
npm run start
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please contact:
- Email: support@topworx.com
- Website: https://www.topworx.com
- Documentation: https://docs.topworx.com 