# ML Service

API endpoints for ML Service.

* For specific request/response model details look at the ```/docs``` . Here the functionality of each endpoint is discussed.

# Docs: 
## 1. Static Assessment Model -> XGboost
    1. GET /api/assessments/static
    req : {}
    res : { Gives a quiz of 15 questions for assessing the study-type of student }

    2. POST /api/assesments/static
    req : { Expects a integer-list of 15 responses with answer options between 0-3 }
    res : { Study-type , Description }


    

## 2. Adaptive Assessment Model -> LSTM( Time series data )
    1. GET /api/assessments/dynamic
    req : { subject, past-score of 10 test otherwise teacher score }
    res : { subject, performance level, average score, trend }

```
HERE: 
    1. Subject is a enum : {'math', 'science', 'english', 'social-science', 'hindi'}
    2. Performance_level is a enum : {'beginner', 'intermediate', 'advanced'}
    3. Average score is a float showing model predicted value.
    4. Trend is a enum : {'stable', 'improving', 'declining'}
```

## 4. Quiz bot
    1. GET /api/quiz/
    req : { topic-info, student-info }
    res : { Quiz-questions , quiz-answers }


## 3. Tutor bot
    1. GET /api/tutor/search
    req : { topic-info, student-info }
    res : { study recommendation }

    1. POST /api/tutor/session
    req : { topic-info, student-info, (chat-message) }
    res : { explanation, (chat-response) }






# Todo
## 5. Recommendation engine


## 6. Doubt solving bot
