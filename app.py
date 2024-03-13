from flask import Flask, request, jsonify,render_template ,request, redirect, url_for
import json
import random
import uuid
from openai import OpenAI
from collections import Counter
import os
import pandas as pd
from flask_cors import CORS
import time
import logging
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()
client_url = os.getenv("CLIENT_URL")

CORS(app, resources={"*": {"origins": client_url}})

logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

open_ai_key = os.getenv('APIKEY')
ass_id = os.getenv('assistant')

api= os.getenv('APIKEY')
assis = os.getenv("assistant")

@app.route("/get_question", methods=["GET"])
def get_question():
    print("OK")
    with open("data.json", "r") as json_file:
        data = json.load(json_file)

    # Shuffle the questions to get a random selection
    random.shuffle(data['questions'])

    # Select the first three questions
    random_questions = data['questions'][:5]

    # Generate a UUID
    unique_id = str(uuid.uuid1())
    logger.info("Started test From this User id : %s",unique_id)
    logger.info("All Questions : %s",random_questions)

    df = pd.DataFrame({'ID': [unique_id]})

    # Define the CSV file path
    csv_file = "started_data.csv"

    # Check if the CSV file exists
    if os.path.exists(csv_file):
        # If it exists, read the existing DataFrame from the CSV file
        existing_df = pd.read_csv(csv_file)
        # Concatenate the new DataFrame with the existing one
        updated_df = pd.concat([existing_df, df], ignore_index=True)
    else:
        # If the CSV file does not exist, use the new DataFrame
        updated_df = df

    # Save the updated DataFrame to the CSV file
    updated_df.to_csv(csv_file, index=False)


    # Save the random questions data with the UUID to a new JSON file
    filename = f"unique_data/{unique_id}.json"
    with open(filename, "w") as unique_data_file:
        json.dump({"questions": random_questions}, unique_data_file, indent=4)

    print("Returning...")
    return jsonify({"questions": random_questions, "uuid": str(unique_id)})

def compare_answers(questions_json, user_answers, user_id):

    current_time = pd.Timestamp.now()
    result = ""
    csv_file = "data.csv"
    if os.path.isfile(csv_file):
        old_df = pd.read_csv(csv_file)
    if not os.path.isfile(csv_file):
            data = {'user_id': [],
            'Question': [],
            'selected_Answer': [],
            'selected_type':[],
            'test_time':[]
            }
            old_df = pd.DataFrame(data)
    question_count = 1
    for i, question in enumerate(questions_json["questions"]):
        question_text = question["question"]
        options = question["options"]
        all_answer = ""
        Answer = ""
        Type = ""
        types = ["A" , "B","C","D"]
        types_count = 0
        for option in options:
            all_answer += f"{types[types_count]}: {option['answer']}({option['type']})\n"
            if option["type"] == user_answers[i]:
                selected_type = types[types_count]
                Answer = option["answer"]
                Type = option["type"]
            types_count += 1

        result += f"""
Spørgsmål {question_count}: {question_text}
{all_answer}
Svar: {selected_type} ({Type})

"""
        question_count += 1



        type_counts = Counter(user_answers)

