from openai import OpenAI
from flask import Flask, request, jsonify, render_template

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

model = "qwen2-7b-instruct-q6_k/Repository"

app = Flask(__name__)

# History
history_answer = [
    {"role": "system",
     "content": "你是一个智能助手。你总是提供合理的且符合逻辑的答案。"},
    {"role": "user",
     "content": ""},
]

history_extract = [
    {"role": "system",
     "content": "你是一个智能助手。你需要列举出以下文本中的要点，同时保持要点间的逻辑顺序。"},
    {"role": "user",
     "content": ""},
]

history_adjustment = [
    {"role": "system",
     "content": "你是一个智能助手。我会给你提供一个文本，这个文本中可能会出现重复的信息。当重复的信息出现时，你只需要保留最开始出现的那一个。当你删除完给定文本中冗余的信息时，你需要按序号列举出剩余信息。记住，你要保持信息间的相对顺序。"},
    {"role": "user",
     "content": ""},
]

history_question = [
    {"role": "system",
     "content": "你是一名老师。你总是通过提出合适的问题引导学生思考。每次我都会给你提供一个文本，你需要基于这个文本设计一个问题。注意，你要确保这个文本是你所设计的问题的答案。"},
    {"role": "user",
     "content": ""},
]

history_confusion = [
    {"role": "system",
     "content": "你是一个智能助手。你需要判断用户是否是困惑的。如果用户输入类似'我不知道'的信息,这个用户很有可能是困惑的。如果这个用户是困惑的，你只需要输出'是的'。"},
    {"role": "user",
     "content": ""},
]

history_feedback = [
    {"role": "system",
     "content": "你是一名老师。你需要判断学生回答正确性。"},
    {"role": "user",
     "content": ""},
]

history_feedback_extract = [
    {"role": "system",
     "content": "你是一个智能助手。你需要列举出以下有关于正确答案的要点。"},
    {"role": "user",
     "content": ""},
]

history_selection = [
    {"role": "system",
     "content": "你是一个智能助手。我会给你提供一个文本、前一个问题和四个备选问题，你需要从四个备选问题中选择出与提供的文本最匹配且与前一个问题承接最连贯的那一个。 \
                 其中，与提供的文本最匹配是指你所选择的备选问题的答案与提供的文本最相似，也就是说，提供的文本是你所挑选出的备选问题的答案；而与前一个问题承接最连贯是指你所挑选出的备选问题与前一个问题在内容上承接最连贯，转折最不突兀。"},
    {"role": "user",
     "content": ""},
]



# Web
flag = 0 # 0: begin; 1: on
main_points = []
socratic_question = ""

