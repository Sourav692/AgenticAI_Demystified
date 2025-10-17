# Multi-Agent EDA System with AutoGen Framework
# Author: Sourav Banerjee
# Date: 2025-06-01

import autogen
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import io
import base64
from typing import Dict, List, Any, Optional
import json
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import scipy.stats as stats
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

class EDAMultiAgentSystem:
    """
    Multi-Agent EDA System using AutoGen Framework

    This class orchestrates a collaborative EDA process using specialized agents
    that work together to perform comprehensive data analysis.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Multi-Agent EDA System

        Args:
            config_path: Path to AutoGen configuration file
        """
        self.config_path = config_path
        self.data = None
        self.analysis_results = {}
        self.report_content = ""
        self.agents = {}

        # Initialize AutoGen configuration
        self._setup_autogen_config()

        # Create specialized agents
        self._create_agents()

        # Setup group chat
        self._setup_group_chat()

    def _setup_autogen_config(self):
        """Setup AutoGen configuration"""
        if self.config_path and os.path.exists(self.config_path):
            self.config_list = autogen.config_list_from_json(self.config_path)
        else:
            # Default configuration - you'll need to update with your API keys
            self.config_list = [
                {
                    "model": "gpt-4",
                    "api_key": "your-openai-api-key-here",  # Replace with your API key
                }
            ]

        self.llm_config = {
            "config_list": self.config_list,
            "temperature": 0.1,
            "timeout": 120,
        }

    def _create_agents(self):
        """Create specialized agents for EDA tasks"""

        # Data Preparation Agent
        self.agents['data_prep'] = autogen.AssistantAgent(
            name="DataPrepAgent",
            system_message="""You are a Data Preparation specialist responsible for data cleaning and preprocessing.
            Your tasks include:
            - Analyzing data quality and structure
            - Identifying missing values, outliers, and inconsistencies
            - Performing data cleaning operations
            - Preparing data for analysis
            - Providing detailed reports on data preparation steps

            Always provide Python code that can be executed and explain your reasoning.
            Focus on data integrity and quality.""",
            llm_config=self.llm_config,
        )

        # EDA Agent
        self.agents['eda'] = autogen.AssistantAgent(
            name="EDAAgent",
            system_message="""You are an Exploratory Data Analysis specialist.
            Your responsibilities include:
            - Conducting comprehensive statistical analysis
            - Creating meaningful visualizations
            - Identifying patterns, trends, and relationships
            - Generating insights from data
            - Performing correlation analysis and feature analysis

            Use appropriate statistical methods and create clear, informative visualizations.
            Provide actionable insights based on your analysis.""",
            llm_config=self.llm_config,
        )

        # Report Generator Agent
        self.agents['report'] = autogen.AssistantAgent(
            name="ReportGeneratorAgent",
            system_message="""You are a Report Generation specialist responsible for creating comprehensive EDA reports.
            Your tasks include:
            - Compiling analysis results into structured reports
            - Creating executive summaries
            - Organizing findings in a logical flow
            - Ensuring clarity and professional presentation
            - Including key visualizations and insights

            Create well-structured, professional reports that communicate findings effectively.""",
            llm_config=self.llm_config,
        )

        # Critic Agent
        self.agents['critic'] = autogen.AssistantAgent(
            name="CriticAgent",
            system_message="""You are a Quality Assurance specialist who reviews and critiques analysis outputs.
            Your responsibilities include:
            - Reviewing code for correctness and efficiency
            - Validating statistical methods and interpretations
            - Checking visualization quality and appropriateness
            - Providing constructive feedback for improvements
            - Ensuring analysis completeness and accuracy

            Be thorough in your reviews and provide specific, actionable feedback.""",
            llm_config=self.llm_config,
        )

        # Executor Agent
        self.agents['executor'] = autogen.UserProxyAgent(
            name="ExecutorAgent",
            system_message="""You are responsible for executing code and validating results.
            Execute Python code provided by other agents and report results accurately.
            Ensure all code runs successfully and produces expected outputs.""",
            code_execution_config={
                "work_dir": "eda_workspace",
                "use_docker": False,
            },
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
        )

        # Admin Agent
        self.agents['admin'] = autogen.AssistantAgent(
            name="AdminAgent",
            system_message="""You are the workflow coordinator and project manager.
            Your responsibilities include:
            - Orchestrating the overall EDA workflow
            - Ensuring all agents complete their tasks
            - Maintaining project alignment with goals
            - Coordinating communication between agents
            - Making final decisions on analysis direction

            Keep the team focused and ensure deliverables meet requirements.""",
            llm_config=self.llm_config,
        )

    def _setup_group_chat(self):
        """Setup group chat for agent collaboration"""
        self.group_chat = autogen.GroupChat(
            agents=list(self.agents.values()),
            messages=[],
            max_round=50,
            speaker_selection_method="round_robin"
        )

        self.manager = autogen.GroupChatManager(
            groupchat=self.group_chat,
            llm_config=self.llm_config
        )

    def load_data(self, data_source: str, **kwargs) -> pd.DataFrame:
        """
        Load data from various sources

        Args:
            data_source: Path to data file or data source identifier
            **kwargs: Additional parameters for data loading

        Returns:
            Loaded DataFrame
        """
        try:
            if data_source.endswith('.csv'):
                self.data = pd.read_csv(data_source, **kwargs)
            elif data_source.endswith('.xlsx') or data_source.endswith('.xls'):
                self.data = pd.read_excel(data_source, **kwargs)
            elif data_source.endswith('.json'):
                self.data = pd.read_json(data_source, **kwargs)
            elif data_source.endswith('.parquet'):
                self.data = pd.read_parquet(data_source, **kwargs)
            else:
                raise ValueError(f"Unsupported file format: {data_source}")

            logger.info(f"Data loaded successfully. Shape: {self.data.shape}")
            return self.data

        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    def run_eda_workflow(self, data_description: str = "") -> Dict[str, Any]:
        """
        Execute the complete EDA workflow using multi-agent collaboration

        Args:
            data_description: Description of the dataset and analysis objectives

        Returns:
            Dictionary containing analysis results and reports
        """
        if self.data is None:
            raise ValueError("No data loaded. Please load data first using load_data()")

        # Prepare initial context
        data_info = {
            "shape": self.data.shape,
            "columns": list(self.data.columns),
            "dtypes": self.data.dtypes.to_dict(),
            "description": data_description
        }

        # Start the collaborative EDA process
        initial_message = f"""
        We need to perform a comprehensive Exploratory Data Analysis on the following dataset:

        Dataset Information:
        - Shape: {data_info['shape']}
        - Columns: {data_info['columns']}
        - Data Types: {data_info['dtypes']}
        - Description: {data_description}

        Please coordinate to complete the following tasks:
        1. Data preparation and cleaning
        2. Statistical analysis and visualization
        3. Generate comprehensive EDA report
        4. Review and validate all outputs

        Let's begin with data preparation.
        """

        # Initiate the group chat
        self.agents['admin'].initiate_chat(
            self.manager,
            message=initial_message
        )

        return self.analysis_results

    def generate_sample_data(self, dataset_type: str = "sales") -> pd.DataFrame:
        """
        Generate sample data for demonstration purposes

        Args:
            dataset_type: Type of sample dataset to generate

        Returns:
            Generated sample DataFrame
        """
        np.random.seed(42)

        if dataset_type == "sales":
            n_samples = 1000

            # Generate sales data
            dates = pd.date_range('2023-01-01', periods=n_samples, freq='D')
            products = ['Product_A', 'Product_B', 'Product_C', 'Product_D', 'Product_E']
            regions = ['North', 'South', 'East', 'West', 'Central']

            data = {
                'Date': np.random.choice(dates, n_samples),
                'Product': np.random.choice(products, n_samples),
                'Region': np.random.choice(regions, n_samples),
                'Sales_Amount': np.random.exponential(1000, n_samples) + np.random.normal(500, 200, n_samples),
                'Quantity': np.random.poisson(10, n_samples) + 1,
                'Customer_Age': np.random.normal(35, 12, n_samples).astype(int),
                'Customer_Satisfaction': np.random.uniform(1, 5, n_samples),
                'Marketing_Spend': np.random.exponential(200, n_samples),
                'Seasonality_Factor': np.sin(np.arange(n_samples) * 2 * np.pi / 365) + 1
            }

            # Add some missing values
            missing_indices = np.random.choice(n_samples, size=int(0.05 * n_samples), replace=False)
            data['Customer_Satisfaction'][missing_indices] = np.nan

            # Add some outliers
            outlier_indices = np.random.choice(n_samples, size=int(0.02 * n_samples), replace=False)
            data['Sales_Amount'][outlier_indices] *= 5

        elif dataset_type == "customer":
            n_samples = 800

            data = {
                'Customer_ID': range(1, n_samples + 1),
                'Age': np.random.normal(40, 15, n_samples).astype(int),
                'Income': np.random.lognormal(10, 0.5, n_samples),
                'Education_Level': np.random.choice(['High School', 'Bachelor', 'Master', 'PhD'], n_samples),
                'Years_Customer': np.random.exponential(3, n_samples),
                'Total_Purchases': np.random.poisson(15, n_samples),
                'Average_Order_Value': np.random.gamma(2, 50, n_samples),
                'Churn_Risk': np.random.uniform(0, 1, n_samples),
                'Satisfaction_Score': np.random.beta(2, 1, n_samples) * 5
            }

        else:
            raise ValueError(f"Unsupported dataset type: {dataset_type}")

        self.data = pd.DataFrame(data)
        logger.info(f"Sample {dataset_type} dataset generated. Shape: {self.data.shape}")

        return self.data

