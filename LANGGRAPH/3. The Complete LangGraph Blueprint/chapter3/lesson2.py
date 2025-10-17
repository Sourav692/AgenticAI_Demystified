#Python Programming Concepts useful in LangGraph

#1. A variable is a name that holds a value.
greeting = "Hello World"

#2. Once a variable is assigned a value, you can show its value
# using the print function
print(greeting)  # Output: Hello World

#3. Python automatically determines the type based on the value assigned:
age = 25          # Integer
price = 19.99     # Float
name = "Alice"    # String
is_active = True  # Boolean
unknown = None    # NoneType
my_tuple = (1, "hello", 3.14) # Tuple
colors = ['red', 'blue', 'green'] #List

print(age) #output is 25
print(price) #output is 19.99
print (name) # output is “Alice” 
print(is_active) #output is True
print(my_tuple[0]) #output is 1
print(my_tuple[1]) #output is Hello
print(colors[0])    # output is red
print(colors[2])    # output is green
print(len(colors))  # Length of the list is 3

#4. Assigning a value of a different type
data = "Hello"
print(type(data))  # Output: <class 'str'>
data = 100
print(type(data))  # Output: <class 'int'>
data = "Hello Again"
print(type(data))  # Output: <class 'str'>

#5. Variable naming rules
#5a. Variables cannot start with a number
user_name = "Alice"  # Valid
user2 = "Bob"        # Valid
#2user = "Charlie"    # Invalid

#5b. Python is case-sensitive
UserName = "Alice"
username = "Bob"
print(UserName)  # Output: Alice
print(username)  # Output: Bob

#5c. Use snake case - lowercase letters with underscores between words
first_name = "Alice"
account_balance = 1000.00

#5d. Use meaningful names
temperature = 36.6  # Clear and descriptive
x = 36.6            # Not descriptive

#5e. Invalid variable names
#if = 5     # SyntaxError
#class = 10 # SyntaxError

#6. Global variables
greeting = "Hello, World!" #This variable can be accessed by many functions
def say_hello():
    print(greeting)
say_hello()  # Output: Hello, World!

#7. Local variables
def greet():
    message = "Hi there!"
    print(message)
greet()        # Output: Hi there!
#print(message) # NameError: name 'message' is not defined

#8. Contants
PI = 3.14159  #ALL CAPS indicates its value should not be changed
MAX_USERS = 100

#9. Unpacking a tuple
coordinates = (10, 20)
x, y = coordinates
print(x)  # Output: 10
print(y)  # Output: 20

#10. Unpacking a list
names = ["Alice", "Bob", "Charlie"]
first, second, third = names
print(first)  # Output: Alice

#11. Excess unpacking 
numbers = [1, 2, 3, 4, 5]
first, *middle, last = numbers
print(middle)  # Output: [2, 3, 4]

#12. Declaring a function
def say_hello():
    print("Hello World!")

#13. Execute code within a function
say_hello()  # Output: Hello World!

#14. Function parameters
def greet(name):
    print(f"Hello, {name}!")

#15. Function arguments, change Alice to any name and run it to see
greet("Alice")  # Output: Hello, Alice!

#16. Positional arguments
def add(a, b):
    return a + b

print(add(5, 3))  # Output: 8

#17. Use Keyword Arguments to specify default values
def create_user(name, age=18):
    print(f"User: {name}, Age: {age}")

create_user(name="Bob", age=25)  # Output: User: Bob, Age: 25
create_user(name="Alice")        # Output: User: Alice, Age: 18

#18. Default values
def greet(name="World"):
    print(f"Hello, {name}!")

greet()         # Output: Hello, World!
greet("Alice")  # Output: Hello, Alice!

#19. Variable positional arguments
def sum_all(*args):
    total = sum(args)
    print(f"Total: {total}")

sum_all(1, 2, 3, 4)  # Output: Total: 10

#20. Variable keyword arguments
def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_info(name="Alice", age=30, country="Wonderland")
# Output:
# name: Alice
# age: 30
# country: Wonderland

#21.Returning a value. If return is not specified, NoneType is returned
def add(a, b):
    return a + b

result = add(5, 3)
print(result)  # Output: 8

#22. Returning multiple values as a tuple
def get_user():
    return "Alice", 30

name, age = get_user()
print(name, age)  # Output: Alice 30

