# Query Reviews

This is a demo streamlit app powered by AI to fetch the review details of the Intel Core Ultra 7155H processor from specific websites and youtube links.
The review details are displayed on screen and can be downloaded as CSV.

## Building from Docker Image (Recommended):

**Note**: This is the recommended option to avoid dependency issues.

- Download the docker image.

  ```
  docker pull reaganlopez/query-reviews:latest
  ```

- Run the docker image and follow the instructions.

  ```
  docker run reaganlopez/query-reviews:latest
  ```

## Building from source:

**Note:** This requires a GOOGLE_API_KEY for Gemini Pro.
**Note:** Since the app uses Selenium to play Youtube videos, you may want to mute your system speakers.

- Clone the repo and `cd` into it.

  ```
  git clone git@github.com:reagan-lopez/query-reviews.git
  cd query-reviews
  ```

- Set up virtual environment and install dependencies.

  ```
  source setup.sh
  ```

- Get a GOOGLE_API_KEY for Gemini Pro from https://ai.google.dev/. Save it in a `.env` file as GOOGLE_API_KEY = '\<api key\>'

- Launch the streamlit app and follow the instructions.

  ```
  streamlit run src/app.py
  ```
