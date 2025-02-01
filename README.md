Below is a comprehensive and detailed `README.md` in Markdown format for your project:

---

```markdown
# News Verification Assistant

The **News Verification Assistant** is an interactive web application that leverages advanced generative AI models along with online search APIs to assess the validity of a news statement. It extracts key assumptions from a given news statement, retrieves online verification results for each assumption, and evaluates whether the news is "REAL" or "FAKE" through a reasoning-based approach.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation and Setup](#installation-and-setup)
- [Environment Variables](#environment-variables)
- [Usage](#usage)
- [Code Overview](#code-overview)
- [Logging and Error Handling](#logging-and-error-handling)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Assumption Extraction:**  
  Uses a generative AI model to generate key assumptions from a user-provided news statement in bullet point format.

- **Online Verification:**  
  Retrieves relevant online search results for each assumption using the Tavily search API.

- **Step-by-Step Evaluation:**  
  Evaluates each assumption using a detailed, step-by-step reasoning approach by cross-checking with the online context.

- **Overall Verdict Synthesis:**  
  Integrates individual evaluations into a final decision indicating whether the news is "REAL" or "FAKE".

- **Interactive User Interface:**  
  Built using Streamlit to provide an intuitive and interactive experience for users.

## Architecture

The application is built with the following components:

1. **Generative AI Model (Gemini):**  
   - Used for generating key assumptions from the user's news statement.
   - Also utilized for evaluating each assumption based on the online context provided by the search results.

2. **Online Search API (Tavily):**  
   - Fetches search results asynchronously for each extracted assumption.

3. **Asynchronous Processing:**  
   - Utilizes Python's `asyncio` to concurrently execute web requests and evaluation tasks, optimizing performance.

4. **User Interface (Streamlit):**  
   - Provides a clean UI where users can enter a news statement, view verification progress, and see final evaluations along with source URLs.

## Installation and Setup

### Prerequisites

- **Python 3.7 or higher**
- **pip** package manager

### Steps to Install

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/your-username/news-verification-assistant.git
   cd news-verification-assistant
   ```

2. **Create and Activate a Virtual Environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Linux/MacOS
   # or on Windows:
   venv\Scripts\activate
   ```

3. **Install Required Dependencies:**

   Make sure you have a `requirements.txt` file that lists all the necessary packages. Then run:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**

   Create a `.env` file in the project root and add the following lines with your API keys:

   ```dotenv
   GEMINI_API_KEY=your_gemini_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

5. **Run the Application:**

   ```bash
   streamlit run your_script_name.py
   ```

   Replace `your_script_name.py` with the name of your main Python file.

## Environment Variables

The application requires two API keys:

- **GEMINI_API_KEY:** API key for the Gemini Generative AI service.
- **TAVILY_API_KEY:** API key for the Tavily online search service.

Environment variables are loaded using the `dotenv` package from a `.env` file located in the project root.

## Usage

1. **Start the Application:**  
   Launch the application using the command:

   ```bash
   streamlit run your_script_name.py
   ```

2. **Enter a News Statement:**  
   Open the provided URL in your browser and input a news statement in the text area.

3. **Verify News:**  
   Click on the **Verify News** button. The application will:
   - Extract key assumptions from your statement.
   - Retrieve and display search results for each assumption.
   - Evaluate each assumption using a step-by-step process.
   - Synthesize the evidence into a final overall evaluation verdict.

4. **Review Results:**  
   The UI displays:
   - The final evaluation verdict.
   - Detailed reasoning for each assumption in expandable sections.
   - Source URLs for the evidence used.

## Code Overview

The main components of the code include:

- **Prompt and Template Creation:**
  - `create_template(user_input: str)`: Constructs a prompt template that feeds the input statement to the generative AI model to extract assumptions.

- **Assertion Generation:**
  - `generate_assertions(user_input: str)`: Uses Gemini to asynchronously generate key assumptions in the form of bullet points.

- **Fetching Search Results:**
  - `fetch_result(assertion: str)`: Invokes the Tavily API to fetch search results for a single assertion.
  - `fetch_all_results(assertions: List[str])`: Concurrently performs search operations for all assumptions.

- **Evaluating Assumptions:**
  - `evaluate_assertions(user_input: str, results_dict: Dict[str, List[Dict[str, Any]]])`: Evaluates each assumption based on the search results using a detailed chain-of-thought prompt.
  - Utilizes Streamlit expanders to display individual evaluation results interactively.

- **Final Evaluation Synthesis:**
  - `asyncprocess_and_evaluate(reasoning_list: List[str])`: Combines individual reasoning outputs into a final comprehensive verdict.

- **Main Pipeline:**
  - `process_user_input(user_input: str)`: Coordinates the entire process from assumption generation to final evaluation.

- **Utility:**
  - `check_result(text: str)`: Helper function to check the final evaluation verdict.

- **Streamlit Interface:**
  - The `main()` function sets up the Streamlit page, handles user input, initiates the asynchronous processing, and displays results.

## Logging and Error Handling

- **Logging:**  
  Configured using Python’s built-in `logging` module.  
  Logs important events, errors, and warnings during execution to aid in debugging.

- **Error Handling:**  
  Checks for the presence of required API keys.  
  Catches exceptions during API calls and evaluations, showing error messages using Streamlit’s UI elements.

## Dependencies

- **Core Python Libraries:**  
  `os`, `re`, `asyncio`, `logging`, `typing`

- **External Libraries:**  
  - [Streamlit](https://streamlit.io/)
  - [dotenv](https://pypi.org/project/python-dotenv/)
  - [Google Generative AI Library](https://cloud.google.com/generative-ai)  
  - [Tavily](https://github.com/your-organization/tavily) *(or install via pip)*
  
Make sure the `requirements.txt` includes all dependencies with the appropriate version numbers.

## Contributing

Contributions are welcome! To contribute:

1. **Fork the Repository.**
2. **Create a New Branch:**  
   Create a branch for your feature or bug fix.
3. **Make Your Changes.**
4. **Submit a Pull Request:**  
   Include detailed explanations of the changes.

Please ensure your code follows the existing coding style and includes relevant tests and documentation.

## License

This project is licensed under the [MIT License](LICENSE).