@app.route('/')
def index():
    return render_template('index1.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message']
    global flag, main_points, socratic_question

    if flag == 0:
        flag = 1
        standard_answer = ""
        history_answer[1]["content"] = "请一步步回答：" + user_input
        completion_answer = client.chat.completions.create(
            model=model,
            messages=history_answer,
            temperature=0,
            stream=True,
        )
        for chunk in completion_answer:
            if chunk.choices[0].delta.content:
                if chunk.choices[0].delta.content in ['<|endoftext|>', '---\n\n']:
                    break
                print(chunk.choices[0].delta.content, end="", flush=True)
                standard_answer += chunk.choices[0].delta.content
        print("\n---------------------------\n")
        print(f'standard_answer:{standard_answer}')
        print("\n---------------------------\n")
        sub_points = []
        history_extract[1]["content"] = "请列举出以下文本中的要点且保持要点间的逻辑顺序：" + standard_answer
        completion_extract = client.chat.completions.create(
            model=model,
            messages=history_extract,
            temperature=0,
            stream=True,
        )
        point_count = 1
        flag_point = 0
        sub_point = ""
        for chunk in completion_extract:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
                sub_point += chunk.choices[0].delta.content
                if chunk.choices[0].delta.content in ['.', '. ']:
                    if flag_point != 1:
                        continue
                    sub_points.append(sub_point)
                    point_count += 1
                    sub_point = ""
                if chunk.choices[0].delta.content in [f'{point_count}']:
                    flag_point = 1
                else:
                    flag_point = 0
        sub_points.append(sub_point)
        sub_points = sub_points[1:]
        main_points = sub_points + main_points
        print("\n---------------------------\n")
        print(main_points)
        print("\n---------------------------\n")
        socratic_question = ""
        point = main_points.pop(0)
        history_question[1]["content"] = "请设计一个问题并确保以下文本是你所设计的问题的答案。" + point + "请直接输出你所设计的问题（不包括答案），问题："
        completion_question = client.chat.completions.create(
            model=model,
            messages=history_question,
            temperature=0,
            stream=True,
        )
        # print()
        for chunk in completion_question:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
                socratic_question += chunk.choices[0].delta.content
                if chunk.choices[0].delta.content in ['<|endoftext|>', '---\n', '？\n']:
                    break
                if chunk.choices[0].delta.content in ['：']:
                    socratic_question = ""
        print("\n---------------------------\n")
        print("\n---------------------------\n")
        print("\n---------------------------\n")
        return jsonify({"server": socratic_question})

    if flag == 1:
        history_confusion[1]["content"] = "请判断用户是否是困惑的。如果这名用户是困惑的，你只需要输出'是的'，否则请输出'不是'。" + "用户输入： " + user_input
        completion_confusion = client.chat.completions.create(
            model=model,
            messages=history_confusion,
            temperature=0,
            stream=True,
        )
        confusion = ""
        # print("confusion")
        for chunk in completion_confusion:
            if chunk.choices[0].delta.content:
                if chunk.choices[0].delta.content in ['\n\n\n', '\n\n', '\n']:
                    break
                print(chunk.choices[0].delta.content, end="", flush=True)
                confusion += chunk.choices[0].delta.content
        print("\n---------------------------\n")
        print(f'confusion: {confusion}')
        print("\n---------------------------\n")
        if confusion == "是的":
            standard_answer = ""
            history_answer[1]["content"] = "请一步步回答：" + socratic_question
            completion_answer = client.chat.completions.create(
                model=model,
                messages=history_answer,
                temperature=0,
                stream=True,
            )
            for chunk in completion_answer:
                if chunk.choices[0].delta.content:
                    if chunk.choices[0].delta.content in ['<|endoftext|>', '---\n\n']:
                        break
                    print(chunk.choices[0].delta.content, end="", flush=True)
                    standard_answer += chunk.choices[0].delta.content
            unfinished_answer = ''.join(main_points)
            standard_answer = standard_answer + "\n2." + unfinished_answer
            print("\n---------------------------\n")
            print(standard_answer)
            print("\n---------------------------\n")
            main_points = []
            history_adjustment[1]["content"] = "以下文本中可能会出现重复信息。当重复的信息出现时，请你保留最开始出现的那一个。当你删除完给定文本中冗余的信息时，请你按序号列举出剩余信息。记住，你要保持信息间的相对顺序。" + standard_answer
            completion_adjustment = client.chat.completions.create(
                model=model,
                messages=history_adjustment,
                temperature=0,
                stream=True,
            )
            point_count = 1
            flag_point = 0
            main_point = ""
            for chunk in completion_adjustment:
                if chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="", flush=True)
                    main_point += chunk.choices[0].delta.content
                    if chunk.choices[0].delta.content in ['.', '. ']:
                        if flag_point != 1:
                            continue
                        main_points.append(main_point)
                        point_count += 1
                        main_point = ""
                    if chunk.choices[0].delta.content in [f'{point_count}']:
                        flag_point = 1
                    else:
                        flag_point = 0
            main_points.append(main_point)
            main_points = main_points[1:]
            print("\n---------------------------\n")
            print(main_points)
            print("\n---------------------------\n")
        else:
            history_feedback[1]["content"] = "请判断学生的回答是否正确：" + "问题：" + socratic_question + "学生回答：" + user_input
            completion_feedback = client.chat.completions.create(
                model=model,
                messages=history_feedback,
                temperature=0,
                stream=True,
            )
            flag_comment = 0
            flag_judgement = 1
            comment = ""
            judgement = ""
            for chunk in completion_feedback:
                if chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="", flush=True)
                    if chunk.choices[0].delta.content in ['。']:
                        flag_comment = 1
                        flag_judgement = 0
                    if flag_judgement == 1:
                        judgement += chunk.choices[0].delta.content
                    if flag_comment == 1:
                        comment += chunk.choices[0].delta.content
            print("\n---------------------------\n")
            print(judgement)
            print("\n---------------------------\n")
            if judgement == "学生的回答不正确":
                history_feedback_extract[1]["content"] = "请列举出以下文本中有关正确答案的要点且保持要点间的逻辑顺序：" + comment
                completion_feedback_extract = client.chat.completions.create(
                    model=model,
                    messages=history_feedback_extract,
                    temperature=0,
                    stream=True,
                )
                correctness = ""
                for chunk in completion_feedback_extract:
                    if chunk.choices[0].delta.content:
                        print(chunk.choices[0].delta.content, end="", flush=True)
                        correctness += chunk.choices[0].delta.content
                unfinished_answer = ''.join(main_points)
                correctness = correctness + "\n2." + unfinished_answer
                main_points = []
                history_adjustment[1]["content"] = "以下文本中可能会出现重复信息。当重复的信息出现时，请你保留最开始出现的那一个。当你删除完给定文本中冗余的信息时，请你按序号列举出剩余信息。记住，你要保持信息间的相对顺序。" + correctness
                completion_adjustment = client.chat.completions.create(
                    model=model,
                    messages=history_adjustment,
                    temperature=0,
                    stream=True,
                )
                point_count = 1
                flag_point = 0
                main_point = ""
                for chunk in completion_adjustment:
                    if chunk.choices[0].delta.content:
                        print(chunk.choices[0].delta.content, end="", flush=True)
                        main_point += chunk.choices[0].delta.content
                        if chunk.choices[0].delta.content in ['.', '. ']:
                            if flag_point != 1:
                                continue
                            main_points.append(main_point)
                            point_count += 1
                            main_point = ""
                        if chunk.choices[0].delta.content in [f'{point_count}']:
                            flag_point = 1
                        else:
                            flag_point = 0
                main_points.append(main_point)
                main_points = main_points[1:]
                print("\n---------------------------\n")
                print(main_points)
                print("\n---------------------------\n")
        if len(main_points) == 0:
            flag = 0
            return jsonify({"server": "太好了！你现在对这个问题有了更加深刻的理解。请问你还有其他问题吗？"})
        else:
            socratic = ""
            point = main_points.pop(0)
            for i in range(4):
                question = ""
                history_question[1]["content"] = "请设计一个问题并确保以下文本是你所设计的问题的答案。" + point + "请直接输出你所设计的问题（不包括答案），问题："
                completion_question = client.chat.completions.create(
                    model=model,
                    messages=history_question,
                    temperature=0.7,
                    stream=True,
                )
                # print()
                for chunk in completion_question:
                    if chunk.choices[0].delta.content:
                        print(chunk.choices[0].delta.content, end=" ", flush=True)
                        question += chunk.choices[0].delta.content
                        if chunk.choices[0].delta.content in ['<|endoftext|>', '---\n', '？\n', '”\n\n', '”\n',  '"\n', '**\n\n', '"\n\n']:
                            break
                        if chunk.choices[0].delta.content in ['：']:
                            socratic_question = ""
                socratic = socratic + f'{i + 1}. ' + question
                print("\n---------------------------\n")
            print(f'POINT: {point}')
            print("\n---------------------------\n")
            print(f'PREVIOUS: {socratic_question}')
            print("\n---------------------------\n")
            print(f'SOCRATIC: {socratic}')
            print("\n---------------------------\n")
            history_selection[1]["content"] = "文本：" + point + "前一个问题：" + socratic_question + "备选问题：" + socratic + "请从以上四个备选问题中选择出与提供的文本最匹配且与前一个问题承接最连贯的那一个问题并直接输出。"
            completion_selection = client.chat.completions.create(
                model=model,
                messages=history_selection,
                temperature=0,
                stream=True,
            )
            socratic_question = ""
            flag = 0
            for chunk in completion_selection:
                if chunk.choices[0].delta.content:
                    if flag == 1:
                        socratic_question += chunk.choices[0].delta.content
                    print(chunk.choices[0].delta.content, end="", flush=True)
                    if chunk.choices[0].delta.content == '.':
                        flag = 1
            print("\n---------------------------\n")
            print("\n---------------------------\n")
            print("\n---------------------------\n")
            return jsonify({"server": socratic_question})

if __name__ == '__main__':
    app.run(debug=True)