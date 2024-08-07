import csv
import random
import uuid

class QuestionManager:
    def __init__(self):
        self.truths = []
        self.dares = []
        self.used_truths = set()
        self.used_dares = set()
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
        used_questions = self.used_truths if question_type == 'truth' else self.used_dares

        eligible_questions = [q for q in questions if int(q['maxrating']) <= max_rating]
        
        if not eligible_questions:
            return None  # No eligible questions available

        unused_questions = [q for q in eligible_questions if q['ID'] not in used_questions]

        if not unused_questions:
            # All questions have been used, reset the used questions set
            used_questions.clear()
            unused_questions = eligible_questions

        selected_question = random.choice(unused_questions)
        used_questions.add(selected_question['ID'])

        # If all questions have been used, reset the used questions set
        if len(used_questions) == len(eligible_questions):
            used_questions.clear()

        return selected_question

    def get_random_question(self, max_rating):
        question_type = random.choice(['truth', 'dare'])
        return self.get_question(question_type, max_rating)