import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys
from models import setup_db, Question, Category




QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)


    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/api/*": {"origins": '*'}})
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE')
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    def get_paginate_questions(request, response):
        page =  request.args.get('page', 1, type=int)
        start =  (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        formatted_questions = [question.format() for question in response]
        paginated_questions = formatted_questions[start:end]
        return paginated_questions

    
    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()
        formatted_categories = {category.id:category.type.format() for category in categories}
        return jsonify({
           'success': True,
           'categories' : formatted_categories
           })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=['GET'])
    def get_questions():
        response = Question.query.all()
        paginated_questions = get_paginate_questions(request, response)
        categories = Category.query.all()
        formatted_categories = {category.id:category.type.format() for category in categories}
        if len(paginated_questions) == 0:
            abort(404)
        else:
           pass
       return jsonify({
           'success':  True,
           'questions' : paginated_questions,
           'total_questions' : len(response),
           'categories': formatted_categories,
           'current_category': None
           })
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:delete_id>', methods=['DELETE'])
    def delete_questions(         delete_id):
        question = Question.query.filter(Question.id == delete_id).one_or_none()
        if question is None:
            abort(404)
        else:
            question.delete()
        return jsonify({
                'success': True
                })
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.


    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def post_questions():
        content = request.get_json()
        new_question =  content.get('question',None)
        new_answer =  content.get('answer',None)
        new_category = content.get('category', None)
        new_difficulty =  content.get('difficulty', None)  
        if not 'question' and 'answer' and 'category' and 'difficulty' in content:
            abort(400)
        else:
            new_intake_question = Question(
                    question = new_question,
                    answer = new_answer,
                    category = new_category,
                    difficulty = new_difficulty)
            new_intake_question.insert()
        return jsonify({
               'success': True
               })
       
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    eTEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
         content = request.get_json()
         searchTerm = content.get('searchTerm')
         if not 'searchTerm' in content:
             abort(400)
         else:
             response = Question.query.order_by(Question.id).filter(Question.question.ilike(f'%{searchTerm}%')).all()
             paginated_searched_results =  get_paginate_questions(request, response)
         return jsonify({
                 'success': True,
                 'questions': paginated_searched_results,
                 'total_questions':len(response),
                 'current_category': None
                   })
        
         


    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:id>/questions')
    def get_questions_by_category(id):
        chosen_category = Category.query.filter(Category.id == id).first()
        questions_by_category = Question.query.filter(Question.category == id).all()
        if len(questions_by_category) == 0:
            abort(404)
        else:
            returned_questions = [question.format() for question in questions_by_category]
        return jsonify({
            'success': True,
            'questions': returned_questions,
            'total_questions': len(questions_by_category),
            'current_category': chosen_category.type
            })

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def show_quizzes():
        content = request.get_json() 
        previousQuestions = content.get('previous_questions', None)
        quizCategory = content.get('quiz_category', None)
        try:
            if int(quizCategory['id']) == 0:
                all_quizzes = Question.query.filter(Question.id.not_in(previousQuestions)).all()
                all_random_quizzes = random.choice(all_quizzes)
                formatted_all_quiz = all_random_quizzes.format()
                return jsonify({
            'success': True,
            'question': formatted_all_quiz
            })
 
            else:
                new_quizzes = Question.query.filter(Question.id.not_in(previousQuestions), Question.category == quizCategory['id']).all() 
                new_random_quizzes = random.choice(new_quizzes)
                formatted_quiz = new_random_quizzes.format()
                return jsonify({
                     'success': True,
                     'question': formatted_quiz
                     })
        except:
            return jsonify({}),209
            
            
          
         


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
            }), 404
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unable to process the request, check your inputs and try again'
            }), 422
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request, verify your inputs and try again'
             }), 400
    return app