# # Utility functions for EDA
# class EDAUtilities:
#     """Utility functions for EDA operations"""

#     @staticmethod
#     def data_overview(df: pd.DataFrame) -> Dict[str, Any]:
#         """Generate comprehensive data overview"""
#         overview = {
#             'shape': df.shape,
#             'columns': list(df.columns),
#             'dtypes': df.dtypes.to_dict(),
#             'missing_values': df.isnull().sum().to_dict(),
#             'missing_percentage': (df.isnull().sum() / len(df) * 100).to_dict(),
#             'memory_usage': df.memory_usage(deep=True).to_dict(),
#             'duplicate_rows': df.duplicated().sum()
#         }
#         return overview

#     @staticmethod
#     def statistical_summary(df: pd.DataFrame) -> Dict[str, Any]:
#         """Generate statistical summary for numerical columns"""
#         numerical_cols = df.select_dtypes(include=[np.number]).columns
#         categorical_cols = df.select_dtypes(include=['object', 'category']).columns

#         summary = {
#             'numerical_summary': df[numerical_cols].describe().to_dict() if len(numerical_cols) > 0 else {},
#             'categorical_summary': {col: df[col].value_counts().to_dict() for col in categorical_cols},
#             'correlation_matrix': df[numerical_cols].corr().to_dict() if len(numerical_cols) > 1 else {}
#         }
#         return summary

