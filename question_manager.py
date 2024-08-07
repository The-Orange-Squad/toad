import csv
import random
import uuid

class QuestionManager:
    def __init__(self):
        self.truths = []
        self.dares = []
        self.last_truths = []
        self.last_dares = []
        self.load_questions()

    def load_questions(self):
        self.load_csv('truths.csv', self.truths)
        self.load_csv('dares.csv', self.dares)

    def load_csv(self, filename, question_list):
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row['ID']:
                    row['ID'] = str(uuid.uuid4())
                question_list.append(row)
        self.save_csv(filename, question_list)

    def save_csv(self, filename, question_list):
        fieldnames = ['ID', 'question', 'maxrating']
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(question_list)

    def get_question(self, question_type, max_rating):
        questions = self.truths if question_type == 'truth' else self.dares
        last_questions = self.last_truths if question_type == 'truth' else self.last_dares

        eligible_questions = [q for q in questions if int(q['maxrating']) <= max_rating]
        for question in eligible_questions:
            if question not in last_questions:
                last_questions.append(question)
                if len(last_questions) > 5:
                    last_questions.pop(0)
                return question

        # If all questions have been used recently, reset the last questions list
        last_questions.clear()
        return random.choice(eligible_questions)

    def get_random_question(self, max_rating):
        question_type = random.choice(['truth', 'dare'])
        return self.get_question(question_type, max_rating)