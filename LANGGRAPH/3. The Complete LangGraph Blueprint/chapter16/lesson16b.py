def generate_code(state: dict) -> dict:
    """
    Generates a Python function based on the prompt.
    """
    if "factorial" in state['prompt']:
        state['generated_code'] = "def factorial(n): return 1 if n == 0 else n * factorial(n-1)"
    else:
        state['generated_code'] = "Unknown function requested."
    return state

def analyze_code(state: dict) -> dict:
    """
    Analyzes the generated code for improvements.
    """
    if "for i in range(len(" in state['generated_code']:
        state['suggestion'] = "Consider using enumerate() for better readability."
    else:
        state['suggestion'] = "Code looks good."
    return state


import unittest
from unittest.mock import patch

class TestAgentIntegration(unittest.TestCase):

    def test_generate_and_analyze_code(self, mock_generate):
        # Test the full workflow of generating and analyzing code
        
        # Mock the generate_code function's output
        mock_generate.return_value = {"generated_code": "for i in range(len(arr)): print(arr[i])", "prompt": ""}
        
        # Step 1: Generate code
        state = {"prompt": "Write a Python function to calculate factorial.", "generated_code": ""}
        generated_state = generate_code(state)
        
        # Step 2: Analyze generated code
        analysis_state = analyze_code(generated_state)
        
        # Verify the suggestion
        self.assertEqual(analysis_state['suggestion'], "Consider using enumerate() for better readability.")


if __name__ == '__main__':
    unittest.main()
