# Import necessary libraries
import streamlit as st
import os
from crewai import Agent, Task, Crew, Process  # Ensure Process is imported
from utils import get_openai_api_key, get_serper_api_key  # Import utility functions
from crewai_tools import ScrapeWebsiteTool, SerperDevTool  # Import specific tools
from langchain_openai import ChatOpenAI  # Import the language model interface
from dotenv import load_dotenv, find_dotenv  # Import environment management tools

# Streamlit app title
st.title("Financial Trading Crew Application")

# Load environment variables from a .env file
load_dotenv(find_dotenv())

# Fetch API keys using utility functions
openai_api_key = get_openai_api_key()
os.environ["OPENAI_MODEL_NAME"] = 'gpt-3.5-turbo'
os.environ["SERPER_API_KEY"] = get_serper_api_key()

# Define tools for the agents
search_tool = SerperDevTool()  # Tool for searching data
scrape_tool = ScrapeWebsiteTool()  # Tool for scraping websites

# Define the Data Analyst agent
data_analyst_agent = Agent(
    role="Data Analyst",
    goal="Monitor and analyze market data in real-time to identify trends and predict market movements.",
    backstory="""Specializing in financial markets, this agent uses statistical modeling and machine learning 
                 to provide crucial insights. With a knack for data, the Data Analyst Agent is the cornerstone 
                 for informing trading decisions.""",
    verbose=True,
    allow_delegation=True,
    tools=[scrape_tool, search_tool]  # Assign tools to the agent
)

# Define the Trading Strategy Developer agent
trading_strategy_agent = Agent(
    role="Trading Strategy Developer",
    goal="Develop and test various trading strategies based on insights from the Data Analyst Agent.",
    backstory="""Equipped with a deep understanding of financial markets and quantitative analysis,
                 this agent devises and refines trading strategies. It evaluates the performance of 
                 different approaches to determine the most profitable and risk-averse options.""",
    verbose=True,
    allow_delegation=True,
    tools=[scrape_tool, search_tool]
)

# Define the Trade Advisor agent
execution_agent = Agent(
    role="Trade Advisor",
    goal="Suggest optimal trade execution strategies based on approved trading strategies.",
    backstory="""This agent specializes in analyzing the timing, price, and logistical details
                 of potential trades. By evaluating these factors, it provides well-founded suggestions 
                 for when and how trades should be executed to maximize efficiency and adherence to strategy.""",
    verbose=True,
    allow_delegation=True,
    tools=[scrape_tool, search_tool]
)

# Define the Risk Advisor agent
risk_management_agent = Agent(
    role="Risk Advisor",
    goal="Evaluate and provide insights on the risks associated with potential trading activities.",
    backstory="""Armed with a deep understanding of risk assessment models and market dynamics, 
                 this agent scrutinizes the potential risks of proposed trades. It offers a detailed 
                 analysis of risk exposure and suggests safeguards to ensure that trading activities 
                 align with the firm’s risk tolerance.""",
    verbose=True,
    allow_delegation=True,
    tools=[scrape_tool, search_tool]
)

# Define the task for analyzing market data
data_analysis_task = Task(
    description="""Continuously monitor and analyze market data for the selected stock ({stock_selection}). 
                   Use statistical modeling and machine learning to identify trends and predict 
                   market movements.""",
    expected_output="Insights and alerts about significant market opportunities or threats for {stock_selection}.",
    agent=data_analyst_agent,
)

# Define the task for developing trading strategies
strategy_development_task = Task(
    description="""Develop and refine trading strategies based on the insights from 
                   the Data Analyst and user-defined risk tolerance ({risk_tolerance}). Consider
                   trading preferences ({trading_strategy_preference}).""",
    expected_output="""A set of potential trading strategies for {stock_selection} that align
                       with the user's risk tolerance.""",
    agent=trading_strategy_agent,
)

# Define the task for planning trade execution
execution_planning_task = Task(
    description="""Analyze approved trading strategies to determine the best execution methods 
                   for {stock_selection}, considering current market conditions and optimal pricing.""",
    expected_output="Detailed execution plans suggesting how and when to execute trades for {stock_selection}.",
    agent=execution_agent,
)

# Define the task for assessing trading risks
risk_assessment_task = Task(
    description="""Evaluate the risks associated with the proposed trading strategies and execution 
                   plans for {stock_selection}. Provide a detailed analysis of potential risks and 
                   suggest mitigation strategies.""",
    expected_output="""A comprehensive risk analysis report detailing potential risks and mitigation 
                       recommendations for {stock_selection}.""",
    agent=risk_management_agent,
)

# Create the financial trading crew
financial_trading_crew = Crew(
    agents=[data_analyst_agent, trading_strategy_agent, execution_agent, risk_management_agent],
    tasks=[data_analysis_task, strategy_development_task, execution_planning_task, risk_assessment_task],
    manager_llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7),  # Specify the language model to manage the crew
    process=Process.hierarchical,  # Set the process type
    verbose=True  # Enable detailed output
)

# Streamlit UI for inputs
st.subheader("Set Parameters for Trading Crew")

# Input fields for the user to specify parameters
stock_selection = st.text_input("Stock Selection", "MSFT")  # Default stock is MSFT
initial_capital = st.number_input("Initial Capital", value=100000, step=1000)  # Default initial capital
risk_tolerance = st.selectbox("Risk Tolerance", ["Low", "Medium", "High"])  # User selects risk tolerance level
trading_strategy_preference = st.selectbox("Trading Strategy Preference", ["Day Trading", "Swing Trading", "Long-term Investment"])  # User selects trading strategy
news_impact_consideration = st.checkbox("Consider News Impact", value=True)  # Option to consider news impact

# Function to run the crew and display the result
def run_trading_crew():
    """
    Executes the financial trading crew with the provided inputs and returns the result.
    Returns:
        result (str): The output of the trading crew execution.
    """
    financial_trading_inputs = {
        'stock_selection': stock_selection,
        'initial_capital': str(initial_capital),
        'risk_tolerance': risk_tolerance,
        'trading_strategy_preference': trading_strategy_preference,
        'news_impact_consideration': news_impact_consideration
    }

    # Run the trading crew and handle any errors
    with st.spinner('Running trading crew... This may take a few minutes.'):
        try:
            result = financial_trading_crew.kickoff(inputs=financial_trading_inputs)
            return result
        except Exception as e:
            st.error(f"An error occurred: {e}")
            return None

# Execution button to run the trading crew
if st.button("Run Trading Crew"):
    result = run_trading_crew()
    if result:
        st.subheader("Trading Crew Results")
        st.markdown(result)
    else:
        st.error("Failed to retrieve results. Please check your input and try again.")
