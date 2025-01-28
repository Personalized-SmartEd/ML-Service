# ML Service

API endpoints for ML Service.


# Docs: 
## 1. Static Assessment Model -> XGboost
    1. GET /api/assessments/static
    req : {}
    res : { Quiz }

    2. POST /api/assesments/static
    req : { Quiz Response }
    res : { Study-type , Description }
    

## 2. Adaptive Assessment Model -> LSTM( Time series data )
    1. GET /api/assessments/adaptive
    req : { subject, past-score of 10 test otherwise teacher score }
    res : { subject, Performance level otherwise average performance }



## 3. Tutor bot
    1. GET /api/tutor/search
    req : { topic-info, student-info }
    res : { study recommendation }

    1. POST /api/tutor/session
    req : { topic-info, student-info, (chat-message) }
    res : { explanation, (chat-response) }


## 4. Quiz bot
    1. GET /api/quizzes/generate
    req : { topic-info, student-info }
    res : { Quiz-questions , quiz-answers }




# Todo
## 5. Recommendation engine


## 6. Doubt solving bot
