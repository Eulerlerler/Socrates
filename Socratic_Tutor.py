# Configuration
from openai import OpenAI
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
model = "qwen2-7b-instruct-q6_k/Repository"



# History
history_answer = [
    {"role": "system",
     "content": "你是一个智能助手。你总是提供合理的且符合逻辑的答案。"},
    {"role": "user",
     "content": ""},
]

history_logic = [
    {"role": "system",
     "content": "你是一个智能助手。你需要判断文本中是否存在多个事件间的逻辑关系。"},
    {"role": "user",
     "content": ""},
]

history_question = [
    {"role": "system",
     "content": "你是一个智能助手。我会给你提供一个或多个逻辑关系，你需要基于我所提供的逻辑关系设计一个引导性的问题。"},
    {"role": "user",
     "content": ""},
]

history_feedback = [
    {"role": "system",
     "content": "你是一名老师。你需要判断学生回答正确性。"},
    {"role": "user",
     "content": ""},
]

history_adjustment_correct = [
    {"role": "system",
     "content": "你是一个智能助手。我会给你提供一个文本和一些需要删除的信息。你需要从文本中删去与提供的信息意思相同或相近的部分，并保留剩下的部分。如果没有剩余的部分，你只需输出“没有剩余信息”。否则，当你删除完成时，你需要按序号列举出剩余信息。记住，你要保持信息间的相对顺序。"},
    {"role": "user",
     "content": ""},
]

history_adjustment_incorrect = [
    {"role": "system",
     "content": "你是一个智能助手。我会给你提供一个文本，这个文本中可能会出现重复的信息。当重复的信息出现时，你只需要保留最开始出现的那一个。当你删除完给定文本中冗余的信息时，你需要按序号列举出剩余信息。记住，你要保持信息间的相对顺序。"},
    {"role": "user",
     "content": ""},
]



# Model
hop_steps = 3
user_question = input()
Socratic_question = ""
history_answer[1]["content"] = "请一步步回答：" + user_question
sub_points = []
logic_pairs = []
sub_point = ""
point_count = 1
flag_answer = 0
completion_answer = client.chat.completions.create(
    model=model,
    messages=history_answer,
    temperature=0,
    stream=True,
)
for chunk in completion_answer:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
        point_count += chunk.choices[0].delta.content
        if chunk.choices[0].delta.content in ['.', '. ']:
            if flag_answer != 1:
                continue
            sub_points.append(sub_point)
            point_count += 1
            sub_point = ""
        if chunk.choices[0].delta.content in [f'{point_count + 1}']:
            flag_answer = 1
        else:
            flag_answer = 0
        if chunk.choices[0].delta.content in ['<|endoftext|>', '---\n\n']:
            break
