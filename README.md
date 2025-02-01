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

```
HERE:
    1. Study_type is a enum : {'visual' , 'auditory', 'reading_writing', 'kinesthetic'}
```
</br>

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
</br>

## 3. Quiz bot
    1. GET /api/quiz/
    req : { student_info, subject_info, quiz_info }
    res : { question_numbers, quiz_questions with answers }
```
HERE: 
    1. student_learning_style is a enum == study_type enum defined above.
    2. student_performance_level is a enum == performance_level enum defined above
    3. subject is a enum also defined above.
```


# Remaining
## 4. Tutor bot
    1. GET /api/tutor/search
    req : { topic-info, student-info }
    res : { study recommendation }

    1. POST /api/tutor/session
    req : { topic-info, student-info, (chat-message) }
    res : { explanation, (chat-response) }

## 5. Recommendation engine


## 6. Doubt solving bot
