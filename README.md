# Query Reviews

This Streamlit app utilizes Generative AI to retrieve review details of the Intel Core Ultra 7155H processor from designated websites and YouTube links. The fetched review details are displayed on screen and can be downloaded as a CSV file.

**Note**

- The decision to generate results one review at a time was made to speed up functional testing. Otherwise, processing all reviews collectively as a batch job would take around an hour.
- Since the requirement was to create an AI bot, it was intentional to avoid a pure web scraping approach.
- It's worth noting that Generative AI encounters challenges in accurately extracting numerical data, often resulting in fabricated numbers.

## Building from Docker Image (Recommended):

**Note**: This is the recommended option to avoid dependency issues.

1. Download the docker image.

   ```
   docker pull reaganlopez/query-reviews:latest
   ```

2. Run the docker image.

   ```
   docker run --rm -p 8501:8501 reaganlopez/query-reviews:latest
   ```

3. View the `streamlit` app in browser.
   ```
   http://localhost:8501/
   ```

## Building from source (Tested on Ubuntu 23.04):

**Note:** This requires a GOOGLE_API_KEY for Gemini Pro. Also, since the app uses Selenium to play Youtube videos, you may want to mute your system speakers.

1. Clone the repo and `cd` into it.

   ```
   git clone git@github.com:reagan-lopez/query-reviews.git
   cd query-reviews
   ```

2. Set up a virtual environment and install python package dependencies.

   ```
   source setup.sh
   ```

3. Make sure `google-chrome-stable` is installed as it is used by `selenium`.`

   ```
   apt-get update && \
   apt-get install -y wget unzip && \
   wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
   apt install -y ./google-chrome-stable_current_amd64.deb && \
   rm google-chrome-stable_current_amd64.deb && \
   apt-get clean
   ```

4. Get a `GOOGLE_API_KEY` for Gemini Pro from https://ai.google.dev/. Save it in a `.env` file as GOOGLE_API_KEY = '\<api key\>'

5. Launch the `streamlit` app.

   ```
   streamlit run src/app.py
   ```

## Implementation Details:

The implementation mainly consists of the following functional components:

### Data Collection:

- For YouTube links:

  - Automatically gathers **metadata** such as channel name and video title.
  - Automatically retrieves **video transcriptions** for review summarization.
  - Automatically captures **video screenshots** every 10 seconds. This interval ensures relevant frames are captured, though occasional misses may occur.

- For Website links (non-YouTube):
  - Automatically **scrapes text content** for review summarization.
  - However, it requires the user to **manually capture the relevant screenshots**. This is because most websites prevent the loading of images by bots, and it was impractical to capture them automatically.

### Overview Generation:

- Utilizes the **RAG (Retrieval Augmented Generation)** concept to generate review overview such as title, author and summary.
  - Text content is embedded using **google-embeddings** and creates an in-memory vector store using **FAISS**.
  - Conducts a **similarity search** to retrieve relevant embeddings for a given query.
  - Utilizes an **LLM (Google Gemini Pro)** to generate the overview based on the retrieved embeddings and query.
  - The model generates a **JSON output** and it's structure is enforced using Pydantic. This may lead to some responses being dropped.

### Benchmark Data Generation:

- Generates benchmark data from each image using the **vision model (Gemini Pro Vision)**.
  - The model is specifically prompted to identify the presence of benchmark data in images to avoid False Positives.
  - The model generates a **JSON output** and it's structure is enforced using Pydantic. This may lead to some responses being dropped.

### Summary Generation:

- Additionally, there is a component responsible for generating an **overall summary** based on individual reviews.
  - This also uses the RAG concept.

## Key Modules:

- [app.py](src/app.py): Contains the Streamlit app.
- [prompts.py](src/prompts.py): Contains the prompts used for different summary generations.
- [genai.py](src/genai.py): Handles all the Generative AI code using LangChain and LlamaIndex.
- [entities.py](src/entities.py): Defines the data classes.
- [utils.py](src/utils.py): Contains helper functions for screenshots, content extraction etc.

## Alternate Design Considerations:

- Since the requirement was to create an AI bot, it was intentional to **avoid a pure web scraping** approach.

- Selecting Google Gemini Pro as the Language Model (LLM) was based on its current availability as a free API. Alternatively, one could opt to utilize **open-source models via Ollama** for local implementation.

- To enhance its versatility, the current design could be improved by replacing hardcoded URLs with a system capable of **automatically retrieving the top search results**.

- Furthermore, to broaden its applicability across review of any product, integrating **Generative AI Agents** could be beneficial.

- It's worth noting that Generative AI still faces challenges in accurately extracting numerical data, often resulting in fabricated numbers. This issue could potentially be addressed by incorporating AI Agents that combine Language Model Models (LLMs) with **Optical Character Recognition (OCR)** techniques to reduce false positives and hallucinations.

- The new version of **Google Gemini Pro (1.5) introduces a feature that enables querying of videos**. This new feature can be used to identify video segments containing benchmark data. This targeted approach could streamline the data collection process for YouTube videos. However, it's important to note that this API is currently restricted for use within Vertex AI and is not externally accessible.

- Lastly, it's important to recognize that this application serves as a demonstration. Future enhancements could include **concurrent execution of multiple steps**, achieved through multiprocessing in Python.
