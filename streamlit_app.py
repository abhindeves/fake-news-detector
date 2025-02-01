#!/usr/bin/env python3
import os
import re
import asyncio
import logging
from dotenv import find_dotenv, load_dotenv
import google.generativeai as genai
from tavily import AsyncTavilyClient
from typing import List, Dict, Any, Tuple
import streamlit as st

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load environment variables
load_dotenv(find_dotenv())

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
TAVILY_API_KEY = os.environ["TAVILY_API_KEY"] = st.secrets["TAVILY_API_KEY"]

# Configure generative AI model
genai.configure(api_key=GEMINI_API_KEY)
SYSTEM_INSTRUCTION = (
    "You are an AI assistant designed to analyze the validity of news. "
    "Your responses should be concise, formatted as bullet points, and avoid "
    "any additional commentary. Maintain a neutral and objective tone, ensuring "
    "that each assumption is framed as a question that can be directly queried online."
)

# Initialize the generative AI model for generating assumptions
model = genai.GenerativeModel(
    "gemini-1.5-flash", system_instruction=SYSTEM_INSTRUCTION
)

# Instantiate the Tavily client for search results
tavily_client = AsyncTavilyClient(api_key=TAVILY_API_KEY)


def create_template(user_input: str) -> str:
    """Creates the prompt template with the dynamic user input."""
    return f"""Here is a statement:
{user_input}
Make a bullet point list of the assumptions you made when given the above statement.
These assumptions will then be used to check online for the validity of the statement.
Only Give Bullet Points, No Other Text

Example:

Input:
deepseek company is owned by elon musk

Output:
* Does elon musk own deepseek?
* Does Elon Musk have any publicly known business interests or holdings that could include a company named "Deepseek"?
* Are there any news articles, press releases, or official statements confirming Elon Musk's ownership of "Deepseek"?
* Do any financial databases or corporate registries list Elon Musk as an owner or shareholder of "Deepseek"?
"""


async def generate_assertions(user_input: str) -> List[str]:
    """Generates assertions from the user input using the Gemini model."""
    with st.spinner("Identifying key assumptions for verification..."):
        template = create_template(user_input)
        try:
            response = await model.generate_content_async(template)
            assertions = response.text.strip()
            assertions_list: List[str] = [
                line.strip().replace("*", "")
                for line in assertions.splitlines()
                if line.strip()
            ]
            st.success("Key assumptions identified.")
            return assertions_list
        except Exception as e:
            logging.error(f"Error generating assertions: {e}")
            st.error("Failed to identify assumptions.")
            return []


