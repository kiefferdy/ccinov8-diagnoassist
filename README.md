# DiagnoAssist

An AI-powered medical diagnosis assistant that enhances doctors' workflows and helps them diagnose patients more effectively with FHIR R4 compliance.

## Getting Started

This project consists of two main components:

- **Frontend** (`frontend/`) - React-based user interface
- **Backend** (`backend/`) - FastAPI server with FHIR R4 API

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- PostgreSQL database (we recommend [Supabase](https://supabase.com) for free cloud PostgreSQL)

### 1. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

For more details, see [Frontend README](./frontend/README.md)

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (see below)
# Create .env file with your database URL

# Run the startup script (handles database setup + server start)
python start.py
```

The backend will be available at `http://localhost:8000`

- **FHIR API**: `http://localhost:8000/fhir/R4/`
- **API Documentation**: `http://localhost:8000/docs`

### 3. Environment Configuration

Create a `.env` file in the `backend/` directory:

```bash
# Database Configuration (Supabase example)
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres

# Security
SECRET_KEY="your-secure-secret-key-here"

# FHIR Configuration
FHIR_BASE_URL=http://localhost:8000/fhir

# Optional: AI Integration
OPENAI_API_KEY=your-openai-key-here
```

**To get your Supabase DATABASE_URL:**

1. Go to [supabase.com](https://supabase.com) → Your Project
2. Settings → Database → Connection string
3. Copy the PostgreSQL URL

**To generate a SECRET_KEY:**

```bash
python -c "import secrets; print('SECRET_KEY=\"' + secrets.token_urlsafe(32) + '\"')"
```

### 4. What `start.py` Does Automatically

The startup script handles everything for you:

- ✅ **Validates environment variables**
- ✅ **Tests database connection**
- ✅ **Creates database tables** (if they don't exist)
- ✅ **Runs migrations** (Alembic or direct table creation)
- ✅ **Starts FHIR-compliant FastAPI server**

No manual database setup required! 🎉

---

## 🏥 Features

### Current Implementation

- **FHIR R4 Compliant API** - Full healthcare interoperability standard
- **Patient Information Management** - Comprehensive demographic data with FHIR Patient resources
- **Clinical Encounters** - FHIR Encounter resources for episodes of care
- **Vital Signs & Observations** - FHIR Observation resources with LOINC coding
- **AI Diagnostic Reports** - FHIR DiagnosticReport resources for AI-generated diagnoses
- **Medical Conditions** - FHIR Condition resources with SNOMED CT coding

### Frontend Features

- **Dynamic Clinical Assessment** - AI-powered adaptive questioning based on chief complaint
- **Physical Examination Interface** - Vital signs recording and physical measurements
- **AI Diagnostic Analysis** - Differential diagnosis generation with probability scoring
- **Laboratory Tests & Results** - Test ordering, result entry, and interpretation
- **Treatment Planning** - AI-generated treatment recommendations

---

## 🔌 API Endpoints

### FHIR R4 Endpoints

- `GET /fhir/R4/metadata` - Server capability statement
- `GET/POST /fhir/R4/Patient` - Patient resources
- `GET/POST /fhir/R4/Encounter` - Encounter resources
- `GET/POST /fhir/R4/Observation` - Observation resources
- `GET/POST /fhir/R4/DiagnosticReport` - Diagnostic report resources
- `GET/POST /fhir/R4/Condition` - Condition resources
- `POST /fhir/R4/Bundle` - Bundle transactions and batches

### Internal API Endpoints

- `POST /api/patients` - Create new patient
- `POST /api/clinical-assessment/questions` - Get dynamic questions
- `POST /api/diagnosis/analyze` - Generate differential diagnoses
- `POST /api/diagnosis/refine` - Refine diagnosis with test results
- `POST /api/treatment/plan` - Generate treatment recommendations

---

## 🏗️ Architecture

### Backend Stack

- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM with PostgreSQL
- **FHIR.resources** - FHIR R4 resource validation
- **Alembic** - Database migrations
- **Pydantic** - Data validation and serialization

### Frontend Stack

- **React** - UI framework
- **Tailwind CSS** - Styling
- **React Router** - Navigation
- **React Hook Form** - Form management
- **Lucide React** - Icons

### Database Schema

- **FHIR Resources Table** - Stores all FHIR resources as JSON
- **Patient Management** - Internal patient data with FHIR mapping
- **Clinical Episodes** - Encounter tracking and management
- **AI Diagnosis History** - Diagnostic analysis results

---

## 🧪 Testing the Setup

After running `python start.py`, test your FHIR server:

```bash
# Test server health
curl http://localhost:8000/health

# Get FHIR capability statement
curl http://localhost:8000/fhir/R4/metadata

# Create a test patient
curl -X POST http://localhost:8000/fhir/R4/Patient \
  -H "Content-Type: application/json" \
  -d '{
    "resourceType": "Patient",
    "name": [{"family": "Doe", "given": ["John"]}],
    "gender": "male",
    "birthDate": "1985-03-15"
  }'

# Search patients
curl http://localhost:8000/fhir/R4/Patient
```

---

## 🐳 Alternative: Docker Setup

If you prefer Docker, create `docker-compose.yml`:

```yaml
version: "3.8"
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: diagnoassist
      POSTGRES_USER: diagnoassist_user
      POSTGRES_PASSWORD: diagnoassist_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Then update your `.env`:

```bash
DATABASE_URL=postgresql://diagnoassist_user:diagnoassist_pass@localhost:5432/diagnoassist
```

And run:

```bash
python start.py  # This will start Docker PostgreSQL automatically
```

---

## 🔄 Development Workflow

1. **Make changes** to your code
2. **Server auto-reloads** (thanks to `--reload` flag)
3. **Database changes** are handled by Alembic migrations
4. **Test FHIR endpoints** at `http://localhost:8000/docs`

---

## 📝 TODO

- [ ] Advanced AI model integration for diagnosis
- [ ] PDF export functionality
- [ ] EHR system integration
- [ ] Patient portal interface
- [ ] Real-time clinical decision support
- [ ] Medical imaging integration
- [ ] Clinical workflow automation
- [ ] Multi-language support
- [ ] Mobile app development
- [ ] Telehealth integration

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Troubleshooting

### Common Issues

**Database Connection Error:**

- Check your `DATABASE_URL` in `.env`
- Ensure your Supabase database is running
- Verify your credentials

**Import Errors:**

- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

**Server Won't Start:**

- Check if port 8000 is already in use
- Look at the error logs in terminal
- Ensure all environment variables are set

**FHIR Validation Errors:**

- Check the request format against FHIR R4 specification
- Use the interactive docs at `/docs` for testing

### Getting Help

- Check the [FastAPI documentation](https://fastapi.tiangolo.com/)
- Review [FHIR R4 specification](https://hl7.org/fhir/R4/)
- Open an issue on GitHub for bugs or questions

---

_DiagnoAssist - Empowering healthcare with AI and FHIR standards_ 🏥✨