# Format the output
        all_preben_types = ["Pligt-Preben", "Præstations-Preben", "Perfektionist-Preben", "Pyt-Preben"]
        output= ""
        for preben_type in all_preben_types:
            count = type_counts.get(preben_type, 0)
            output += f"{preben_type}: {count}\n"


        # Find the winner type

        winners = []
        max_count = max(type_counts.values())
        for key, value in type_counts.items():
            if value == max_count:
                winners.append(key)

        # Handle ties
        if len(winners) == 1:
            winner = winners[0]
        else:
            # Resolve ties according to the specified rules
            if ("Pyt-Preben", 2) in type_counts.items() and ("Pligt-Preben", 2) in type_counts.items() and ("Præstations-Preben", 1) in type_counts.items():
                winner = "Pyt-Preben"
            elif ("Pyt-Preben", 2) in type_counts.items() and ("Pligt-Preben", 2) in type_counts.items() and ("Perfektionist-Preben", 1) in type_counts.items():
                winner = "Pligt-Preben"
            elif ("Pyt-Preben", 2) in type_counts.items() and ("Præstations-Preben", 2) in type_counts.items() and ("Pligt-Preben", 1) in type_counts.items():
                winner = "Pyt-Preben"
            elif ("Pyt-Preben", 2) in type_counts.items() and ("Præstations-Preben", 2) in type_counts.items() and ("Perfektionist-Preben", 1) in type_counts.items():
                winner = "Præstations-Preben"
            elif ("Pyt-Preben", 2) in type_counts.items() and ("Perfektionist-Preben", 2) in type_counts.items() and ("Pligt-Preben", 1) in type_counts.items():
                winner = "Perfektionist-Preben"
            elif ("Pyt-Preben", 2) in type_counts.items() and ("Perfektionist-Preben", 2) in type_counts.items() and ("Præstations-Preben", 1) in type_counts.items():
                winner = "Pyt-Preben"
            elif ("Perfektionist-Preben", 2) in type_counts.items() and ("Præstations-Preben", 2) in type_counts.items() and ("Pyt-Preben", 1) in type_counts.items():
                winner = "Præstations-Preben"
            elif ("Perfektionist-Preben", 2) in type_counts.items() and ("Præstations-Preben", 2) in type_counts.items() and ("Pligt-Preben", 1) in type_counts.items():
                winner = "Perfektionist-Preben"
            elif ("Perfektionist-Preben", 2) in type_counts.items() and ("Pligt-Preben", 2) in type_counts.items() and ("Pyt-Preben", 1) in type_counts.items():
                winner = "Pligt-Prseben"
            elif ("Perfektionist-Preben", 2) in type_counts.items() and ("Pligt-Preben", 2) in type_counts.items() and ("Præstations-Preben", 1) in type_counts.items():
                winner = "Perfektionist-Preben"
            elif ("Pligt-Preben", 2) in type_counts.items() and ("Præstations-Preben", 2) in type_counts.items() and ("Pyt-Preben", 1) in type_counts.items():
                winner = "Præstations-Preben"
            elif ("Pligt-Preben", 2) in type_counts.items() and ("Præstations-Preben", 2) in type_counts.items() and ("Perfektionist-Preben", 1) in type_counts.items():
                winner = "Pligt-Preben"
            else:
                winner = winners[0]  # Default to the first winner in the list
        final_prompt = f"{result} \nSvar for hver PrebenType:\n{output} \nVinder PrebenType: {winner}"
                # Append data to DataFrame
        df = pd.DataFrame({'user_id': [user_id],
                                   'Question': [question_text],
                                   'selected_Answer': [Answer],
                                   'selected_type': [Type],
                                    'test_time':[current_time]

                                })

        old_df = pd.concat([old_df, df])
    print("---------------------------------------------------------------------")
    print("Final Prompt",final_prompt)
    print("---------------------------------------------------------------------")


    # Save DataFrame to CSV
    old_df.to_csv("data.csv", index=False)

    all_types = user_answers

    all_preben_types = ["Pligt-Preben", "Præstations-Preben", "Perfektionist-Preben", "Pyt-Preben"]

    preben_counts = {preben_type: all_types.count(preben_type) for preben_type in all_preben_types}

    df_preben_counts = pd.DataFrame({preben_type: [preben_counts[preben_type]] for preben_type in all_preben_types})

    df_preben_counts['user_id'] = user_id
    df_preben_counts['test_time'] = current_time

    # Check if the CSV file exists
    if os.path.exists("personality_result.csv"):
        # Load the existing DataFrame from the CSV file
        existing_df = pd.read_csv("personality_result.csv")

        # Concatenate the new data with the existing DataFrame
        df_preben_counts = pd.concat([existing_df, df_preben_counts], ignore_index=True)

    # Reorder columns
    df_preben_counts = df_preben_counts[['user_id', 'test_time'] + all_preben_types]

    # Save the concatenated DataFrame to the CSV file
    df_preben_counts.to_csv("personality_result.csv", index=False, sep=',')
    merged_df = pd.merge(old_df, df_preben_counts,on=['user_id', 'test_time'])
    merged_df.drop_duplicates(inplace=True)
    merged_df.to_csv("final_data.csv", index=False)


    return final_prompt , winner

client = OpenAI(api_key=api)
print()

assistant_id = assis


def AssistantAwaitResult(run):
    response = ""
    # Wait for OpenAI assistant response
    while run.status != 'completed':
        # Get the latest status of the run
        run = client.beta.threads.runs.retrieve(thread_id=run.thread_id, run_id=run.id)
        print("Run status: " + str(run.status))
        if run.status == 'failed':
            print("Status Failed. Error: " + str(run.last_error) + "\n")
            return "Status Failed. Error: " + str(run.last_error)
            break
        time.sleep(5)

    if run.status == 'completed':
        thread_messages = client.beta.threads.messages.list(run.thread_id)
        response = thread_messages.data[0].content[0].text.value
        print("Answer ------------------------------------",response)

    return response