sub_points.append(sub_point)
print("\n---------------------------\n")
print(sub_points)
print("\n---------------------------\n")
while True:
    point = sub_points[0]
    history_logic[1]["content"] = "请你判断文本中是否存在多个事件间的逻辑关系。其中，所需列举的逻辑关系主要分为对比、因果以及溯因这三类。三类逻辑关系的定义和举例如下： \
                                   对比关系：对比关系描述了多个事件在一个属性上的区别。当对比关系出现时，你需要按照以下格式将其列举出来：[逻辑关系：对比关系，事件：（产生对比关系的多个事件），属性：（产生区别的属性）] \
                                   例如，给定如下文本：地表反照率在不同季节变化，夏季反射减少，冬季反射增加。 \
                                   该文本描述了地表反射率在夏季和冬季的不同情况，因此存在对比关系。其中，拥有对比关系的事件是夏季和冬季，产生区别的属性是地表反射率。 \
                                   因此，你需要按照以下格式将其列举出来：1. 逻辑关系：对比关系，事件：夏季、冬季，属性：地表反射率 \
                                   因果关系：因果关系描述了一个事件导致另外一个事件的发生。当因果关系出现时，你需要按照以下格式列举出来：[逻辑关系：因果关系，事件：（产生因果关系的事件），结果：（该事件导致的结果）] \
                                   例如，给定如下文本：阳光照射到这些水滴上，光线会分散并折射。 \
                                   该文本描述了阳光照射到水滴上以后会发生分散和折射的现象，因此存在因果关系。其中，产生因果关系的事件是阳光照射到水滴上，该事件导致的结果是光线会分散并折射。 \
                                   因此，你需要按照以下格式将其列举出来：1. 逻辑关系：因果关系，原因：阳光照射到水滴上，结果：光线会分散并折射 \
                                   溯因关系：溯因关系描述了一个事件产生的原因。当溯因关系出现时，你需要按照以下格式将其列举出来：[逻辑关系：溯因关系，事件：（产生溯因关系的事件），原因：（该事件产生的原因）] \
                                   例如，给定如下文本：萤火虫的能量主要来自食物，特别是它们摄取的昆虫和小型水生动物。 \
                                   该文本描述了萤火虫的能量来源，因此存在溯因关系。其中，产生溯因关系的事件是萤火虫的能量来源，该事件产生的原因是食物，特别是它们摄取的昆虫和小型水生动物。 \
                                   因此，你需要按照以下格式将其列举出来：1. 逻辑关系：溯因关系，事件：萤火虫的能量来源，原因：食物，特别是它们摄取的昆虫和小型水生动物 \
                                   以上三个逻辑关系提取的优先级是：对比关系提取的优先级最高，其次是因果关系和溯因关系。当提取逻辑关系时，你应该优先提取先出现的事件间的逻辑关系，并按照优先级提取他们之间全部的逻辑关系，然后再提取后出现的事件间全部的逻辑关系。 \
                                   现在，请你按照以上规定依次列举出以下文本中所有存在的事件间的逻辑关系：" + point
    completion_logic = client.chat.completions.create(
        model=model,
        messages=history_logic,
        temperature=0,
        stream=True,
    )
    logic_pairs = []
    point_count = 1
    flag_point = 0
    logic_pair = ""
    for chunk in completion_logic:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
            logic_pair += chunk.choices[0].delta.content
            if chunk.choices[0].delta.content in ['.', '. ']:
                if flag_point != 1:
                    continue
                logic_pairs.append(logic_pair)
                point_count += 1
                logic_pair = ""
            if chunk.choices[0].delta.content in [f'{point_count + 1}']:
                flag_point = 1
            else:
                flag_point = 0
            if chunk.choices[0].delta.content in ['<|endoftext|>', '\n\n']:
                break
    logic_pairs.append(logic_pair)
    logics = ""
    for i in range(hop_steps):
        if len(logic_pairs) == 0:
            break
        logics += logic_pairs.pop(0)
    history_question[1]["content"] = "我会给你提供一个或多个逻辑关系，这些逻辑关系按照递进的顺序列出，分别描述了一件事件如何与另外一个事件相关联。 \
                                      其中，对比关系描述了多个事件在一个属性上的区别，因果关系表明前一事件会导致后一事件的发生，溯因关系描述了一个事件产生的原因。 \
                                      所提供的逻辑关系构成了一个推理的链条，你需要从最开始的事件出发，隐藏中间的推理步骤，设计一个需要多步推理的引导性的问题，引导用户自我完成中间的推理步骤，思考出最开始的事件将会引发的结果。 \
                                      现在，给定以下逻辑关系：" + logics + "请你将这些逻辑关系整合成一个需要多步推理的引导性的问题，引导用户自我思考将会产生的变化："
    Socratic_question = ""
    completion_question = client.chat.completions.create(
        model=model,
        messages=history_question,
        temperature=0,
        stream=True,
    )
    for chunk in completion_question:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
            Socratic_question += chunk.choices[0].delta.content
    print("\n---------------------------\n")
    user_input = input()
    history_feedback[1]["content"] = "请判断学生的回答是否正确：" + "问题：" + Socratic_question + "学生回答：" + user_input + "如果学生回答正确了，请直接输出“正确”，否则请一步步回答问题。"
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
    if judgement == "正确":
        unfinished_answer = ''.join(sub_points)
        text = user_input + "\n2." + unfinished_answer
        sub_points = []
        history_adjustment_correct[1]["content"] = "你是一个智能助手。我会给你提供一个文本，这个文本中可能会出现重复的信息。你需要删除给定文本中的重复信息，当你删除完给定文本中冗余的信息时，你需要按序号列举出剩余信息。记住，你要保持信息间的相对顺序。" + text
        completion_adjustment = client.chat.completions.create(
            model=model,
            messages=history_adjustment_correct,
            temperature=0,
            stream=True,
        )
        point_count = 1
        flag_point = 0
        sub_point = ""
        flag = ""
        for chunk in completion_adjustment:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
                sub_point += chunk.choices[0].delta.content
                flag += chunk.choices[0].delta.content
                if chunk.choices[0].delta.content in ['.', '. ']:
                    if flag_point != 1:
                        continue
                    sub_points.append(sub_point)
                    point_count += 1
                    main_point = ""
                if chunk.choices[0].delta.content in [f'{point_count}']:
                    flag_point = 1
                else:
                    flag_point = 0
        sub_points.append(sub_point)
        sub_points = sub_points[1:]
        print("\n---------------------------\n")
        print(sub_points)
        print("\n---------------------------\n")
        if flag == "没有剩余信息":
            break
    else:
        unfinished_answer = ''.join(sub_points)
        text = judgement + "\n2." + unfinished_answer
        sub_points = []
        history_adjustment_incorrect[1]["content"] = "以下文本中可能会出现重复信息。当重复的信息出现时，请你保留最开始出现的那一个。当你删除完给定文本中冗余的信息时，请你按序号列举出剩余信息。记住，你要保持信息间的相对顺序。" + text
        completion_adjustment = client.chat.completions.create(
            model=model,
            messages=history_adjustment_incorrect,
            temperature=0,
            stream=True,
        )
        point_count = 1
        flag_point = 0
        sub_point = ""
        for chunk in completion_adjustment:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
                sub_point += chunk.choices[0].delta.content
                if chunk.choices[0].delta.content in ['.', '. ']:
                    if flag_point != 1:
                        continue
                    sub_points.append(sub_point)
                    point_count += 1
                    main_point = ""
                if chunk.choices[0].delta.content in [f'{point_count}']:
                    flag_point = 1
                else:
                    flag_point = 0
        sub_points.append(sub_point)
        sub_points = sub_points[1:]
        print("\n---------------------------\n")
        print(sub_points)
        print("\n---------------------------\n")