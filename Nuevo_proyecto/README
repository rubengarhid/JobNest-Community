# XGBoost Job Classification Model 

This project implements an end-to-end machine learning pipeline for classifying professional roles based on structured and enriched textual features such as keywords, skills, KPIs, and tools.

The core of the system is an **XGBoost classifier**, selected for its strong performance on tabular data, ability to model non-linear relationships, and built-in regularization mechanisms that help prevent overfitting.

---

##  Objective

- Develop a robust classification model capable of learning meaningful patterns from job-related metadata.  
- Improve model generalization by expanding and enriching the original dataset while preserving its structure and class distribution.  
- Build a reproducible ML workflow that can be extended to larger datasets or similar tasks.

---

## 📊 Dataset Strategy

- Started from a clean, structured dataset with consistent role-based categories.  
- Synthetically expanded the dataset to:
  - Increase lexical diversity  
  - Reduce data sparsity  
  - Improve training robustness  
- Maintained the original class distribution to avoid introducing bias.

The final dataset includes features such as:
- **Role**
- **Keywords**
- **Skills**
- **KPIs**
- **Tools**
- **Category (target variable)**

---

##  Model: XGBoost Classifier

I used **XGBoost** because it provides:

- Excellent performance on structured/tabular data  
- Strong handling of complex feature interactions  
- Regularization to reduce overfitting  
- Interpretability via feature importance  

---

## 🔧 Feature Engineering

Key preprocessing steps included:

- Transforming text-based fields (*Keywords, Skills, Tools*) into numerical representations suitable for tree-based models.  
- Encoding categorical variables properly.  
- Ensuring consistent scaling and formatting of input features.

---

##  Training & Optimization

The model was trained and fine-tuned using:

- Hyperparameter tuning on:
  - Learning rate  
  - Maximum tree depth  
  - Number of estimators  
  - Regularization parameters  

- Cross-validation to ensure stability and avoid overfitting.  

---

## Evaluation

Model performance was assessed using:

- Accuracy  
- Precision  
- Recall  
- F1-score  

Additionally, My teenmates analyzed **feature importance** to understand which skills, tools, and keywords most influenced predictions.
They are professionals with more than 8 years of experience.

---

##  Results

This project delivers:

- A complete ML pipeline: data → preprocessing → training → evaluation  
- A high-performing and interpretable classifier  
- A framework that can be easily extended to:
  - Recommendation systems  
  - Semantic search  
  - Role matching  
  - HR analytics  

---

## Tech Stack

- Python  
- XGBoost  
- Pandas  
- Scikit-learn  
- Jupyter Notebook  

---

## Files in this repository

- `XGBoost_classification.ipynb` → Main notebook with full ML pipeline  
- `keywords_clean.csv` → Original dataset  
- `keywords_expanded_for_ml.csv` → Expanded training dataset  

---

## 📬 Contact

If you’re interested in this project or want to collaborate, feel free to reach out or open an issue!  