#23. Lambda functions
add = lambda x, y: x + y
print(add(3, 5))  # Output: 8

# Using lambda in a higher-order function
numbers = [1, 2, 3, 4]
squared = list(map(lambda x: x ** 2, numbers))
print(squared)  # Output: [1, 4, 9, 16]

#24. Function decorators
def log_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"Executing {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_decorator
def greet(name):
    print(f"Hello, {name}!")

greet("Alice")
# Output:
# Executing greet
# Hello, Alice!

#25. Recursive function
def factorial(n):
    if n == 1:
        return 1
    else:
        return n * factorial(n - 1)

print(factorial(5))  # Output: 120

#26.Documenting your code
def greet(name):
    """Greets a person by name."""
    print(f"Hello, {name}!")

help(greet) # Output:
# Help on function greet in module __main__:
# greet(name)
#    Greets a person by name.

#27. Dictionary
person = {"name": "Alice", "age": 30, "is_active": True }
print(person["name"])  # Output: Alice
print(person["age"])   # Output: 30
print(person["is_active"])  # Output: True  

#28. Creating dictionaries
#Using curly braces
user_info = { "name": "Alice", "age": 30 }
#Using the dict() constructor
user_info = dict([("name", "Alice"), ("age", 30)])
user_info = dict(name="Alice", age=30)
#Using dict.fromkeys
keys = ["name", "age", "is_active"]
user_info = dict.fromkeys(keys, None)
print(user_info)
# Output: {'name': None, 'age': None, 'is_active': None}

#29. Accessing a dictionary
user_info = {"name": "Alice", "age": 30}
print(user_info["name"])  # Output: Alice

#30. Alternative way to acess a dictionary with default value
print(user_info.get("location", "Unknown"))  # Output: Unknown

#31. Adding a dictionary
user_info["location"] = "Wonderland"  # Adds a new key-value pair
user_info["age"] = 31                # Updates the value for the existing key
print(user_info)
# Output: {'name': 'Alice', 'age': 31, 'location': 'Wonderland'})

#32: Removing items from the dictionary
age = user_info.pop("age")
print(age)  # Output: 31
print(user_info)
# Output: {'name': 'Alice', 'location': 'Wonderland'}

del user_info["location"]
del user_info  # Deletes the entire dictionary

#last_item = user_info.popitem()

#user_info.clear()  # Removes all items from the dictionary

#33. Dictionary methods
user_info = {"name": "James", "age": 45}
keys = user_info.keys()      # Returns a view of the keys
print(keys)
values = user_info.values()  # Returns a view of the values
print(values)
items = user_info.items()    # Returns a view of the key-value pairs
print(items)

#34. Iterating over a dictionary
for key in user_info:
    print(key)
for value in user_info.values():
    print(value)
for key, value in user_info.items():
    print(key, value)

#35. Updating a dictionary
user_info.update({"location": "Nairobi", "age": 32})
print(user_info)

#Retrieve or set default value
user_info.setdefault("is_active", True)

#36. Nested dictionaries
user_info = {
    "name": "Alice",
    "contact": {
        "email": "alice@example.com",
        "phone": "123-456-7890"
    }
}
print(user_info["contact"]["email"])  # Output: alice@example.com

#37. Accessing nested values
email = user_info["contact"]["email"]
phone = user_info.get("contact", {}).get("phone", "Not available")
print(email, phone)

#38. Modofying nested dictionary values
user_info["contact"]["email"] = "new_email@example.com"

#39. Comprehension
# Creating a dictionary with squares of numbers
squares = {x: x ** 2 for x in range(5)}
print(squares)
# Output: {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

#40. Copying dictionaries
user_info_copy = user_info.copy()
user_info_copy["name"] = "Bob"
print(user_info["name"])  # Output: Alice
print(user_info_copy["name"])  # Output: Bob

#Nested copy
import copy
deep_copy = copy.deepcopy(user_info)
print(deep_copy)

#41. Merging two dictionaries
dict1 = {"a": 1, "b": 2}
dict2 = {"b": 3, "c": 4}
# Merging
merged = dict1 | dict2
# Output: {'a': 1, 'b': 3, 'c': 4}
# In-place merge
dict1 |= dict2
# Output: {'a': 1, 'b': 3, 'c': 4}