def AssistantAddMessage(assistantid, threadid, input):
    print ("AssistantAddMessage\n")
    thread = client.beta.threads.retrieve(threadid)

    # Sto or cancel any runs on this thread object
    runs = client.beta.threads.runs.list(threadid, limit=1, order="desc")

    if (runs.data):
        run = runs.data[0]
        if run.status == 'requires_action' or run.status == 'in_progress':
            print ("\nCanceling pending run: " + str(run.action) + "\n")
            run = client.beta.threads.runs.cancel(
                thread_id=thread.id,
                run_id=run.id
            )
            print(run)
            print ("Run cancelled" + str(run.status) + "\n")
        else:
            print ("Run status: " + run.status + "\n")

    thread_message = client.beta.threads.messages.create(
        threadid,
        role="user",
        content=input,
        )

    print ("thread  : ")
    print(thread)
    print ("thre ad messages  : ")
    print(thread_message)

    run = client.beta.threads.runs.create(
    thread_id=threadid,
    assistant_id=assistantid
    )
    runid = run.id
    return run

def PresentUserConclusion(result):
    try:
        conclusion = ""
        assistant = client.beta.assistants.retrieve(assistant_id)
        print("assistant  : ")
        print(assistant)
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": result
                }
            ]
        )
        print("\nthread  : ")
        print(thread)

        # Add user message to OpenAI assistant chat
        run = AssistantAddMessage(assistant.id, thread.id, result)
        if (run):
            # Wait for OpenAI assistant response
            conclusion = AssistantAwaitResult(run)
        else:
            print("No run returned from AssistantSubmitFunctionResponse\n")

        return conclusion
    except Exception as e:
        print(f"error: {e}")



@app.route('/conclusion', methods=["POST"])
def conclusion():
    # global final_person
    
    global final_person
    id = request.json["id"]
    answer = request.json["answer"]

    with open(f"unique_data/{id}.json", "r") as json_file:
        json_ques = json.load(json_file)


    result , winner = compare_answers(json_ques, answer,id)
    logger.info("Result : %s ",result)
    print(result)

    # # Define the prompt template
    prompt_template = result
    response =PresentUserConclusion(prompt_template)
    logger.info("Final : %s",response)
    logger.info("Winner : %s",winner)
    return jsonify({"answer": str(response),
    "winner":winner})



@app.route("/data", methods=["GET"])
def data():
    data_df = pd.read_csv("final_data.csv")
    json_data = data_df.to_dict(orient="records")
    return jsonify(json_data)




@app.route('/login')
def idex():
    return render_template('index.html')

@app.route('/dashboard', methods=['POST'])
def dashboard():
    email = request.form.get('email')
    password = request.form.get('password')

    if email == "test@gmail.com" and password == "testing123":
        df = pd.read_csv("final_data.csv")
        unique_rows = df.drop_duplicates(subset=['user_id'])
        started_df = pd.read_csv("started_data.csv")

        # Count the unique user IDs
        unique_completed_ids = df['user_id'].nunique()
        unique_started_ids = started_df['ID'].nunique()
        pligt_counts = unique_rows['Pligt-Preben'].sum()
        praestations_counts = unique_rows['Præstations-Preben'].sum()
        perfektionist_counts = unique_rows['Perfektionist-Preben'].sum()
        pyt_counts = unique_rows['Pyt-Preben'].sum()

        # Convert int64 types to int
        unique_completed_ids = int(unique_completed_ids)
        unique_started_ids = int(unique_started_ids)
        pligt_counts = int(pligt_counts)
        praestations_counts = int(praestations_counts)
        perfektionist_counts = int(perfektionist_counts)
        pyt_counts = int(pyt_counts)

        # Prepare output dictionary
        output = {
            "completed": unique_completed_ids,
            "uncompleted": unique_started_ids,
            "pligt_counts": pligt_counts,
            "praestations_counts": praestations_counts,
            "perfektionist_counts": perfektionist_counts,
            "pyt_counts": pyt_counts
        }

        # Save output to JSON file
        with open("static/data.json", "w") as outfile:
            json.dump(output, outfile)


        with open('static/data.json', 'r') as file:
            data = json.load(file)
        return render_template('report.html', data=data)

    else:
        return redirect(url_for('index'))

@app.route("/status", methods=["GET"])
def check():
    return "server working!!!!!!!!!!!!!!!!"

@app.route("/post", methods=["POST"])
def post_check():
    return "post is working"

if __name__ == '__main__':
    app.run(port=3001)