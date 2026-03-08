# InsightWrite - Data-Driven Article Publishing Platform

A full-stack Django application with AI-powered recommendations, advanced analytics, and real-time user behavior tracking.

## 🚀 Features

### Step 1: Basic Website ✅
- User registration & login (Reader/Writer/Admin roles)
- Create, edit, publish articles
- Categories & tags
- Likes, comments, views
- Search articles

### Step 2: Data Collection ✅
- User interaction tracking
- Reading sessions
- Scroll depth
- Time on page
- User journey mapping

### Step 3: Reader Behavior Analysis ✅
- Popular categories analysis
- Reading patterns
- Drop-off points
- Engagement metrics

### Step 4: Article Recommendation System ✅
- TF-IDF content similarity
- Collaborative filtering
- Personalized recommendations
- Similar articles

### Step 5: Sentiment Analysis ✅
- Comment sentiment scoring
- Article sentiment analysis
- Engagement insights

### Step 6: Trending Prediction ✅
- ML-based trending prediction
- Velocity calculations
- Engagement rate analysis

### Step 7: Writer Dashboard ✅
- Performance analytics
- Audience insights
- Content suggestions

### Step 8: Admin Analytics ✅
- Platform growth metrics
- User behavior insights
- Content performance

## 🛠 Tech Stack

- **Backend**: Django 4.2, Django REST Framework
- **Database**: PostgreSQL
- **Cache**: Redis
- **Task Queue**: Celery
- **Frontend**: Bootstrap 5, Chart.js
- **Data Science**: Pandas, NumPy, Scikit-learn, NLTK
- **ML**: TF-IDF, Cosine Similarity, Sentiment Analysis
- **Deployment**: Docker, Docker Compose

## 🐳 Docker Setup

### Quick Start
```bash
# Clone and setup
cd capstone-project
chmod +x setup.sh
./setup.sh
```

### Manual Setup
```bash
# Copy environment file
cp .env.example .env

# Build and start containers
docker-compose build
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Load sample data
docker-compose exec web python manage.py shell < load_sample_data.py
```

## 🌐 Access Points

- **Web App**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API**: http://localhost:8000/api/
- **Analytics**: http://localhost:8000/analytics/

## 👤 Default Users

- **Admin**: admin / admin123
- **Writer**: writer / writer123

## 📊 Data Science Features

### Recommendation Engine
- **Content-Based**: TF-IDF vector similarity
- **Collaborative**: User behavior patterns
- **Hybrid**: Combined approach for better accuracy

### Analytics Pipeline
- **Real-time tracking**: User interactions, reading sessions
- **Behavior analysis**: Reading patterns, engagement metrics
- **Predictive modeling**: Trending article prediction

### Sentiment Analysis
- **Comment analysis**: Positive/negative sentiment
- **Content scoring**: Article engagement prediction
- **User feedback**: Recommendation improvement

## 📈 Analytics Dashboard

### Reader Insights
- Reading time distribution
- Category preferences
- Completion rates
- Engagement patterns

### Content Performance
- Article views and engagement
- Category performance
- Writer analytics
- Trending predictions

### System Metrics
- User growth
- Content velocity
- Platform health

## 🚀 Deployment

### Production Setup
```bash
# Set production environment
export DEBUG=False
export SECRET_KEY=your-production-secret-key

# Use production database
export DB_HOST=your-db-host
export DB_PASSWORD=your-db-password

# Deploy with Docker
docker-compose -f docker-compose.prod.yml up -d
```

## 📚 API Endpoints

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/register/` - User registration

### Articles
- `GET /api/articles/` - List articles
- `GET /api/articles/{slug}/` - Article detail
- `POST /api/articles/` - Create article (writer)

### Recommendations
- `GET /api/recommendations/` - Get recommendations
- `POST /api/recommendations/feedback/` - Submit feedback

### Analytics
- `GET /api/analytics/reading-patterns/` - Reading patterns
- `GET /api/analytics/content-stats/` - Content statistics

## 🔧 Development

### Running Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py makemigrations
python manage.py migrate

# Run development server
python manage.py runserver

# Run Celery worker
celery -A insightwrite worker -l info

# Run Celery beat
celery -A insightwrite beat -l info
```

### Testing
```bash
# Run tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 📝 Project Structure

```
capstone-project/
├── accounts/          # User management
├── articles/          # Article publishing
├── analytics/         # Data collection & analysis
├── recommendations/    # ML recommendations
├── templates/         # HTML templates
├── static/           # Static files
├── media/            # User uploads
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Service orchestration
└── requirements.txt   # Python dependencies
```

## 🎯 Learning Outcomes

This project demonstrates:
- **Full-stack development**: Django + React/Bootstrap
- **Data science**: ML recommendations, sentiment analysis
- **Analytics**: Real-time tracking, behavior analysis
- **DevOps**: Docker, containerization
- **Database**: PostgreSQL, complex queries
- **API design**: RESTful APIs, authentication

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License
---

**Built with ❤️ for data science learning**
# Capstone-Project
