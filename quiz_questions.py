import os


def load_questions_from_file(file_path):
    with open(file_path, "r", encoding="koi8-r") as file:
        content = file.read()

    blocks = content.split("\n\n")
    questions_answers = {}
    question = None

    for block in blocks:
        if block.startswith("Вопрос"):
            question = block.split(":\n", 1)[1].strip()

        elif block.startswith("Ответ") and question:
            answer = block.split(":\n", 1)[1].strip()
            questions_answers[question] = answer

    return questions_answers


def load_questions_from_directory(directory_path):
    all_questions_answers = {}

    for filename in os.listdir(directory_path):
        if not filename.endswith(".txt"):
            continue

        file_path = os.path.join(directory_path, filename)

        file_questions = load_questions_from_file(file_path)
        all_questions_answers.update(file_questions)

    return all_questions_answers


def clean_answer(answer):
    answer = answer.split(".")[0]
    answer = answer.split("(")[0]
    return answer.strip().lower()
