FROM python:3.11
WORKDIR /usr/src/query-reviews
COPY . .
RUN chmod +x setup.sh && ./setup.sh
RUN apt-get update && \
    apt-get install -y wget unzip && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt-get clean
ENV PATH="/usr/src/query-reviews/venv/bin:${PATH}"
ARG GOOGLE_API_KEY
ENV GOOGLE_API_KEY $GOOGLE_API_KEY
CMD ["streamlit", "run", "src/app.py"]