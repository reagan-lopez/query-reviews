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
        self.url: str = url
        self.is_youtube: bool = None
        self.website_name: str = None
        self.title: str = None
        self.author: str = None
        self.dir_path: str = None
        self.summary: str = None
        self.benchmarks: pd.DataFrame = None

    def set_overview(self):
        if not self.url:
            return

        self.is_youtube = utils.is_youtube_link(self.url)

        msg = f"Collecting data from {self.url}"
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

    def set_benchmark_data(self, images=None):
        msg = f"Collecting benchmark images from {self.url}"
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

    def download_csv(self):
        output = StringIO()  # Create an in-memory file-like object
        writer = csv.writer(output)

        if self:
            website = self.website_name
            link = self.url
            title = self.title
            author = self.author
            summary = self.summary
        else:
            website, title, link, author, summary = "", "", "", "", ""

        writer.writerow(["Website", website])
        writer.writerow(["Link", link])
        writer.writerow(["Title", title])
        writer.writerow(["Author", author])
        writer.writerow(["Summary", textwrap.fill(summary, width=70)])

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
        self.urls = urls
        self.overview: pd.DataFrame = None
        self.summary: str = None

    def set_summary(self):
        if not self.urls:
            return

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
        output = StringIO()  # Create an in-memory file-like object
        writer = csv.writer(output)

        if self:
            summary = self.summary
        else:
            summary = ""

        writer.writerow(["Summary", textwrap.fill(summary, width=70)])

        # Adding two empty rows for formatting
        writer.writerow([])
        writer.writerow([])

        if self.overview is not None:
            self.overview.to_csv(output, index=False)

        csv_data = output.getvalue()  # Get the CSV data as a string
        output.close()

        return csv_data