#42. TypedDict
from typing_extensions import TypedDict
class Person(TypedDict):
    name: str
    age: int

person : Person = {"name": "Alice", "age": 30}
print(person["name"])  # Output: Alice

#Factory method
Person = TypedDict('Person', {'id': int, 'name': str, 'age': int})

#43. Nested Dictionaries with TypedDict
class Address(TypedDict):
    street: str
    city: str
    zip_code: int

class UserProfile(TypedDict):
    username: str
    email: str
    address: Address

profile: UserProfile = {
    "username": "johndoe",
    "email": "johndoe@example.com",
    "address": {
        "street": "123 Elm St",
        "city": "Metropolis",
        "zip_code": 12345
    }
}

#44. TypedDict in functions
class User(TypedDict):
    name: str
    age: int
    is_active: bool

def display_user_info(user: User) -> None:
    print(f"Name: {user['name']}, Age: {user['age']}, Active: {user['is_active']}")

user_data = {"name": "Alice", "age": 30, "is_active": True}
display_user_info(user_data)

#45. TypedDict as Return Type
def create_user(name: str, age: int) -> User:
    return {"name": name, "age": age, "is_active": True}

new_user = create_user("Bob", 25)
print(new_user)
#Output {'name': 'Bob', 'age': 25, 'is_active': True}

from typing_extensions import TypedDict

#46. Default values with Typed Dict
class ServerConfig(TypedDict):
    host: str
    port: int
    use_ssl: bool

def create_default_server_config() -> ServerConfig:
    return {
        "host": "localhost",
        "port": 8080,
        "use_ssl": False
    }

config = create_default_server_config()

#47. Typed Dict inheritance

class BaseUser(TypedDict):
    username: str
    email: str

class AdminUser(BaseUser):
    access_level: int

admin: AdminUser = {
    "username": "admin",
    "email": "admin@example.com",
    "access_level": 5
}

#48. Classes
class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age

# Creating an object of the Dog class
my_dog = Dog("Buddy", 3)
print(my_dog.name)  # Output: Buddy
print(my_dog.age)   # Output: 3

#49 Class Attributes
class Dog:
    species = "Canis lupus"  # Class attribute

    def __init__(self, name, age):
        self.name = name    # Instance attribute
        self.age = age      # Instance attribute

# Accessing attributes
dog1 = Dog("Buddy", 3)
dog2 = Dog("Lucy", 5)
print(dog1.species)  # Output: Canis lupus
print(dog1.name)     # Output: Buddy

#50 Methods
class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def bark(self):
        return f"{self.name} says woof!"

dog = Dog("Buddy", 3)
print(dog.bark())  # Output: Buddy says woof!

#51: Initializer
class Car:
    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year

my_car = Car("Toyota", "Corolla", 2021)
print(my_car.make)  # Output: Toyota

#52. Self keyword
class Cat:
    def __init__(self, name):
        self.name = name

    def meow(self):
        return f"{self.name} says meow!"

cat = Cat("Whiskers")
print(cat.meow())  # Output: Whiskers says meow!

#53. Inheritance
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "Some generic sound"

class Dog(Animal):  # Dog inherits from Animal
    def speak(self):
        return f"{self.name} says woof!"

dog = Dog("Buddy")
print(dog.speak())  # Output: Buddy says woof!

#54. Multiple inheritance
class Walker:
    def walk(self):
        return "Walking..."

class Swimmer:
    def swim(self):
        return "Swimming..."

class Amphibian(Walker, Swimmer):
    pass

frog = Amphibian()
print(frog.walk())  # Output: Walking...
print(frog.swim())  # Output: Swimming...

#55. Encapsulation and access modifiers
class BankAccount:
    def __init__(self, owner, balance):
        self.owner = owner
        self._balance = balance  # Protected

    def __withdraw(self, amount):  # Private method
        if amount <= self._balance:
            self._balance -= amount
            return self._balance
        return "Insufficient funds"

account = BankAccount("Alice", 1000)
print(account._balance)  # Accessing a protected attribute (not recommended)

#55.Class Methods
class Person:
    species = "Homo sapiens"

    @classmethod
    def set_species(cls, new_species):
        cls.species = new_species

Person.set_species("Homo sapiens sapiens")
print(Person.species)  # Output: Homo sapiens sapiens

