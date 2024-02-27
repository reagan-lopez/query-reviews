import utils
import constants
import genai
from logger import logging

import os
import csv
from io import StringIO
import pandas as pd
import textwrap


class Review:
    def __init__(self, url: str):
        """
        Initialize Review object with the provided URL.

        Args:
        url (str): The URL of the review.
        """
        self.url: str = url
        self.is_youtube: bool = None
        self.website_name: str = None
        self.title: str = None
        self.author: str = None
        self.dir_path: str = None
        self.summary: str = None
        self.benchmarks: pd.DataFrame = None

    def set_overview(self):
        """
        Set overview attributes of the review.
        """
        if not self.url:
            return

        self.is_youtube = utils.is_youtube_link(self.url)

        msg = f"Generating overview for {self.url}"
        print(msg)
        logging.info(msg)

        if self.is_youtube:
            self.website_name, self.title = utils.collect_youtube_metadata(url=self.url)
            self.author = (
                self.website_name
            )  # Author is same as Channel name (Website name)
            if self.website_name:
                self.dir_path = os.path.join(
                    constants.DATA_DIR, self.website_name.replace(" ", "")
                )
                utils.collect_youtube_content(url=self.url, dir_path=self.dir_path)
                _, generated_summary = genai.generate_overview(
                    dir_path=self.dir_path, generate_metadata=False
                )
                if generated_summary:
                    self.summary = generated_summary.summary

        else:
            self.website_name = utils.collect_website_metadata(url=self.url)
            if self.website_name:
                self.dir_path = os.path.join(
                    constants.DATA_DIR, self.website_name.replace(" ", "")
                )
                utils.collect_website_content(url=self.url, dir_path=self.dir_path)
                generated_metadata, generated_summary = genai.generate_overview(
                    dir_path=self.dir_path, generate_metadata=True
                )
                if generated_metadata:
                    self.title = generated_metadata.title
                    self.author = generated_metadata.author
                if generated_summary:
                    self.summary = generated_summary.summary

        msg = f"Done generating overview for {self.url}"
        print(msg)
        logging.info(msg)

    def set_benchmark_data(self, images=None):
        """
        Set benchmark data of the review.

        Args:
        images (list): List of image paths.
        """
        msg = f"Generating benchmark data for {self.url}"
        print(msg)
        logging.info(msg)

        images_path = None
        if self.is_youtube:
            images_path = utils.collect_youtube_images(
                url=self.url, dir_path=self.dir_path
            )
        else:
            images_path = utils.collect_website_images(
                images=images, dir_path=self.dir_path
            )

        generated_benchmarks = genai.generate_benchmark_data(images_path=images_path)
        self.benchmarks = utils.get_benchmarks_df(benchmarks=generated_benchmarks)

        msg = f"Done generating benchmark data for {self.url}"
        print(msg)
        logging.info(msg)

    def download_csv(self):
        """
        Download review data as CSV.
        """
        output = StringIO()  # Create an in-memory file-like object
        writer = csv.writer(output)

        writer.writerow(["Website", self.website_name])
        writer.writerow(["Link", self.url])
        writer.writerow(["Title", self.title])
        writer.writerow(["Author", self.author])
        if not self.summary or self.summary == "":
            writer.writerow(["Summary", self.summary])
        else:
            writer.writerow(["Summary", textwrap.fill(self.summary, width=70)])

        # Adding two empty rows for formatting
        writer.writerow([])
        writer.writerow([])

        if self.benchmarks is not None:
            self.benchmarks.to_csv(output, index=False)

        csv_data = output.getvalue()  # Get the CSV data as a string
        output.close()

        return csv_data


class Reviews:
    def __init__(self, urls: str):
        """
        Initialize Reviews object with the provided URLs.

        Args:
        urls (list): List of review URLs.
        """
        self.urls = urls
        self.overview: pd.DataFrame = None
        self.summary: str = None

    def set_summary(self):
        """
        Set summary attributes of the reviews.
        """
        if not self.urls:
            return

        msg = f"Generating summary for {len(self.urls)} urls"
        print(msg)
        logging.info(msg)

        data = []
        columns = ["Website", "Link", "Title", "Author", "Summary"]
        summaries = []
        for url in self.urls:
            review = Review(url)
            review.set_overview()
            data.append(
                [
                    review.website_name,
                    review.url,
                    review.title,
                    review.author,
                    review.summary,
                ]
            )
            summaries.append(review.summary)
        self.overview = pd.DataFrame(data, columns=columns)

        generated_summary = genai.generate_overall_summary(summaries)
        if generated_summary:
            self.summary = generated_summary.summary

    def download_csv(self):
        """
        Download reviews summary data as CSV.
        """
        output = StringIO()  # Create an in-memory file-like object
        writer = csv.writer(output)

        if not self.summary or self.summary == "":
            writer.writerow(["Overall Summary", self.summary])
        else:
            writer.writerow(["Overall Summary", textwrap.fill(self.summary, width=70)])

        # Adding two empty rows for formatting
        writer.writerow([])
        writer.writerow([])

        if self.overview is not None:
            self.overview.to_csv(output, index=False)

        csv_data = output.getvalue()  # Get the CSV data as a string
        output.close()

        return csv_data
