
import unittest
from unittest.mock import patch
from react_agent_module import perform_search, filter_results, compile_markdown

class TestReActAgent(unittest.TestCase):

    @patch('react_agent_module.llm_tool.invoke')
    def test_perform_search(self, mock_invoke):
        # Mock the response from the search tool
        mock_invoke.return_value = type('', (), {'content': "Python programming\nBest practices\nCode readability"})()

        state = {"query": "Python programming best practices", "search_results": [], "markdown_result": ""}
        result = perform_search(state)
        
        # Verify the search results are populated
        expected_results = ["Python programming", "Best practices", "Code readability"]
        self.assertEqual(result['search_results'], expected_results)

    @patch('react_agent_module.llm_tool.invoke')
    def test_filter_results(self, mock_invoke):
        # Mock the response from the filter tool
        mock_invoke.return_value = type('', (), {'content': "Best practices"})()

        state = {"query": "", "search_results": ["Python programming", "Best practices", "Code readability"], "markdown_result": ""}
        result = filter_results(state)
        
        # Verify only relevant results are kept
        expected_results = ["Best practices"]
        self.assertEqual(result['search_results'], expected_results)

    @patch('react_agent_module.llm_tool.invoke')
    def test_compile_markdown(self, mock_invoke):
        # Mock the response for the compiled Markdown document
        mock_invoke.return_value = type('', (), {'content': "# Python Best Practices\n\n- Code readability"})()

        state = {"query": "", "search_results": ["Best practices"], "markdown_result": ""}
        result = compile_markdown(state)
        
        # Verify the Markdown document is correctly compiled
        expected_markdown = "# Python Best Practices\n\n- Code readability"
        self.assertEqual(result['markdown_result'], expected_markdown)

if __name__ == '__main__':
    unittest.main()
