import prompts
from logger import logging

from typing import List
from pydantic import BaseModel, Field

from llama_index import SimpleDirectoryReader
from llama_index.multi_modal_llms import GeminiMultiModal
from llama_index.program import MultiModalLLMCompletionProgram
from llama_index.output_parsers import (
    PydanticOutputParser as LlamaIndexPydanticOutputParser,
)

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_community.vectorstores import FAISS


class GeneratedMetadata(BaseModel):
    title: str = Field(..., description="Title of the website", required=False)
    author: str = Field(..., description="Author of the website", required=False)


class GeneratedSummary(BaseModel):
    summary: str = Field(
        ..., description="Summary of the website content", required=False
    )


class GeneratedProduct(BaseModel):
    name: str = Field(..., description="Name of the product")
    score: int = Field(
        ..., description="Benchmark score of the product measured in metrics"
    )


class GeneratedBenchmark(BaseModel):
    is_benchmark: bool = Field(..., description="True if benchmark is detected")
    name: str = Field(..., description="Name of the benchmark")
    type: str = Field(..., description="Type of benchmark")
    metric: str = Field(..., description="Unit of measurement")
    products: List[GeneratedProduct] = Field(
        ..., description="List of products being benchmarked"
    )


# Generate overview
def generate_overview(dir_path, generate_metadata=False):
    metadata, summary = None, None

    # Define models
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)

    try:
        # Load documenet vector store
        documents = SimpleDirectoryReader(dir_path).load_data()
        nodes = []
        for doc in documents:
            nodes.append(doc.text)
        vector_store = FAISS.from_texts(nodes, embedding=embeddings)
    except Exception as e:
        logging.exception(e)
        return metadata, summary

    if generate_metadata:
        # Generate Metadata
        pydantic_parser = PydanticOutputParser(pydantic_object=GeneratedMetadata)
        format_instructions = pydantic_parser.get_format_instructions()
        context_vectors = vector_store.similarity_search(prompts.query_review_metadata)
        prompt = ChatPromptTemplate.from_template(
            template=prompts.prompt_review_metadata
        )
        messages = prompt.format_messages(
            context=context_vectors,
            question=prompts.query_review_metadata,
            format_instructions=format_instructions,
        )
        try:
            output = model(messages=messages)
            logging.info(f"Model output:\n{output.content}")
            metadata = pydantic_parser.parse(output.content)
        except Exception as e:
            logging.exception(e)

    # Generate Summary
    pydantic_parser = PydanticOutputParser(pydantic_object=GeneratedSummary)
    format_instructions = pydantic_parser.get_format_instructions()
    context_vectors = vector_store.similarity_search(prompts.query_review_summary)
    prompt = ChatPromptTemplate.from_template(template=prompts.prompt_review_summary)
    messages = prompt.format_messages(
        context=context_vectors,
        question=prompts.query_review_summary,
        format_instructions=format_instructions,
    )
    try:
        output = model(messages=messages)
        logging.info(f"Model output:\n{output.content}")
        summary = pydantic_parser.parse(output.content)
    except Exception as e:
        logging.exception(e)

    return metadata, summary


# Generate benchmark data
def generate_benchmark_data(images_path):
    benchmarks = []
    model = GeminiMultiModal(model_name="models/gemini-pro-vision", temperature=0)
    try:
        image_documents = SimpleDirectoryReader(images_path).load_data()
    except Exception as e:
        logging.exception(e)
        return benchmarks
    for image_doc in image_documents:
        prompt_template_str = prompts.prompt_benchmark_data
        try:
            llm_program = MultiModalLLMCompletionProgram.from_defaults(
                output_parser=LlamaIndexPydanticOutputParser(GeneratedBenchmark),
                image_documents=[image_doc],
                prompt_template_str=prompt_template_str,
                multi_modal_llm=model,
                verbose=False,
            )
            response = llm_program()
            logging.info(f"Benchmark: \n {response}")
            benchmarks.append(response)
        except Exception as e:
            logging.exception(e)
    return benchmarks


# Generate overall summary
def generate_overall_summary(summaries):
    overall_summary = None

    # Remove empty summaries before embedding
    summaries = [summary for summary in summaries if summary is not None]

    # Define models
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)

    try:
        vector_store = FAISS.from_texts(summaries, embedding=embeddings)
    except Exception as e:
        logging.exception(e)
        return overall_summary

    pydantic_parser = PydanticOutputParser(pydantic_object=GeneratedSummary)
    format_instructions = pydantic_parser.get_format_instructions()
    context_vectors = vector_store.similarity_search(prompts.query_overall_summary)
    prompt = ChatPromptTemplate.from_template(template=prompts.prompt_overall_summary)
    messages = prompt.format_messages(
        context=context_vectors,
        question=prompts.query_overall_summary,
        format_instructions=format_instructions,
    )
    try:
        output = model(messages=messages)
        logging.info(f"Model output:\n{output.content}")
        overall_summary = pydantic_parser.parse(output.content)
    except Exception as e:
        logging.exception(e)

    return overall_summary
