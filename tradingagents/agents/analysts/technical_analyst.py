from copy import deepcopy
from typing import Any

from langchain_core.prompts import ChatPromptTemplate

from tradingagents.agents.schemas import MarketPrediction
from tradingagents.agents.utils.agent_utils import get_technical_analysis
from tradingagents.agents.utils.structured import bind_structured


def create_technical_analyst(llm: Any, ticker_symbol: str):
    structured_llm = bind_structured(llm, MarketPrediction, "Technical Analyst")

    system_message = """
    You are an expert quantitative trading agent specialized in technical analysis.
    Your job is to review numerical technical indicators computed from OHLCV market
    data and output a technical trading recommendation.

    Your entire response must consist of a single MarketPrediction object matching
    the provided schema.

    Rules:
    1. Base your prediction strictly on the technical analysis data returned by the
       tool.
    2. If the RSI is above 70, factor in overbought conditions. If the RSI is below
       30, factor in oversold conditions.
    3. Look for moving average crossovers, such as by comparing current price to the
       20-candle and 50-candle simple moving average.
    4. Do not hallucinate or assume sentiment outside the provided numerical context.
    """

    prompt = ChatPromptTemplate.from_messages([("system", system_message),
                                               ("human", """
                                                Analyze the technical analysis profile for {ticker} using only the provided tool
                                                output.

                                                The tool provides the following indicators:
                                                - Current price
                                                - 20-candle simple moving average (SMA20)
                                                - 50-candle simple moving average (SMA50)
                                                - 14-candle RSI
                                                - MACD line
                                                - MACD signal line
                                                - Most recent price trend

                                                Based on these indicators, determine the appropriate signal: BUY, SELL, or HOLD.

                                                Guidance:
                                                - Recommend BUY when most indicators are bullish and there is no major bearish
                                                contradiction.
                                                - Recommend SELL when most indicators are bearish and there is no major bullish
                                                contradiction.
                                                - Recommend HOLD when indicators are mixed, neutral, or conflicting.

                                                In your rationale, briefly explain which indicator values support the decision.
                                                Assign a confidence score from 0.0 to 1.0 based on how strongly the indicators
                                                agree. Increase confidence when multiple indicators align in the same direction;
                                                decrease confidence when the indicators are mixed, neutral, or conflicting.
                                                """)])

    formatted_messages = prompt.format_messages(ticker = ticker_symbol)

    # Fetch technical analysis profile from the tool
    technical_analysis = get_technical_analysis.invoke({"ticker": ticker_symbol})

    # Append the tool output to the list of messages
    full_llm_input = formatted_messages + [("human",
                                            f"Use the following technical analysis data.\n{technical_analysis}")]

    # Obtain and return the structured prediction
    result = structured_llm.invoke(full_llm_input)
    return result

def run_technical_analysis_agent(ticker_symbol: str):
    from tradingagents.default_config import DEFAULT_CONFIG
    from tradingagents.llm_clients import create_llm_client

    config = deepcopy(DEFAULT_CONFIG)

    quick_client = create_llm_client(provider = config["llm_provider"],
                                     model = config["quick_think_llm"])
    quick_thinking_llm = quick_client.get_llm()

    return create_technical_analyst(quick_thinking_llm, ticker_symbol)

if __name__ == "__main__":
    from cli.utils import get_ticker

    ticker_symbol = get_ticker()
    result = run_technical_analysis_agent(ticker_symbol)

    print(result.model_dump_json(indent = 2))