#56. Static methods
class Math:
    @staticmethod
    def add(a, b):
        return a + b


print(Math.add(3, 5))  # Output: 8

#57. Magic methods
class Car:
    def __init__(self, make, model):
        self.make = make
        self.model = model

    def __str__(self):
        return f"{self.make} {self.model}"

    def __repr__(self):
        return f"Car('{self.make}', '{self.model}')"

car = Car("Toyota", "Corolla")
print(car)  # Output: Toyota Corolla
print(repr(car))  # Output: Car('Toyota', 'Corolla')

#58. Operator overloading
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

v1 = Vector(1, 2)
v2 = Vector(3, 4)
result = v1 + v2
print(result.x, result.y)  # Output: 4 6

#5.9 Class Properties
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    @property
    def area(self):
        return self.width * self.height

rect = Rectangle(5, 10)
print(rect.area)  # Output: 50

#60 Class properties controlling attributes
class Rectangle:
    def __init__(self, width, height):
        self._width = width
        self._height = height

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        if value > 0:
            self._width = value
        else:
            raise ValueError("Width must be positive")


#61. Type hints
from typing import List, Dict, Optional

def process_data(data: Dict[str, Optional[List[int]]]) -> None:
    print(data)

#62. Async
import asyncio

async def fetch_data():
    await asyncio.sleep(1)
    return "Data fetched!"

async def main():
    results = await asyncio.gather(fetch_data(), fetch_data())
    print(results)

asyncio.run(main())

#63 HTTP Requests
import requests
try:
    response = requests.get("https://api.example.com/data")
    if response.status_code == 200:
        data = response.json()
        print(data)
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")


#64. Pydantic
from pydantic import BaseModel, Field, ValidationError

class User(BaseModel):
    name: str
    age: int = Field(..., gt=0)

try:
    user = User(name="Alice", age=-1)
except ValidationError as e:
    print(e)

#65. Logging
import logging

# Configure basic logging settings
logging.basicConfig(level=logging.INFO)  # Sets logging to capture INFO and above messages

# Create a logger instance
logger = logging.getLogger(__name__)

# Log an informational message
logger.info("This is an informational message.")

#66. SubProcess
import sys
import subprocess

result = subprocess.run(["echo", "Hello, LangGraph!"], capture_output=True, text=True, executable=sys.executable)
print(result.stdout)

#67. json
import json

data = {"name": "Alice", "age": 30}
with open("data.json", "w") as f:
    json.dump(data, f)

#68. Pandas

import pandas as pd

try:
    df = pd.read_csv("data.csv")
    print(df.head())
except FileNotFoundError:
    print("File not found")


#68. Matplotlib

try:
    import matplotlib.pyplot as plt
    plt.plot([1, 2, 3, 4], [10, 20, 25, 30])
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.show()
except Exception as e:
    print(f"Error: {e}")


#69. Seaborn
import seaborn as sns

sns.set(style="darkgrid")
tips = sns.load_dataset("tips")
sns.scatterplot(x="total_bill", y="tip", data=tips)
plt.show()


#70. sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

try: 
    engine = create_engine("sqlite:///data.db")
    Session = sessionmaker(bind=engine)
    session = Session()
except Exception as e:
    print(f"Error: {e}")

#71. Json
import json

# Writing to a JSON file
data = {"name": "Alice", "age": 30}
try:
    with open("data.json", "w") as f:
        json.dump(data, f)
except Exception as e:
    print(f"Error: {e}")


# Reading from a JSON file
with open("data.json", "r") as f:
    loaded_data = json.load(f)
print(loaded_data)  # Output: {'name': 'Alice', 'age': 30}

#How to instal yaml module: pip install PyYAML
#72. yaml file handling
import yaml
# Writing to a YAML file
config = {"name": "Alice", "roles": ["admin", "user"]}
try:
    with open("config.yaml", "w") as f:
        yaml.dump(config, f)

    # Reading from a YAML file
    with open("config.yaml", "r") as f:
        loaded_config = yaml.safe_load(f)
    print(loaded_config)  # Output: {'name': 'Alice', 'roles': ['admin', 'user']}

except Exception as e:
    print(f"Error: {e}")

#73. Operating system file handling
import os
try:
    #Create a folder
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Get an environment variable
    api_key = os.environ.get("API_KEY", "default_value")