async def fetch_result(assertion: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Asynchronously fetch search results for a given assertion.
    """
    try:
        result = await tavily_client.search(query=assertion)
        return assertion, result.get("results", [])
    except Exception as e:
        logging.error(f"Error fetching search results for '{assertion}': {e}")
        return assertion, []


async def fetch_all_results(assertions: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Asynchronously fetch search results for all assertions.
    """
    with st.spinner("Retrieving online verification results..."):
        tasks = [fetch_result(assertion) for assertion in assertions]
        results = await asyncio.gather(*tasks)
        st.success("Online verification results retrieved.")
        return {assertion: res for assertion, res in results}


async def evaluate_assertions(
    user_input: str, results_dict: Dict[str, List[Dict[str, Any]]]
) -> List[str]:
    """
    For each assertion and its search results, use the generative AI model
    to decide if the original user_input is Real News or Fake News.
    """
    st.info("Evaluating each key assumption...")
    model_eval = genai.GenerativeModel("gemini-1.5-flash")
    eval_response_list = []
    
    # Create a temporary container for intermediate display
    temp_container = st.empty()
    
    for statement, context in results_dict.items():
        if not context:
            logging.warning(f"No results found for assertion: {statement.strip()}")
            st.warning(f"No search results found for '{statement.strip()}'.")
            continue

        try:
            title = context[0].get("title", "").strip()
            content = context[0].get("content", "").strip()
            url = context[0].get("url", "").strip()
        except (IndexError, KeyError) as e:
            logging.error(f"Error processing context for '{statement.strip()}': {e}")
            st.error(f"Error processing context for '{statement.strip()}'.")
            continue

        evaluation_prompt = f"""Here is a statement:  
{statement.strip()}  

Carefully analyze the correctness of this statement using the provided information gathered from the internet:  
{content}  

### Step-by-Step Evaluation:
1. Identify the key claims made in the statement.  
2. Cross-check these claims with the provided context and assess whether they align with verified information.  
3. Consider any contradictions or missing details that might affect the validity of the statement.  
4. Based on your reasoning, determine whether:\n```{user_input}``` is Real News or Fake News.

### Final Decision:  
- If the above news is Real News then output *TRUE* else output *FALSE*.

Provide your reasoning along with the final answer and include the source URL of the data.
"""
        try:
            eval_response = await model_eval.generate_content_async(evaluation_prompt)
            # Display evaluation in an expander for a more interactive view
            with st.expander(f"Evaluation for assertion: {statement.strip()}"):
                st.text_area("Result", value=f"{eval_response.text.strip()}\n\nSource URL: {url}", 
                             height=200)
            eval_response_list.append(eval_response.text.strip())
            # A short pause to enhance interactivity
            await asyncio.sleep(1)
        except Exception as e:
            logging.error(
                f"Error generating evaluation for assertion '{statement.strip()}': {e}"
            )
            st.error(f"Failed to evaluate assertion '{statement.strip()}'.")
    st.success("All key assumptions evaluated.")
    return eval_response_list


async def asyncprocess_and_evaluate(reasoning_list: List[str]) -> str:
    """
    Combines a list of reasoning strings into paragraphs, builds a prompt,
    and sends it to the generative model to provide an overall evaluation.
    """
    combined_text = "\n\n".join(reasoning_list)
    model_eval = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
General Prompt:

You are provided with a list of reasoning steps, where each step includes its chain-of-thought and a preliminary conclusion 
regarding the veracity of a news item (either "FAKE" or "REAL"). Your task is to synthesize these individual steps into a cohesive 
overall reasoning narrative, and provide a final verdict on whether the news is FAKE or REAL.

Instructions:

1. Read and understand each reasoning step below.
2. Extract key evidence and conclusions.
3. Combine these pieces into a single comprehensive chain-of-thought.
4. Decide if the news is FAKE or REAL.
5. Clearly justify your final decision in the combined narrative.
6. Write the reasoning in such a way that people can easly understand.

Output Format:
Your final output should contain two sections:
Overall Reasoning: A detailed explanation that synthesizes the evidence and logic.
Final Result: A clear statement indicating either "FAKE" or "REAL".

Example Output:

Final Result: [FAKE or REAL]

Overall Reasoning: [Detailed explanation combining evidence and reasoning.]

Reasoning Steps:
{combined_text}
"""
    with st.spinner("Synthesizing overall evaluation..."):
        final_result = await model_eval.generate_content_async(prompt)
    return final_result.text.strip()


async def process_user_input(user_input: str) -> Tuple[str, Dict[str, List[Dict[str, Any]]]]:
    """
    Executes the entire pipeline: generate assertions, fetch search results,
    evaluate assertions, and return a final summary evaluation.
    """
    assertions_list = await generate_assertions(user_input)
    if not assertions_list:
        return "No assertions generated. Cannot proceed.", {}
    results_dict = await fetch_all_results(assertions_list)
    eval_results = await evaluate_assertions(user_input, results_dict)
    final_evaluation = await asyncprocess_and_evaluate(eval_results)
    return final_evaluation, results_dict


def check_result(text: str):
    """
    Checks if "Final Result: FAKE" or "Final Result: REAL" is present in the given text.
    Returns:
        "FAKE" if "Final Result: FAKE" is found,
        "REAL" if "Final Result: REAL" is found,
        None otherwise.
    """
    text_lower = text.lower()
    if re.search(r"final result: fake", text_lower):
        return "FAKE"
    elif re.search(r"final result: real", text_lower):
        return "REAL"
    else:
        return None


def main():
    st.set_page_config(page_title="News Verification Assistant",
                       layout="wide")
    st.title("News Verification Assistant")
    st.markdown(
        """
        Welcome to the News Verification Assistant.
        
        **How It Works:**
        1. Extracts key assumptions from your news statement.
        2. Retrieves online verification results for each assumption.
        3. Evaluates each assumption using advanced generative AI.
        4. Synthesizes the findings into a final verdict.
        
        Enter a news statement below to verify its authenticity.
        """
    )
    

    user_input = st.text_area("Enter the statement to analyze:", height=200)
    if st.button("Verify News", key="verify_news"):
        if not user_input.strip():
            st.error("Input cannot be empty. Please provide a valid statement.")
        else:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            final_evaluation, results_dict = loop.run_until_complete(
                process_user_input(user_input.strip())
            )
            loop.close()
            
            st.subheader("Overall Final Evaluation:")
            verdict = check_result(final_evaluation)
            if verdict == "FAKE":
                st.error(final_evaluation)
            elif verdict == "REAL":
                st.success(final_evaluation)
            else:
                st.info(final_evaluation)
            
            # Display source URLs
            st.subheader("Source URLs:")
            for value in results_dict.values():
                if value:  # Avoid IndexError for empty lists
                    item = value[0]
                    url = item.get("url", "#")
                    title = item.get("title", "No Title")
                    st.markdown(
                        f"- [{title}]({url})", unsafe_allow_html=True
                    )


if __name__ == "__main__":
    main()
