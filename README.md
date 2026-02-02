# CV vs LinkedIn Comparator MVP

🎯 **Goal**: Compare CVs (PDF/DOCX) with LinkedIn profiles using free AI tools and provide visual match scores.

## 🌟 Features

- ✅ **CV Parsing**: Extract text from PDF and DOCX files
- ✅ **Semantic Comparison**: Use local sentence transformers for privacy
- ✅ **Section Analysis**: Compare Experience, Skills, and Education separately
- ✅ **Skills Detection**: Automatically identify and compare technical skills
- ✅ **Visual Results**: Interactive Streamlit interface with progress bars
- ✅ **Recommendations**: Get actionable suggestions to improve consistency

## 🏗️ Architecture

```
CV_LINKEDIN_COMPARATOR/
├── backend/
│   ├── __init__.py
│   ├── requirements.txt
│   ├── cv_parser.py          # PDF/DOCX text extraction
│   ├── comparator.py          # Semantic similarity computation
│   └── main.py                # FastAPI REST API
├── frontend/
│   └── app.py                 # Streamlit UI
├── test/
│   └── test_comparator.py     # Unit tests
├── start.bat                  # Windows startup script
├── start.sh                   # Linux/Mac startup script
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip
- 4GB+ RAM (for local model)

### Installation

1. **Clone or download the project**

2. **Install backend dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

3. **Download spaCy model** (optional, for enhanced parsing):
```bash
python -m spacy download en_core_web_sm
```

### Running the Application

#### Option 1: Using startup scripts

**Windows:**
```bash
# Double-click start.bat or run:
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

#### Option 2: Manual startup

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
streamlit run app.py
```

The application will open automatically in your browser at `http://localhost:8501`

### Running Tests

```bash
cd test
python test_comparator.py
```

Or use the test scripts:
- Windows: `run_tests.bat`
- Linux/Mac: `./run_tests.sh`

## 📖 How to Use

1. **Start the application** (backend + frontend)
2. **Upload your CV** (PDF or DOCX format)
3. **Paste your LinkedIn profile text**:
   - Go to your LinkedIn profile
   - Select all text (Ctrl+A / Cmd+A)
   - Copy and paste into the text area
4. **Click "Compare"**
5. **Review results**:
   - Overall match score
   - Section-by-section breakdown
   - Skills comparison
   - Recommendations

##  API Endpoints

### `POST /compare`
Compare CV with LinkedIn profile

**Request:**
- `cv_file`: Uploaded file (multipart/form-data)
- `linkedin_text`: LinkedIn profile text (form field)

**Response:**
```json
{
  "success": true,
  "overall_score": 85.5,
  "section_scores": {
    "experience": 88.2,
    "skills": 82.5,
    "education": 86.0
  },
  "skills_comparison": {
    "common": ["Python", "JavaScript"],
    "cv_only": ["React"],
    "linkedin_only": ["Docker"],
    "match_rate": 66.7
  },
  "recommendations": [
    "✅ Excellent match! Your CV and LinkedIn profile are well aligned."
  ]
}
```

### `POST /parse-cv`
Parse CV only (testing endpoint)

### `POST /parse-linkedin`
Parse LinkedIn text only (testing endpoint)

### `GET /health`
Health check endpoint

## Technology Stack

### Backend
- **FastAPI**: Modern web framework for APIs
- **sentence-transformers**: Local semantic similarity (all-MiniLM-L6-v2)
- **pdfplumber**: PDF text extraction
- **python-docx**: DOCX text extraction
- **spaCy**: Natural language processing
- **scikit-learn**: Cosine similarity computation

### Frontend
- **Streamlit**: Interactive web UI
- **requests**: HTTP client for API calls

### Privacy
- ✅ **100% Local Processing**: All AI models run on your machine
- ✅ **No External API Calls**: No data sent to third parties
- ✅ **No Rate Limits**: Process unlimited comparisons
- 
##  Score Interpretation

| Score | Meaning | Icon |
|-------|---------|------|
| 80-100% | Excellent match - profiles are well aligned | ✅ |
| 60-79% | Good match - minor improvements suggested | ⚠️ |
| 0-59% | Needs improvement - significant differences | ❌ |

##  Section Weights

The overall score is calculated as a weighted average:
- **Experience**: 40%
- **Skills**: 35%
- **Education**: 25%

##  Configuration

### Model Selection
Edit `backend/comparator.py` to use a different model:
```python
comparator = CVLinkedInComparator(model_name='paraphrase-MiniLM-L6-v2')
```

Available models: [Sentence Transformers Hub](https://www.sbert.net/docs/pretrained_models.html)

### Section Weights
Edit weights in `backend/comparator.py`:
```python
self.section_weights = {
    'experience': 0.4,
    'skills': 0.35,
    'education': 0.25
}
```

## Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is available
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Kill the process if needed
```

### Model download issues
```bash
# Manually download the model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### PDF parsing errors
- Ensure PDF is not password-protected
- Try converting to DOCX first
- Check if PDF has selectable text (not scanned image)

##  Limitations

- **Parsing accuracy**: Works best with well-formatted CVs with clear section headers
- **Skills detection**: Limited to predefined skill keywords (expandable)
- **Language**: Optimized for English (some Spanish support)
- **File size**: Large files (>10MB) may take longer to process

##  Future Enhancements

- [ ] Multi-language support
- [ ] Custom skill dictionaries
- [ ] Export comparison reports (PDF)
- [ ] Batch processing
- [ ] Historical comparison tracking
- [ ] Integration with LinkedIn API
- [ ] Advanced NLP for better section detection

##  License

MIT License - Feel free to use and modify

##  Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

##  Support

For issues or questions, please open an issue on GitHub.

##  Acknowledgments

- [Sentence Transformers](https://www.sbert.net/) - Semantic similarity
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Streamlit](https://streamlit.io/) - UI framework
- [pdfplumber](https://github.com/jsvine/pdfplumber) - PDF parsing

---