except Exception as e:
    print(f"Error: {e}")

#74.sys 
import sys
import os
# Check if enough arguments were passed
if len(sys.argv) < 2:
    print("Usage: python script.py <filename>")
    #sys.exit("Please provide a file path as an argument.")
else:
    # Accessing command-line arguments
    filename = sys.argv[1]
    print(f"Processing file: {filename}")

#Exit management
def process_data(data):
    if not data:
        print("Error: No data provided.")
        #sys.exit(1)  # Exit with an error status

    print("Data processed successfully.")
    #sys.exit(0)  # Exit with a success status

# Simulating a scenario with empty data
data = None
process_data(data)

# Define a directory containing custom modules
custom_module_path = os.path.join(os.getcwd(), "custom_modules")

# Add the directory to sys.path if it's not already there
if custom_module_path not in sys.path:
    sys.path.append(custom_module_path)

# Now you can import custom modules from the added path
try:
    import custom_modules
    print("Custom module imported successfully.")
except ImportError:
    print("Failed to import custom module.")

#75. Random
import random
# Generate a random integer between 1 and 100
random_number = random.randint(1, 100)
print(random_number)
# Choose a random item from a list
options = ["apple", "banana", "cherry"]
fruit = random.choice(options)
print(fruit)
# Shuffle a list
numbers = [1, 2, 3, 4, 5]
shuffle = random.shuffle(numbers)
print(shuffle)
#Uniform float numbers
random_float = random.uniform(0, 1)
print(random_float)

#76. DateTime
from datetime import datetime, timedelta

# Get the current date and time
now = datetime.now()

# Calculate a future date by adding a timedelta
future_date = now + timedelta(days=5)
print(future_date.strftime("%Y-%m-%d"))

#77. Collections
from collections import Counter, defaultdict

# Counting occurrences of items in a list
words = ["apple", "banana", "apple", "cherry"]
word_count = Counter(words)
print(word_count)
# Output: Counter({'apple': 2, 'banana': 1, 'cherry': 1})

# Using defaultdict to handle missing keys
fruits = defaultdict(int)
fruits["apple"] += 1
print(fruits)  # Output: defaultdict(<class 'int'>, {'apple': 1})

#78. Iter Tools
from itertools import cycle

# Cycling through a list indefinitely
colors = cycle(["red", "green", "blue"])
for _ in range(6):
    print(next(colors))

#79.Map
# List of numbers to square
numbers = [1, 2, 3, 4]

# Using map to square each number
squares = list(map(lambda x: x**2, numbers))
print(squares)  # Output: [1, 4, 9, 16]

# List of strings
words = ["hello", "world", "langgraph"]

# Using map to convert each string to uppercase
uppercase_words = list(map(lambda word: word.upper(), words))
print(uppercase_words)  # Output: ['HELLO', 'WORLD', 'LANGGRAPH']

# List of dictionaries with user data
users = [
    {"name": "Alice", "age": 25},
    {"name": "Bob", "age": 30},
    {"name": "Charlie", "age": 35}
]

# Using map to extract only the 'name' field from each dictionary
names = list(map(lambda user: user["name"], users))
print(names)  # Output: ['Alice', 'Bob', 'Charlie']

#80.Filter
# List of numbers to filter
numbers = [1, 2, 3, 4, 5, 6]

# Using filter to keep only even numbers
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)  # Output: [2, 4, 6]

# List of names
names = ["Alice", "Bob", "Charlie", "Dave"]

# Using filter to keep names with more than 3 characters
long_names = list(filter(lambda name: len(name) > 3, names))
print(long_names)  # Output: ['Alice', 'Charlie', 'Dave']

# List of dictionaries with user data
users = [
    {"name": "Alice", "age": 25},
    {"name": "Bob", "age": 20},
    {"name": "Charlie", "age": 35}
]

# Using filter to keep only users who are 30 years or older
adult_users = list(filter(lambda user: user["age"] >= 30, users))
print(adult_users)  # Output: [{'name': 'Charlie', 'age': 35}]