#     @staticmethod
#     def detect_outliers(df: pd.DataFrame, method: str = 'iqr') -> Dict[str, List]:
#         """Detect outliers in numerical columns"""
#         numerical_cols = df.select_dtypes(include=[np.number]).columns
#         outliers = {}

#         for col in numerical_cols:
#             if method == 'iqr':
#                 Q1 = df[col].quantile(0.25)
#                 Q3 = df[col].quantile(0.75)
#                 IQR = Q3 - Q1
#                 lower_bound = Q1 - 1.5 * IQR
#                 upper_bound = Q3 + 1.5 * IQR
#                 outlier_indices = df[(df[col] < lower_bound) | (df[col] > upper_bound)].index.tolist()
#             elif method == 'zscore':
#                 z_scores = np.abs(stats.zscore(df[col].dropna()))
#                 outlier_indices = df[z_scores > 3].index.tolist()

#             outliers[col] = outlier_indices

#         return outliers

# # Example usage and demonstration
# def demonstrate_eda_system():
#     """Demonstrate the Multi-Agent EDA System"""

#     print("🚀 **Multi-Agent EDA System Demonstration**")
#     print("=" * 60)

#     # Initialize the system
#     eda_system = EDAMultiAgentSystem()

#     # Generate sample data
#     print("\n📊 **Generating Sample Sales Dataset...**")
#     sample_data = eda_system.generate_sample_data("sales")
#     print(f"Generated dataset with shape: {sample_data.shape}")
#     print(f"Columns: {list(sample_data.columns)}")

#     # Display basic information
#     print("\n🔍 **Basic Data Overview:**")
#     overview = EDAUtilities.data_overview(sample_data)
#     print(f"Shape: {overview['shape']}")
#     print(f"Missing values: {sum(overview['missing_values'].values())}")
#     print(f"Duplicate rows: {overview['duplicate_rows']}")

#     # Run basic statistical analysis
#     print("\n📈 **Statistical Summary:**")
#     stats_summary = EDAUtilities.statistical_summary(sample_data)
#     print("Numerical columns statistical summary available")
#     print(f"Categorical columns: {len(stats_summary['categorical_summary'])}")

#     # Note: The actual multi-agent workflow would require valid API keys
#     print("\n⚠️  **Note:** To run the full multi-agent workflow, please:")
#     print("1. Set up your OpenAI API key in the configuration")
#     print("2. Run: eda_system.run_eda_workflow('Sales data analysis for business insights')")

#     return eda_system, sample_data

# # Advanced EDA Components
# class AdvancedEDAComponents:
#     """Advanced EDA components for comprehensive analysis"""

