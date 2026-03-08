with open('quiz-questions/1vs1200.txt', encoding='koi8-r') as file:
    content = file.read()

blocks = content.split('\n\n')

questions_answers = {}

question = None

for block in blocks:

    if block.startswith('Вопрос'):
        question = block.split(':\n', 1)[1].strip()

    if block.startswith('Ответ'):
        answer = block.split(':\n', 1)[1].strip()
        questions_answers[question] = answer

print(questions_answers)