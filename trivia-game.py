import requests
import psycopg2
import os
import html  
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_HOST = os.getenv('HOSTNAME')
DB_NAME = os.getenv('DATABASE')
DB_USER = os.getenv('NAME')
DB_PASSWORD = os.getenv('PASSWORD')
DB_PORT = os.getenv('PORT')

# Establish database connection
connection = psycopg2.connect(
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

cursor = connection.cursor()

# Create table if it does not exist
cursor.execute('DROP TABLE IF EXISTS trivia')

cursor.execute('''
    CREATE TABLE trivia (
        id SERIAL PRIMARY KEY, 
        question TEXT UNIQUE, 
        correct_answer TEXT
    )
''')

connection.commit()

# Fetch trivia questions from API
trivia_api = requests.get('https://opentdb.com/api.php?amount=20&type=multiple')
data = trivia_api.json()

# Insert data into database with cleaned text
for i, item in enumerate(data["results"], start=1):  
    question = html.unescape(item["question"]) 
    correct_answer = html.unescape(item["correct_answer"])  
    
    question = question.replace("'", "''")  
    correct_answer = correct_answer.replace("'", "''")  

    try:
        cursor.execute(
            "INSERT INTO trivia (id, question, correct_answer) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
            (i, question, correct_answer) 
        )
        connection.commit()
    except Exception as e:
        print(f"Error inserting question {i}: {e}")

print("All questions processed with cleaned text!")

def trivia_game():
    print("\nWelcome to the Ultimate Trivia Game!")
    print("You have 10 questions to answer, and you get 3 attempts per question.")
    print("Type 'exit' anytime to quit the game.\n")

    score = 0
    attempts_per_question = 3
    total_questions = 10  # Max questions per game
    used_questions = set()  # Keeps track of questions used

    while len(used_questions) < total_questions:
        try:
            question_number = input("Choose a question number between 1 and 20: ")
            
            if question_number.lower() == "exit":
                print("\nGame exited. Your final score:", score)
                connection.close()
                return

            question_number = int(question_number)

            # Check if question was already used
            if question_number in used_questions:
                print("You've already chosen this question! Pick another one.")
                continue

            cursor.execute("SELECT question, correct_answer FROM trivia WHERE id = %s", (question_number,))
            result = cursor.fetchone()
            
            if not result:
                print("Invalid question number, please try again.")
                continue

            question, correct_answer = result
            used_questions.add(question_number)  # Mark question as used

            print(f"\nYour question: {question}")

            attempts = 0
            while attempts < attempts_per_question:
                user_answer = input("Your answer: ").strip()

                if user_answer.lower() == "exit":
                    print("\nGame exited. Your final score:", score)
                    connection.close()
                    return

                if user_answer.lower() == correct_answer.lower():
                    print("Correct! Well done!\n")
                    score += 1
                    break
                else:
                    attempts += 1
                    if attempts < attempts_per_question:
                        print(f"Incorrect! Try again ({attempts_per_question - attempts} attempts left).")
                    else:
                        print(f"Out of attempts! The correct answer was: {correct_answer}\n")

        except ValueError:
            print("Please enter a valid number.")

    print(f"\nGame Over! Your final score is: {score}/{total_questions}")
    connection.close()


# Start the game
trivia_game()