#     @staticmethod
#     def create_correlation_heatmap(df: pd.DataFrame, figsize: tuple = (12, 8)) -> None:
#         """Create correlation heatmap for numerical variables"""
#         numerical_cols = df.select_dtypes(include=[np.number]).columns
#         if len(numerical_cols) > 1:
#             plt.figure(figsize=figsize)
#             correlation_matrix = df[numerical_cols].corr()
#             sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
#                        square=True, linewidths=0.5)
#             plt.title('Correlation Heatmap of Numerical Variables')
#             plt.tight_layout()
#             plt.show()

#     @staticmethod
#     def create_distribution_plots(df: pd.DataFrame, numerical_cols: List[str] = None) -> None:
#         """Create distribution plots for numerical variables"""
#         if numerical_cols is None:
#             numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()

#         n_cols = min(3, len(numerical_cols))
#         n_rows = (len(numerical_cols) + n_cols - 1) // n_cols

#         fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))
#         axes = axes.flatten() if n_rows > 1 else [axes] if n_rows == 1 else axes

#         for i, col in enumerate(numerical_cols):
#             if i < len(axes):
#                 sns.histplot(data=df, x=col, kde=True, ax=axes[i])
#                 axes[i].set_title(f'Distribution of {col}')

#         # Hide unused subplots
#         for i in range(len(numerical_cols), len(axes)):
#             axes[i].set_visible(False)

#         plt.tight_layout()
#         plt.show()

#     @staticmethod
#     def create_categorical_plots(df: pd.DataFrame, categorical_cols: List[str] = None) -> None:
#         """Create plots for categorical variables"""
#         if categorical_cols is None:
#             categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

#         for col in categorical_cols[:4]:  # Limit to first 4 categorical columns
#             plt.figure(figsize=(10, 6))
#             value_counts = df[col].value_counts()

#             if len(value_counts) <= 10:
#                 sns.countplot(data=df, x=col)
#                 plt.xticks(rotation=45)
#             else:
#                 # Show top 10 categories for variables with many categories
#                 top_categories = value_counts.head(10)
#                 plt.bar(range(len(top_categories)), top_categories.values)
#                 plt.xticks(range(len(top_categories)), top_categories.index, rotation=45)

#             plt.title(f'Distribution of {col}')
#             plt.tight_layout()
#             plt.show()

# # Configuration template
# CONFIG_TEMPLATE = '''
# {
#     "model": "gpt-4",
#     "api_key": "your-openai-api-key-here"
# }
# '''

# def main():
#     """Main function to run the EDA system demonstration"""
#     try:
#         # Run demonstration
#         eda_system, sample_data = demonstrate_eda_system()

#         # Create some visualizations
#         print("\n📊 **Creating Visualizations...**")
#         advanced_eda = AdvancedEDAComponents()

#         # Correlation heatmap
#         advanced_eda.create_correlation_heatmap(sample_data)

#         # Distribution plots
#         numerical_cols = ['Sales_Amount', 'Quantity', 'Customer_Age', 'Marketing_Spend']
#         advanced_eda.create_distribution_plots(sample_data, numerical_cols)

#         # Categorical plots
#         categorical_cols = ['Product', 'Region']
#         advanced_eda.create_categorical_plots(sample_data, categorical_cols)

#         print("\n✅ **EDA System demonstration completed successfully!**")

#         return eda_system, sample_data

#     except Exception as e:
#         logger.error(f"Error in main execution: {str(e)}")
#         raise

# if __name__ == "__main__":
#     # Run the demonstration
#     system, data = main()

# Standalone Data Generator Function
# def generate_and_save_sample_data(dataset_type: str = "sales", output_dir: str = "data", n_samples: int = None) -> str:
#     """
#     Generate sample data and save it to CSV file

#     Args:
#         dataset_type: Type of sample dataset to generate ("sales" or "customer")
#         output_dir: Directory to save the CSV file
#         n_samples: Number of samples to generate (optional)

#     Returns:
#         Path to the saved CSV file
#     """
#     # Create output directory if it doesn't exist
#     os.makedirs(output_dir, exist_ok=True)

#     # Set random seed for reproducibility
#     np.random.seed(42)

#     if dataset_type == "sales":
#         n_samples = n_samples or 1000

#         print(f"🏪 Generating {n_samples} sales records...")

#         # Generate sales data
#         dates = pd.date_range('2023-01-01', periods=n_samples, freq='D')
#         products = ['Product_A', 'Product_B', 'Product_C', 'Product_D', 'Product_E']
#         regions = ['North', 'South', 'East', 'West', 'Central']