#81. Reduce
from functools import reduce
# List of numbers to sum
numbers = [1, 2, 3, 4]
# Using reduce to sum all numbers
total_sum = reduce(lambda x, y: x + y, numbers)
print(total_sum)  # Output: 10
# List of numbers to multiply
numbers = [1, 2, 3, 4]
# Using reduce to multiply all numbers together
product = reduce(lambda x, y: x * y, numbers)
print(product)  # Output: 24
# List of strings
words = ["hello", "world", "langgraph", "is", "awesome"]
# Using reduce to find the longest string in the list
longest_word = reduce(lambda x, y: x if len(x) > len(y) else y, words)
print(longest_word)  # Output: 'langgraph'

#82. Combining map, reduce and filter
from functools import reduce
# List of numbers
numbers = [1, 2, 3, 4, 5, 6]

# Filtering even numbers, mapping to squares, and reducing to sum
sum_of_squares_of_evens = reduce(
    lambda x, y: x + y,
    map(lambda x: x**2, filter(lambda x: x % 2 == 0, numbers))
)
print(sum_of_squares_of_evens)  # Output: 56 (2^2 + 4^2 + 6^2)


#83. Aync basics

import asyncio

async def fetch_data():
    await asyncio.sleep(1)  # Simulates a non-blocking wait
    return "Data fetched!"

# Run the asynchronous function
result = asyncio.run(fetch_data())
print(result)  # Output: Data fetched!

#Sequential tasks
async def task1():
    await asyncio.sleep(1)
    print("Task 1 completed")

async def task2():
    await asyncio.sleep(2)
    print("Task 2 completed")

async def main():
    await task1()
    await task2()

asyncio.run(main())

#Concurrent tasks
async def task(name):
    await asyncio.sleep(1)
    print(f"Task {name} completed")

async def main():
    await asyncio.gather(task("A"), task("B"), task("C"))

asyncio.run(main())
#Output: 
# Task A completed
# Task B completed
# Task C completed

#Concurrent IO
async def fetch_source(source):
    print(f"Fetching from {source}...")
    await asyncio.sleep(2)
    print(f"Completed fetching from {source}")

async def main():
    sources = ["Source 1", "Source 2", "Source 3"]
    await asyncio.gather(*(fetch_source(source) for source in sources))

asyncio.run(main())
#Output
# Fetching from Source 1...
# Completed fetching from Source 1
# Fetching from Source 2...
# Completed fetching from Source 2
# Fetching from Source 3...
# Completed fetching from Source 3

#error hanndling async
async def faulty_task():
    try:
        raise ValueError("An error occurred")
    except ValueError as e:
        print(f"Error: {e}")

asyncio.run(faulty_task())
#Output


async def task1():
    raise ValueError("Error in Task 1")

async def task2():
    await asyncio.sleep(1)
    return "Task 2 completed successfully"

async def main():
    results = await asyncio.gather(task1(), task2(), return_exceptions=True)
    for result in results:
        if isinstance(result, Exception):
            print(f"Handled exception: {result}")
        else:
            print(result)

asyncio.run(main())
#Output
# Error: ValueError("Error in Task 1")
# Task 2 completed successfully

#84. Async in Langraph 
import asyncio

async def fetch_data_for_node(node_id, api_url):
    print(f"Node {node_id}: Fetching data from {api_url}...")
    await asyncio.sleep(2)  # Simulates a network delay
    print(f"Node {node_id}: Completed data fetch from {api_url}")
    return f"Data from {api_url}"

async def main():
    # URLs for data fetching in different nodes
    nodes = {
        "Node 1": "https://api.example.com/data1",
        "Node 2": "https://api.example.com/data2",
        "Node 3": "https://api.example.com/data3"
    }

    # Concurrently fetch data for all nodes
    results = await asyncio.gather(
        *(fetch_data_for_node(node_id, url) for node_id, url in nodes.items())
    )
    
    print("All data fetched:", results)

asyncio.run(main())
#Output
#Node Node 1: Fetching data from https://api.example.com/data1...
#Node Node 2: Fetching data from https://api.example.com/data2...
#Node Node 3: Fetching data from https://api.example.com/data3...
#Node Node 1: Completed data fetch from https://api.example.com/data1
#Node Node 2: Completed data fetch from https://api.example.com/data2
#Node Node 3: Completed data fetch from https://api.example.com/data3
#All data fetched: ['Data from https://api.example.com/data1', 'Data from https://api.example.com/data2', 'Data from https://api.example.com/data3']

#85. 










































