import utils
import constants
import entities

import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime


def main():
    # Set Streamlit page configuration
    st.set_page_config(layout="wide")
    # Set the title of the web app
    st.title("Query Reviews")

    # Load environment variables
    load_dotenv()
    try:
        # Attempt to set the Google API key from environment variable
        os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
    except Exception as e:
        # Display an error message if the GOOGLE_API_KEY environment variable is not set
        st.error(
            "The GOOGLE_API_KEY environment variable is not set. Please set the GOOGLE_API_KEY environment variable."
        )
    else:
        # Check if it is the first run
        if "first_run" not in st.session_state:
            # Create necessary directory for data storage
            utils.create_directory(constants.DATA_DIR, overwrite=True)
            # Mark that it's not the first run
            st.session_state["first_run"] = True
            # Initialize previous URL as None
            st.session_state["previous_url"] = None

        # List of input URLs
        options = ["Select a review URL"]
        input_urls = [
            "https://www.pcworld.com/article/2171363/acer-swift-go-14-review-3.html",
            "https://www.youtube.com/watch?v=WH-qtuVRS2c",
            "https://www.youtube.com/watch?v=Obtc24lwbrw",
            "https://www.youtube.com/watch?v=Dio25xA6pwE",
            "https://www.pcmag.com/news/meteor-lake-first-tests-intel-core-ultra-7-benched-for-cpu-graphics-and",
        ]
        options.extend(input_urls)

        # Create tabs for Individual Review and Overall Summary
        tab1, tab2 = st.tabs(["Individual Review", "Overall Summary"])

        # Individual Review tab functionality
        with tab1:
            # Dropdown to select review URL
            selected_url = st.selectbox(
                "Select a review URL", options, index=0, label_visibility="hidden"
            )
            if selected_url != "Select a review URL":
                # Display review overview
                st.subheader("Review Overview")
                if selected_url != st.session_state["previous_url"]:
                    st.session_state["previous_url"] = selected_url
                    with st.spinner(
                        "***:blue[Generating review overview for the selected url...]***"
                    ):
                        review = entities.Review(selected_url)
                        review.set_overview()
                        st.session_state["review"] = review

                if "review" in st.session_state:
                    review = st.session_state["review"]
                    st.write(f"**Website:** {review.website_name}")
                    st.write(f"**Link:** {review.url}")
                    st.write(f"**Title:** {review.title}")
                    st.write(f"**Author:** {review.author}")
                    st.write(f"**Summary:** {review.summary}")
                    st.subheader("Benchmark Data")

                if "review" in st.session_state and review.benchmarks is None:
                    review = st.session_state["review"]

                    if review.is_youtube:
                        with st.spinner(
                            "***:blue[Generating benchmark data. This may take few minutes based on the duration of the video...]***"
                        ):
                            review.set_benchmark_data(images=None)
                    else:
                        st.info(
                            """
                            NOTE: Benchmark data cannot be automatically fetched for non-YouTube sites as they typically block bots.
                            Please upload screenshots and click **Fetch Benchmark Data** below.
                            """
                        )
                        images = st.file_uploader(
                            "Upload screenshots",
                            accept_multiple_files=True,
                            label_visibility="hidden",
                        )
                        if st.button("Fetch Benchmark Data"):
                            with st.spinner(
                                "***:blue[Generating benchmark data. This may take few minutes based on the number of images...]***"
                            ):
                                if images:
                                    review.set_benchmark_data(images=images)

                if "review" in st.session_state and review.benchmarks is not None:
                    st.dataframe(
                        review.benchmarks,
                        hide_index=True,
                        use_container_width=True,
                    )

                    data = review.download_csv()
                    filename_csv = f'review_{os.path.basename(review.dir_path)}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
                    st.download_button(
                        label="Download as CSV",
                        data=data,
                        file_name=filename_csv,
                        mime="text/csv",
                    )

        # Overall Summary tab functionality
        with tab2:
            n = len(input_urls)
            if (
                st.button("Generate Overall Summary")
                and "reviews" not in st.session_state
            ):
                with st.spinner(
                    f"***:blue[Generating overall summary for {n} urls. This may take few minutes based on the number of urls...]***"
                ):
                    reviews = entities.Reviews(input_urls)
                    reviews.set_summary()
                    st.session_state["reviews"] = reviews
            if "reviews" in st.session_state:
                reviews = st.session_state["reviews"]

                st.subheader("Overall Summary")
                st.write(reviews.summary)

                st.subheader("Details")
                st.dataframe(
                    reviews.overview,
                    hide_index=True,
                    use_container_width=True,
                )

                data = reviews.download_csv()
                filename_csv = (
                    f'review_summary_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
                )
                st.download_button(
                    label="Download as CSV",
                    data=data,
                    file_name=filename_csv,
                    mime="text/csv",
                )


if __name__ == "__main__":
    main()