#         data = {
#             'Date': np.random.choice(dates, n_samples),
#             'Product': np.random.choice(products, n_samples),
#             'Region': np.random.choice(regions, n_samples),
#             'Sales_Amount': np.random.exponential(1000, n_samples) + np.random.normal(500, 200, n_samples),
#             'Quantity': np.random.poisson(10, n_samples) + 1,
#             'Customer_Age': np.random.normal(35, 12, n_samples).astype(int),
#             'Customer_Satisfaction': np.random.uniform(1, 5, n_samples),
#             'Marketing_Spend': np.random.exponential(200, n_samples),
#             'Seasonality_Factor': np.sin(np.arange(n_samples) * 2 * np.pi / 365) + 1
#         }

#         # Add some missing values (5% of Customer_Satisfaction)
#         missing_indices = np.random.choice(n_samples, size=int(0.05 * n_samples), replace=False)
#         data['Customer_Satisfaction'][missing_indices] = np.nan

#         # Add some outliers (2% of Sales_Amount)
#         outlier_indices = np.random.choice(n_samples, size=int(0.02 * n_samples), replace=False)
#         data['Sales_Amount'][outlier_indices] *= 5

#         filename = f"sales_data_{n_samples}_records.csv"

#     elif dataset_type == "customer":
#         n_samples = n_samples or 800

#         print(f"👥 Generating {n_samples} customer records...")

#         data = {
#             'Customer_ID': range(1, n_samples + 1),
#             'Age': np.random.normal(40, 15, n_samples).astype(int),
#             'Income': np.random.lognormal(10, 0.5, n_samples),
#             'Education_Level': np.random.choice(['High School', 'Bachelor', 'Master', 'PhD'], n_samples),
#             'Years_Customer': np.random.exponential(3, n_samples),
#             'Total_Purchases': np.random.poisson(15, n_samples),
#             'Average_Order_Value': np.random.gamma(2, 50, n_samples),
#             'Churn_Risk': np.random.uniform(0, 1, n_samples),
#             'Satisfaction_Score': np.random.beta(2, 1, n_samples) * 5
#         }

#         filename = f"customer_data_{n_samples}_records.csv"

#     else:
#         raise ValueError(f"Unsupported dataset type: {dataset_type}. Use 'sales' or 'customer'.")

#     # Create DataFrame
#     df = pd.DataFrame(data)

#     # Save to CSV
#     output_path = os.path.join(output_dir, filename)
#     df.to_csv(output_path, index=False)

#     # Display summary information
#     print(f"✅ Dataset generated successfully!")
#     print(f"📁 Saved to: {output_path}")
#     print(f"📊 Shape: {df.shape}")
#     print(f"📋 Columns: {list(df.columns)}")

#     # Display basic statistics
#     print(f"\n📈 Basic Statistics:")
#     print(f"   • Missing values: {df.isnull().sum().sum()}")
#     print(f"   • Duplicate rows: {df.duplicated().sum()}")

#     if dataset_type == "sales":
#         print(f"   • Date range: {df['Date'].min()} to {df['Date'].max()}")
#         print(f"   • Products: {df['Product'].nunique()} unique")
#         print(f"   • Regions: {df['Region'].nunique()} unique")
#         print(f"   • Avg Sales Amount: ${df['Sales_Amount'].mean():.2f}")
#     elif dataset_type == "customer":
#         print(f"   • Age range: {df['Age'].min()} to {df['Age'].max()}")
#         print(f"   • Avg Income: ${df['Income'].mean():.2f}")
#         print(f"   • Education levels: {df['Education_Level'].nunique()} unique")

#     return output_path

# def generate_all_sample_datasets(output_dir: str = "data"):
#     """
#     Generate both sales and customer sample datasets

#     Args:
#         output_dir: Directory to save the CSV files

#     Returns:
#         List of paths to saved CSV files
#     """
#     print("🚀 **Sample Data Generator**")
#     print("=" * 50)

#     saved_files = []

#     # Generate sales dataset
#     print("\n1️⃣ Generating Sales Dataset...")
#     sales_path = generate_and_save_sample_data("sales", output_dir, 1000)
#     saved_files.append(sales_path)

#     print("\n" + "-" * 50)

#     # Generate customer dataset
#     print("\n2️⃣ Generating Customer Dataset...")
#     customer_path = generate_and_save_sample_data("customer", output_dir, 800)
#     saved_files.append(customer_path)

#     print("\n" + "=" * 50)
#     print("🎉 **All datasets generated successfully!**")
#     print(f"📂 Files saved in: {output_dir}/")
#     for file_path in saved_files:
#         print(f"   • {os.path.basename(file_path)}")

#     return saved_files

# if __name__ == "__main__":
#     # Generate all sample datasets
#     generate_all_sample_datasets()
