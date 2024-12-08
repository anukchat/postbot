# AI Hedge Fund

An AI-powered hedge fund that uses multiple agents to make trading decisions. The system employs several specialized agents working together:

  1. Market Data Agent - Gathers and preprocesses market data
  2. Quantitative Agent - Analyzes technical indicators and generates trading signals
  3. Fundamentals Agent - Analyzes fundamental data and generates trading signals
  4. Sentiment Agent - Analyzes market sentiment and generates trading signals
  5. Risk Management Agent - Evaluates portfolio risk and sets position limits
  6. Portfolio Management Agent - Makes final trading decisions and generates orders



## Disclaimer

This project is for **educational and research purposes only**.

  * Not intended for real trading or investment
  * No warranties or guarantees provided
  * Past performance does not indicate future results
  * Creator assumes no liability for financial losses
  * Consult a financial advisor for investment decisions



By using this software, you agree to use it solely for learning purposes.

## Table of Contents

  * Features
  * Setup
  * Usage
    * Running the Hedge Fund
    * Running the Hedge Fund (with Reasoning)
    * Running the Backtester
  * Project Structure
  * Contributing
  * License



## Features

  * Multi-agent architecture for trading decisions
  * Technical analysis using MACD, RSI, Bollinger Bands, and OBV
  * Fundamental analysis using financial metrics
  * Sentiment analysis using web search
  * Risk management with position sizing recommendations
  * Portfolio management with automated trading decisions
  * Backtesting capabilities with performance analytics



## Setup

Clone the repository:
    
    
    git clone https://github.com/your-repo/ai-hedge-fund.git
    cd ai-hedge-fund

  1. Install Poetry (if not already installed):


    
    
    curl -sSL https://install.python-poetry.org | python3 -

  2. Install dependencies:


    
    
    poetry install

  3. Set up your environment variables:


    
    
    # Create .env file for your API keys
    cp .env.example .env
    
    export OPENAI_API_KEY='your-api-key-here' # For using LLM
    export FINANCIAL_DATASETS_API_KEY='your-api-key-here' # For fetching stock market data
    export TAVILY_API_KEY='your-api-key-here' # For web search

## Usage

### Running the Hedge Fund
    
    
    poetry run python src/agents.py --ticker AAPL

You can optionally specify the start and end dates to make decisions for a specific time period.
    
    
    poetry run python src/agents.py --ticker AAPL --start-date 2024-01-01 --end-date 2024-03-01

### Running the Hedge Fund (with Reasoning)

This will print the reasoning of each agent to the console.
    
    
    poetry run python src/agents.py --ticker AAPL --show-reasoning

### Running the Backtester
    
    
    poetry run python src/backtester.py --ticker AAPL

**Example Output:**
    
    
    Starting backtest...
    Date         Ticker Action Quantity    Price         Cash    Stock  Total Value
    ----------------------------------------------------------------------
    2024-01-01   AAPL   buy       519.0   192.53        76.93    519.0    100000.00
    2024-01-02   AAPL   hold          0   185.64        76.93    519.0     96424.09
    2024-01-03   AAPL   hold          0   184.25        76.93    519.0     95702.68
    2024-01-04   AAPL   hold          0   181.91        76.93    519.0     94488.22
    2024-01-05   AAPL   hold          0   181.18        76.93    519.0     94109.35
    2024-01-08   AAPL   sell        519   185.56     96382.57      0.0     96382.57
    2024-01-09   AAPL   buy       520.0   185.14       109.77    520.0     96382.57
    

You can optionally specify the start and end dates to backtest over a specific time period.
    
    
    poetry run python src/backtester.py --ticker AAPL --start-date 2024-01-01 --end-date 2024-03-01

## Project Structure
    
    
    ai-hedge-fund/
    ├── src/
    │   ├── agents.py # Main agent definitions and workflow
    │   ├── backtester.py # Backtesting functionality
    │   ├── tools.py # Agent tools
    ├── pyproject.toml # Poetry configuration
    ├── .env.example # Environment variables
    └── README.md # Documentation
    

## Contributing

  1. Fork the repository
  2. Create a feature branch
  3. Commit your changes
  4. Push to the branch
  5. Create a Pull Request



## License

This project is licensed under the MIT License - see the LICENSE file for details.
