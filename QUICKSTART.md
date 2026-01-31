# 🚀 Quick Start Guide - CV vs LinkedIn Comparator

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies

```bash
# Navigate to backend folder
cd backend

# Install all required packages
pip install -r requirements.txt
```

This will install:
- FastAPI & Uvicorn (API server)
- Streamlit (UI)
- sentence-transformers (AI model)
- PDF/DOCX parsers
- And other dependencies

**Note**: First time installation may take 5-10 minutes as it downloads the AI model (~90MB).

### Step 2: Start the Application

#### 🪟 Windows Users:
```bash
# Just double-click this file:
start.bat
```

#### 🐧 Linux/Mac Users:
```bash
# Give execute permission (first time only)
chmod +x start.sh

# Run the script
./start.sh
```

### Step 3: Access the Application

The startup script will automatically:
1. Start the backend API on `http://localhost:8000`
2. Open the frontend UI in your browser at `http://localhost:8501`

If the browser doesn't open automatically, manually visit: **http://localhost:8501**

---

## 📝 Using the Application

### 1. Prepare Your Files

**CV Requirements:**
- Format: PDF or DOCX
- Should include clear sections: Experience, Skills, Education
- Maximum size: 10MB recommended

**LinkedIn Profile:**
- Go to your LinkedIn profile
- Press `Ctrl+A` (Windows) or `Cmd+A` (Mac) to select all
- Press `Ctrl+C` / `Cmd+C` to copy
- The text should include your Experience, Skills, and Education sections

### 2. Upload and Compare

1. Click **"Browse files"** to upload your CV
2. Paste your LinkedIn profile text in the text area
3. Click **"🔍 Compare CV and LinkedIn"**
4. Wait 10-30 seconds for analysis

### 3. Review Results

You'll see:
- ✅ **Overall Match Score** (0-100%)
- 📊 **Section Scores** (Experience, Skills, Education)
- 🎯 **Skills Analysis** (Common, CV-only, LinkedIn-only)
- 💡 **Recommendations** for improving consistency

---

## 🔧 Manual Setup (Alternative)

If the startup scripts don't work, start manually:

### Terminal 1 - Backend:
```bash
cd backend
python -m uvicorn main:app --reload
```

Wait until you see: `"Application startup complete."`

### Terminal 2 - Frontend:
```bash
cd frontend
streamlit run app.py
```

The browser should open automatically at `http://localhost:8501`

---

## ✅ Verify Installation

### Check Backend API:
Visit `http://localhost:8000/health`

Should return:
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### Check Frontend:
Visit `http://localhost:8501`

You should see the CV vs LinkedIn Comparator interface.

---

## 🐛 Common Issues

### Issue 1: "Module not found" error
**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

### Issue 2: Port already in use
**Solution (Windows):**
```bash
# Find and kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F

# Find and kill process on port 8501
netstat -ano | findstr :8501
taskkill /PID <PID_NUMBER> /F
```

**Solution (Linux/Mac):**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 8501
lsof -ti:8501 | xargs kill -9
```

### Issue 3: Model download timeout
**Solution:**
```bash
# Manually download the model first
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Issue 4: PDF parsing error
**Solutions:**
- Ensure PDF is not password-protected
- Try converting to DOCX format
- Check if PDF has selectable text (not scanned image)

---

## 🧪 Test the Installation

1. **Use the sample CV** provided in `SAMPLE_CV.txt`
2. Copy the "Sample LinkedIn Profile Text" section
3. Save the CV section as a `.txt` file and paste into a Word document, save as `.docx`
4. Upload and test the comparison

Expected result: Score should be > 80% (excellent match)

---

## 📞 Need Help?

- Check the full [README.md](README.md) for detailed documentation
- Run tests: `python test/test_comparator.py`
- Check logs in the terminal windows

---

## 🎉 You're Ready!

Start comparing your CV with your LinkedIn profile to ensure consistency across platforms!

**Pro Tip**: Keep your terminal windows open to see real-time logs and debug information.
