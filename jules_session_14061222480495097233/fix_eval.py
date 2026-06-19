with open("code/evaluation/main.py", "r") as f:
    content = f.read()

content = content.replace("model=\"gpt-4o-mini\"", "model=\"gpt-4o\"")

with open("code/evaluation/main.py", "w") as f:
    f.write(content)
    
with open("code/agent.py", "r") as f:
    content = f.read()

content = content.replace("model=\"gpt-4o-mini\"", "model=\"gpt-4o\"")

with open("code/agent.py", "w") as f:
    f.write(content)
