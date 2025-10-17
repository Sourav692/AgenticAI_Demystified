import unittest
from unittest.mock import patch
from react_agent_module import graph, ReActAgentState

class TestReActAgentWorkflow(unittest.TestCase):

    @patch('react_agent_module.llm_tool.invoke')
    def test_full_workflow(self, mock_invoke):
        # Mock responses for each stage in the workflow
        mock_invoke.side_effect = [
            type('', (), {'content': "Python programming\nBest practices\nCode readability"})(),  # Search results
            type('', (), {'content': "Best practices"})(),  # Filtered results
            type('', (), {'content': "# Python Best Practices\n\n- Code readability"})()  # Markdown document
        ]

        # Set up initial state and invoke the full workflow
        initial_state = {"query": "Python programming best practices", "search_results": [], "markdown_result": ""}
        result = graph.invoke(initial_state)

        # Verify the final Markdown result
        expected_markdown = "# Python Best Practices\n\n- Code readability"
        self.assertEqual(result['markdown_result'], expected_markdown)

if __name__ == '__main__':
    unittest.main()
