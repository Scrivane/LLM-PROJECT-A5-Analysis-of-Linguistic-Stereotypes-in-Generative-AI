from google import genai
import json
from datetime import datetime
import os
from openai import OpenAI
import base64
from groq import Groq
from ollama import chat
from ollama import ChatResponse
import os
from mistralai import Mistral
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
"""
change the following keys with yoru own you cna generate them in the respective sites
"""
api_key_google='placeholder'
groq_token="placeholder"
api_key_minstral="placeholder"
###
###
###
###




def make_a_query3(prompt, tokenizer, model, max_new_tokens=512):
    import gc
    """
    query: your question or instruction
    ground_truth: optional reference text
    first_response: optional previous response to include in prompt
    """
    # Build the prompt following Qwen instruction-style format

    
    # Prepare chat template
    messages = [{"role": "user", "content": prompt}]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    # Tokenize for model input
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    # Generate output
    with torch.no_grad():
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id
        )

    # Remove prompt tokens to get only the model response
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
    content = tokenizer.decode(output_ids, skip_special_tokens=True)
    del model_inputs, generated_ids
    torch.cuda.empty_cache()
    gc.collect()
    return content







def log_llm_output(prompt, response, model_name, log_file):
    log_entry = {
        "date": datetime.now().isoformat(),  # ISO 8601 timestamp
        "prompt": prompt,
        "response": response,
        "model_name": model_name
    }
        # Append JSON line to file
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")



def check_if_output_exists(prompt, model_name, log_file):
    """
    Checks whether an LLM output already exists in the log file for a given prompt, image, and model.
    
    Returns:
        response (str): The saved LLM response if found, otherwise None.
    """
    if not os.path.exists(log_file):
        return False  # No log file yet → no previous entries

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue  # skip malformed line
                
                if (
                    entry.get("prompt") == prompt
                    and entry.get("model_name") == model_name
                ):
                    return entry.get("response")  # Found a match
    except Exception as e:
        print(f"Error reading log file: {e}")
    
    return False  # Not found





def call_local_qwen(prompt, log_file,maxnew_token=15):
   

    model_name = "Qwen/Qwen3-4B-Instruct-2507-FP8"
    if check_if_output_exists(prompt, model_name,log_file)==False:
        try:


            



                    model = AutoModelForCausalLM.from_pretrained(model_name, 
                                                            
                                                                torch_dtype="auto",
                                                            
                                                            device_map="cuda")
                    tokenizer = AutoTokenizer.from_pretrained(model_name)
         
                




                    answer=make_a_query3(prompt, tokenizer, model, max_new_tokens=maxnew_token)
          
                    log_llm_output(prompt, answer, model_name,log_file)



        
        except Exception as e:
            print(f"Error model {model_name}. the error is : {e}")   
    






def call_multiple_apis_only_text(prompt, log_file):
   

    model_name="gemini-2.5-pro"
    if check_if_output_exists(prompt, model_name,log_file)==False:
        try:

            client = genai.Client(api_key=api_key_google)



            response = client.models.generate_content(
                model=model_name,
                contents=[prompt],
            )

            print(response.text)
            log_llm_output(prompt, response.text, model_name,log_file)
            print("\n\n\n\n-----")
        
        except Exception as e:
            print(f"Error model {model_name}. the error is : {e}")   
    




    h_token=""



    """ client = OpenAI(    non funziona
        base_url="https://router.huggingface.co/v1",
        api_key=h_token,
    ) """
    model_name="meta-llama/llama-4-maverick-17b-128e-instruct"

    if check_if_output_exists(prompt, model_name,log_file)==False:
        try:
        
            client = Groq(api_key=groq_token)
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                {
                    "role": "user",
                    "content":[
                        {"type": "text", "text": prompt},
          
                           

                    ]
                }
                ],
                temperature=1,
                max_completion_tokens=1024,
                top_p=1,
                stream=True,
                stop=None
            )
            first_answer=""
            for chunk in completion:
                print(chunk.choices[0].delta.content or "", end="")
                first_answer+=chunk.choices[0].delta.content or ""

            log_llm_output(prompt, first_answer, model_name,log_file)
        
        except Exception as e:
            print(f"Error model {model_name}. the error is : {e}")   
    


    """   works with qwen byuyt no idea wich model
    prompt="Tell me a joke about programmers."
    from gradio_client import Client, handle_file


    client = Client("Qwen/Qwen3-VL-Demo")


    file_handled = handle_file(img_path)
    result=client.predict(
    input_value={"files":[file_handled],"text":"Show a representation of this image ER model in a plain textual format easily understandable by LLMs "},
    api_name="/add_message"
    )
    print(result)
    print("-----")
    print("-----")
    print("-----")
    print("-----")
    print("-----")
    print("-----")
    assistant_reply = result[1]["value"][-1]["content"][0]["content"]

    print(assistant_reply) """


    #   good in qwen3-vl:235b-instruct-cloud

    #run qwen3-vl:235b-instruct-cloud
    # use  ollama signin  before running 
    model_name='qwen3-vl:235b-instruct-cloud'
    if check_if_output_exists(prompt, model_name,log_file)==False:
        try:

            response: ChatResponse = chat(   
                model=model_name,   #can also use qwen3-vl:235b-cloud'
                messages=[
            {
                'role': 'user',
                'content': prompt,

            },
            ])


            print(response['message']['content'])


            log_llm_output(prompt, response['message']['content'], model_name,log_file)
        
        except Exception as e:
            print(f"Error model {model_name}. the error is : {e}")   






    model_name = "magistral-small-2509"  #seems pretty good
    #model = "pixtral-large-latest"  #not goos
    #model = "mistral-large-latest"   #not good

    #model = "magistral-medium-latest"   #not good
    if check_if_output_exists(prompt, model_name,log_file)==False:
        try:

            client = Mistral(api_key=api_key_minstral)



            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]

            chat_response = client.chat.complete(
                model=model_name,
                messages=messages
            )

            print(chat_response)
            print("\n\n\n\n-----")
            print("-----")
            print("-----\n\n\n\n")

            final_output = chat_response.choices[0].message.content
            if isinstance(final_output, str):
                final_output = str(final_output)
            else:
                final_output = final_output[-1].text
                

            print(final_output) 

            log_llm_output(prompt, final_output, model_name,log_file)


        except Exception as e:
            print(f"Error model {model_name}. the error is : {e}")   



    
##############grok

        """  model_name = "x-ai/grok-4.1-fast"   #si fermerà a funzionare il 4 dicembre
        if check_if_output_exists(prompt, model_name,log_file)==False:
            try:
                client = OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=grok_key_,
                        )


                response = client.chat.completions.create(
                model=model_name,
                messages=[
                        {
                            "role": "user",
                            "content": [{"type":"text","text":prompt}
                        ]}],
                extra_body={"reasoning": {"enabled": True}}
                    )

                final_output = response.choices[0].message.content

               

                print(final_output)
                print("\n\n\n\n-----")
                print("-----")
                print("-----\n\n\n\n")

 
                log_llm_output(prompt, img_path, final_output, model_name,log_file)


            except Exception as e:
                print(f"Error model {model_name}. the error is : {e}") """   







    """ from zai import ZaiClient   non va serve paga

    client = ZaiClient(api_key=zai_key)  # Enter your own APIKey
    response = client.chat.completions.create(
        model="glm-4.5v",  # Enter the name of the model you want to call
        messages=[
            {
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": img_url
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ],
                "role": "user"
            }
        ],
        thinking={
            "type":"enabled"
        }
    )
    print(response.choices[0].message) """




