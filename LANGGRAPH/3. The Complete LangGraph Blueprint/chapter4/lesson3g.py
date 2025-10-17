def check_age(age):
    if age < 0:
        raise ValueError("Age cannot be negative")
    elif age < 18:
        print("Not eligible to vote")
    else:
        print("Eligible to vote")

try:
    check_age(-5)
except ValueError as e:
    print(e)  # Outputs: Age cannot be negative

try:
    number = int(input("Enter a number: "))
    result = 10 / number
except ValueError:
    print("You must enter a valid integer.")
except ZeroDivisionError:
    print("You can't divide by zero.")
else:
    print(f"Result: {result}")
finally:
    print("Execution completed.")

try:
    number = int(input("Enter a number: "))
    result = 10 / number
except ZeroDivisionError as e:
    raise RuntimeError("Failed to divide") from e

from langgraph import Graph, Node

class APIRequestNode(Node):
    def run(self):
        try:
            data = self.make_request()
            self.send_output(data)
        except TimeoutError:
            self.send_output("The request timed out.")
        except ValueError as e:
            self.send_output(f"Invalid data: {e}")
        finally:
            self.log("Request completed.")

graph = Graph()
node = APIRequestNode()
graph.add_node(node)





