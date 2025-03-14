import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from secret import *


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(DB_USER, DB_PASSWORD, DB_HOST, DB_TEST_NAME)
        setup_db(self.app, self.database_path)

        self.new_question = {
                "question": "what is my name",
                "answer" : "Adekilekun",
                "category": 5,
                "difficulty": 2
                }
        self.new_quizzes = {
                "previous_questions" : [1,4],
                "quiz_category": {"id": "1", "type":"Science"}
                }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass
    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        abu = self.client().get('/categories')
        data = json.loads(abu.data)

        self.assertEqual(abu.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
    
    def test_get_question(self):
        abu = self.client().get('/questions?page=2')
        data = json.loads(abu.data)

        self.assertEqual(abu.status_code, 200)
        self.assertEqual(data['success'], True)
    def test_get_questions_not_found(self):
        abu = self.client().get('/questions?page=200')

        self.assertEqual(abu.status_code, 404)
    def test_get_questions_by_categories(self):
        abu = self.client().get('/categories/3/questions')
        data = json.loads(abu.data)
        
        self.assertEqual(abu.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertEqual(data['success'], True)
    def test_questions_by_categories_not_found(self):
        abu = self.client().get('/categories/56/questions')
        data = json.loads(abu.data)

        self.assertEqual(abu.status_code, 404)
        self.assertEqual(data['success'], False)
    def test_delete_question(self):
        abu = self.client().delete('/questions/6')
        
        self.assertEqual(abu.status_code, 200)
    def test_delete_question_not_found(self):
        abu = self.client().delete('/questions/1000')
        data = json.loads(abu.data)

        self.assertEqual(abu.status_code, 404)
        self.assertEqual(data['success'], False)
    def test_post_quizzes_pass(self):
        abu = self.client().post('/quizzes', json=self.new_quizzes)
        data = json.loads(abu.data)

        self.assertEqual(abu.status_code, 200)
    def test_post_quizzes_failed(self):
        abu = self.client().post('/quizzes/6', json=self.new_quizzes)
        data = json.loads(abu.data)

        self.assertEqual(abu.status_code, 404)
        self.assertEqual(data['success'], False)
    def test_post_questions(self):
        abu = self.client().post('/questions', json=self.new_question)
        data = json.loads(abu.data)

        self.assertEqual(abu.status_code, 200)
        self.assertEqual(data['success'], True)
    def test_post_questions_failed(self):
        abu = self.client().post('/questions/5', json={'answer': 'abdullahi'})
        
        self.assertEqual(abu.status_code, 405)
    def test_search_questions_pass(self):
        abu = self.client().post('/questions/search', json={'searchTerm' : 'Author'})
        data = json.loads(abu.data)

        self.assertEqual(abu.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['success'], True)
    def test_searched_questions_failed(self):
        abu = self.client().post('/questions/search', json={"answer": "Abdullahi"})
        
        self.assertEqual(abu.status_code, 400)
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
