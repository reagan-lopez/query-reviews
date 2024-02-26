# Query Reviews

## Building from source:

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
