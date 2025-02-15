
---

# ML Service Documentation

This document details the architecture, API endpoints, and underlying machine learning models powering our educational platform. Our service comprises multiple specialized agents designed to deliver personalized assessments, tutoring, doubt resolution, and study recommendations.

---

## Table of Contents

1. [Static Assessment Model (Logistic Regression)](#1-static-assessment-model-logistic-regression)
2. [Adaptive Assessment Model (XGBoost)](#2-adaptive-assessment-model-xgboost)
3. [Quiz Bot (RAG-based Agent)](#3-quiz-bot-rag-based-agent)
4. [Tutor Bot (RAG-based Agent)](#4-tutor-bot-rag-based-agent)
5. [Doubt Solving Bot (Multimodal AI Agent)](#5-doubt-solving-bot-multimodal-ai-agent)
6. [Recommendation Engine](#6-recommendation-engine)
7. [Knowledge Base Creation: Embeddings and Vector Database](#7-knowledge-base-creation-embeddings-and-vector-database)
8. [Project Substructure](#8-project-substructure)

---

## 1. Static Assessment Model (Logistic Regression)

**Model Overview:**  
- **Algorithm:** Logistic Regression  
- **Purpose:** To classify a student’s study type using their responses from a fixed quiz.  
- **Technical Details:**  
  - **Data Input:** A 15-question quiz where each response is an integer between 0 and 3.  
  - **Model Structure:**  
    - Uses a linear combination of the input features (quiz responses) with a logistic function to predict probability distributions over study-type classes.  
    - For multi-class classification, a one-vs-rest or softmax approach is employed.  
  - **Training:**  
    - Trained on historical quiz data labeled with study types.  
    - Feature scaling and regularization (L1 or L2) are applied to avoid overfitting and ensure model generalization.  
  - **Optimization:**  
    - Hyperparameters such as the regularization strength are tuned via grid search with cross-validation.

**API Endpoints:**  
- **GET /api/assessments/static**  
  - **Request:** None  
  - **Response:** A 15-question quiz intended to assess the student’s study type.

- **POST /api/assessments/static**  
  - **Request:**  
    ```json
    {
      "responses": [0, 1, 2, ..., 3]
    }
    ```  
  - **Response:**  
    ```json
    {
      "study_type": "Determined study type",
      "description": "Detailed explanation of the study type"
    }
    ```

---

## 2. Adaptive Assessment Model (XGBoost)

**Model Overview:**  
- **Algorithm:** XGBoost (Extreme Gradient Boosting)  
- **Purpose:** To evaluate and predict student performance trends using historical test data.  
- **Technical Details:**  
  - **Data Input:**  
    - Subject identifier (from a defined enum).  
    - A series of past test scores (or teacher-provided scores).  
  - **Feature Engineering:**  
    - Transforms the time-series data into engineered features (e.g., recent score average, score variance, and trend indicators).  
  - **Model Structure:**  
    - XGBoost is used in a regression or classification setup to predict multiple outputs such as performance level (beginner, intermediate, advanced), average score (float), and performance trend (stable, improving, declining).  
  - **Training:**  
    - The model is trained using gradient boosting on engineered features from historical data.  
    - Hyperparameters are tuned using cross-validation to achieve robust performance across different student profiles.

**API Endpoint:**  
- **GET /api/assessments/dynamic**  
  - **Request:**  
    ```json
    {
      "subject": "math", // one of ['math', 'science', 'english', 'social-science', 'hindi']
      "past_scores": [/* Array of 10 scores or teacher provided score */]
    }
    ```  
  - **Response:**  
    ```json
    {
      "subject": "math",
      "performance_level": "intermediate", // one of ['beginner', 'intermediate', 'advanced']
      "average_score": 78.5,
      "trend": "improving" // one of ['stable', 'improving', 'declining']
    }
    ```

---

## 3. Quiz Bot (RAG-based Agent)

**Model Overview:**  
- **Architecture:** Retrieval Augmented Generation (RAG)  
- **Purpose:** To dynamically generate quizzes tailored to the student’s learning style and performance.  
- **Technical Details:**  
  - **Retrieval Component:**  
    - Uses a vector database populated with educational content (including embeddings from NCERT books) to retrieve contextually relevant information.  
  - **Generative Component:**  
    - A transformer-based model synthesizes the retrieved context with student profile data to generate quiz questions and answer options.  
  - **Integration:**  
    - Combines inputs from static assessments (Logistic Regression) and adaptive assessments (XGBoost) along with real-time retrieval for a personalized quiz experience.

**API Endpoint:**  
- **GET /api/quiz/**  
  - **Request:**  
    ```json
    {
      "student_info": {
        "student_learning_style": "visual"
      },
      "subject_info": {
        "subject": "science"
      },
      "quiz_info": {
        // Additional configuration parameters
      }
    }
    ```  
  - **Response:**  
    ```json
    {
      "question_numbers": [1, 2, 3, ...],
      "quiz_questions": [
        {
          "question": "What is the boiling point of water?",
          "options": ["90°C", "100°C", "110°C", "120°C"]
        }
      ]
    }
    ```

---

## 4. Tutor Bot (RAG-based Agent)

**Model Overview:**  
- **Architecture:** Retrieval Augmented Generation (RAG)  
- **Purpose:** To deliver personalized tutoring sessions with context-aware explanations.  
- **Technical Details:**  
  - **Retrieval:**  
    - Searches a dedicated vector database for relevant educational content.  
  - **Generative Component:**  
    - Uses a transformer-based model to generate detailed explanations based on both retrieved information and student context.  
  - **Session Management:**  
    - Maintains complete conversation history to provide continuity and personalized guidance.

**API Endpoint:**  
- **POST /api/tutor/session**  
  - **Request:**  
    ```json
    {
      "topic_info": "Concept: Newton's Laws",
      "student_info": {
        "name": "John Doe"
      },
      "complete_chat": [
        // Array of previous chat messages
      ]
    }
    ```  
  - **Response:**  
    ```json
    {
      "explanation": "Newton's First Law states that...",
      "updated_complete_chat": [
        // Updated conversation history
      ]
    }
    ```

---

## 5. Doubt Solving Bot (Multimodal AI Agent)

**Model Overview:**  
- **Architecture:** Multimodal AI Agent  
- **Purpose:** To resolve student doubts by integrating both text and image inputs.  
- **Technical Details:**  
  - **Text Processing:**  
    - Utilizes NLP to understand and process the textual content of the doubt.  
  - **Image Analysis:**  
    - Employs computer vision techniques to extract information from attached images (e.g., diagrams, handwritten notes).  
  - **Fusion:**  
    - Combines insights from both modalities to generate a comprehensive explanation and relevant follow-up questions.  
  - **Output:**  
    - Provides detailed textual explanations and, if applicable, processed visual content.

**API Endpoint:**  
- **POST /api/doubt/ask**  
  - **Request:**  
    ```json
    {
      "student_info": {
        "id": "student123"
      },
      "doubt": {
        "text": "How does photosynthesis work?",
        "image": "base64encodedstring", // Optional
        "image_description": "Diagram of a plant cell" // Optional
      },
      "subject": "science"
    }
    ```  
  - **Response:**  
    ```json
    {
      "explanation": "Photosynthesis is the process by which plants...",
      "image": "optional_processed_image", // If applicable
      "follow_up_questions": ["Can you explain the role of chlorophyll?"]
    }
    ```

---

## 6. Recommendation Engine

**Model Overview:**  
- **Architecture:** An advanced reinforcement-learning and chain-of-thought based LLM to offer extremely personalized recommendations.  
- **Purpose:** To generate personalized study routines and recommend learning resources based on aggregated student data.  
- **Technical Details:**  
  - **Data Aggregation:**  
    - Combines profile data from static assessments (Logistic Regression), dynamic assessments (XGBoost), and other interactions.  
  - **Algorithm:**  
    - Uses content-based filtering and rule-based logic to match student needs with appropriate study routines and resources.

**API Endpoint:**  
- **POST /api/reccomedn/generate-routine**  
  - **Request:**  
    ```json
    {
      "student_profile": {
        "study_type": "kinesthetic",
        "performance_level": "advanced"
      }
    }
    ```  
  - **Response:**  
    ```json
    {
      "routine": "Monday: Algebra practice, Tuesday: Physics problems, ...",
      "resources": [
        "Resource link 1",
        "Resource link 2"
      ]
    }
    ```

---

## 7. Knowledge Base Creation: Embeddings and Vector Database

**Data Source:**  
- **Content:** Textbooks for Grades 6–8 across subjects such as Math, Science, English, Social Science, and Hindi, sourced directly from the official NCERT portal.

**Embeddings Creation:**  
- **Preprocessing:**  
  - **Text Cleaning:** Standardization, noise removal, and tokenization of text data.  
  - **Segmentation:** Dividing text into meaningful passages or paragraphs for enhanced retrieval precision.
- **Embedding Generation:**  
  - **Model:** Utilizes a pre-trained language model (e.g., Sentence-BERT) fine-tuned on educational material to generate dense vector representations.  
  - **Optimization:** Embeddings are optimized to capture domain-specific nuances in the educational content.
- **Vector Database:**  
  - **Storage:**  
    - Embeddings are indexed using a vector database system (such as FAISS or Pinecone) to facilitate fast similarity searches.  
  - **Integration:**  
    - This vector database underpins the retrieval component of our RAG-based Quiz and Tutor Bots, ensuring access to the most contextually relevant content.
- **Maintenance:**  
  - **Updates:**  
    - Regular updates align the database with the latest curriculum revisions from the NCERT portal.
  - **Scalability:**  
    - The infrastructure is designed to support a growing corpus and handle increased query loads efficiently.

---

## 8. Project Substructure

Below is the folder structure of the **Personalized-SmartEd/ML-Service** repository:

```
ML-Service/
├── Notebooks/               # Jupyter notebooks for exploratory data analysis, model training, and experimentation
├── docs/                    # Detailed API endpoint specifications and technical documentation
├── src/                     # Core source code for the ML service including model implementations and API integrations
├── tmp/data/                # Temporary directory for raw and processed data used during development
├── .gitignore               # Specifies files and directories excluded from version control
├── App.py                   # Main application entry point for the ML service API
├── README.md                # Project documentation
└── requirements.txt         # Python package dependencies
```

---
