query_review_metadata = """
    Fetch the Title and Author of the website.      
    """

prompt_review_metadata = """
    Generate the output based on the context below. The output must be in the specified JSON format.      
        title: This must be the Title of the Website. If you don't know the answer, set the value as empty.
        author: This must be the Author of the Website or review. If you don't know the answer, set the value as empty.
    Context: \n{context}?\n
    Question: \n{question}\n
    Format Instructions: \n{format_instructions}\n        
    """

query_review_summary = """
    Generate a clear summary of the review, ensuring that the sentiment (positive or negative) is discernible from the summary.       
    """

prompt_review_summary = """
    Generate the output based on the context below. The output must be in the specified JSON format.      
        summary: This must be the summary of the review. If you don't know the answer, set the value as empty.
    Context: \n{context}?\n
    Question: \n{question}\n
    Format Instructions: \n{format_instructions}\n        
    """

prompt_benchmark_data = """
    Input: Image data (URL or uploaded file)

    Task: Benchmark Data Detection and Extraction

    Objective: Identify if the image contains benchmark data.
        Generally benchmark data will include charts, tables and numbers comparing various
        products such as laptops, processors, CPUs, GPUs, NPUs, battery life etc.
        If the probability of the image containing benchmark data is 1, then extract and infer specific benchmark data from the image.
        If the probability of the image containing benchmark data is less than 1, then do not analyze the image further.

    Output: JSON object with extracted benchmark data as follows:
        is_benchmark: This field must be set to True or False based on if the image contains benchmark data or not.
            If this field is set to False, then the rest of the JSON fields must be set to their corresponding empty values.
            if this field is set to True, then populate the rest of the JSON fields as follows:
        benchmark_name: This must be the name of the benchmark. 
            Example 1: "Cinebench R23 - Multi-core"
            Example 2: "Geekbench 6.2 - Multi-core"
            Example 3: "Geekbench 6.2 - Single-core"
            Example 4: "UL Procyon AI (Integer)"
            Example 5: "PCMark 10 - Applications"
            Example 6: "3DMark - Wild Life Extreme"
            Example 7: "GFXBench - Aztech Ruins"
        benchmark_type: This must be the type of processor being benchmarked.
            Example 1: "CPU"
            Example 2: "NPU"
            Example 3: "Graphics"
        benchmark_metric: This must be the unit of measure of the benchmark.
            Example 1: "Score" if the unit is points or score.
            Example 2: "FPS" if the unit is frames per second.
        benchmark_products: This must be the list of products or processors being benchmarked.
            product_name: This must be the name of the product or processor being benchmarked.
                Example 1: "Acer Swift Go 14"
                Example 2: "Apple M2"
                Example 3: "i7-1360P"
            product_score: This must be the benchmark score of the product.
                Example 1: 12576
                Example 2: 8310
                Example 3: 9623
    """

query_overall_summary = """
    Generate an overall summary of the Intel Core Ultra processor, ensuring that the sentiment (positive or negative) is discernible from the summary.       
    """

prompt_overall_summary = """
    Generate the output based on the context below. The output must be in the specified JSON format.      
        summary: This must be the overall summary. If you don't know the answer, set the value as empty.
    Context: \n{context}?\n
    Question: \n{question}\n
    Format Instructions: \n{format_instructions}\n        
    """
