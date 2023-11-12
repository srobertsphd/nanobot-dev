
import openai
import pinecone

index = pinecone.Index('utech-manual')


def vectorize_prompt_with_openai(prompt):
    """
    This returns the vector embedding only, without the other
    components of the openia object - (this is the ['data'])
    """
    prompt_vector = openai.Embedding.create(input=prompt, engine="text-embedding-ada-002")
    return prompt_vector['data'][0].embedding

def format_pinecone_response_object(response):
    """
    Takes in a python object that is returned from Pinecone
    iterates over the k nearest neighbor matches
    pulls out the relevant info and puts this into a list of dicts
    this format can be written to json
    """
    response_list = []
    for index, item in enumerate(response):
        item_dict = {
#             "response_ranking": index,
#             "embed_id": item['id'],
            "score": item['score'],
            "text": item['metadata']['text']
        }
        response_list.append(item_dict)
    return response_list

def submit_query_to_pinecone(prompt_vector, k):
    """
    index is my pinecone database.
    metadata is the text that was used to make the vector
    k, top_k is the number of vectors it will retrieve for a single prompt
    """
    query = index.query(
        vector=prompt_vector,
        top_k=k,
        include_metadata=True
    )
    return format_pinecone_response_object(query.matches)

def pinecone_prompt_and_retrieve(prompt, k):
    """
    input: takes the prompts, and the number of retrievals (k)
    1. gets the vector
    2. sends the query to pinecone
    3. formats the response
    """
    vect = vectorize_prompt_with_openai(prompt)
    return submit_query_to_pinecone(vect, k) 

def get_completion_from_messages(messages, model="gpt-3.5-turbo",temperature=0,max_tokens=500):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, # this is the degree of randomness of the model's output
        max_tokens=max_tokens, # the maximum number of tokens the model can ouptut 
    )
    return response.choices[0].message["content"]

delimiter = "####"

def get_system_message(retrieved_texts):
    system_message_pinecone = f"""
        You are an engineer with expertise in complex tools
        Follow these instructions to process the user query. 
        The user query is delimited with {delimiter}.

        [Context from Vector Database]
        these {retrieved_texts} are the top relevant pieces of information retrieved from the vector database. 
        please use this along with your ability to search outside of the retrieved texts provided
        The name of the equipment that the questions are relation to is a SPTS uEtch Module Piamaxx HF Vapor Mems Etch Release System

        [Instructions]
            
        Step 1: {delimiter} Formulate a response that best matches the user's query, 
                Give the response with as much relevant detail as possible
                Do not preface or end the response with extra polite words. 
                Just answer the question with the facts.
                
    """
    return system_message_pinecone