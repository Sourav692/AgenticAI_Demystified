# Concatenation
greeting = "Hello" + " " + "World"
print(greeting)  # Outputs: Hello World

# Repetition
echo = "Echo " * 3
print(echo)  # Outputs: Echo Echo Echo

text = "LangGraph"
# Extracting a substring
print(text[0:4])  # Outputs: Lang
print(text[-5:])  # Outputs: Graph

name = "Alice"
age = 30
# Using f-strings for formatting
print(f"My name is {name}, and I am {age} years old.")  # Outputs: My name is Alice, and I am 30 years old.

text = "LangGraph is a powerful framework."
# Searching for a substring
print(text.find("powerful"))  # Outputs: 13
print("Graph" in text)        # Outputs: True

# Splitting a string into a list
words = text.split(" ")
print(words)  # Outputs: ['LangGraph', 'is', 'a', 'powerful', 'framework.']

# Joining a list into a string
sentence = " ".join(words)
print(sentence)  # Outputs: LangGraph is a powerful framework.

text = "LangGraph"
print(text.upper())   # Outputs: LANGGRAPH
print(text.lower())   # Outputs: langgraph
print(text.title())   # Outputs: Langgraph


