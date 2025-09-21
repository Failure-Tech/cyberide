import flask
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

# tokenizer = AutoTokenizer.from_pretrained("purpcode/purpcode-32b-rl")
# model = AutoModelForCausalLM.from_pretrained("purpcode/purpcode-32b-rl", trust_remote_code=True) # , device_map="auto", torch_dtype="auto",s

pipe = pipeline("text-generation", model="purpcode/purpcode-14b-rule-sft")

test_input = input("Enter code for cyberaware proof checking: ")

messages = [
    {
        "role": "user",
        "content": "Generate me cyberaware code for a simple proxy server in python listening on port 8080"
    }
]

# inputs = tokenizer.apply_chat_template(
#     messages,
#     add_generation_prompt=True,
#     tokenize=True,
#     return_dict=True,
#     return_tensors="pt"
# ) #.to(model.device)

# outputs = model.generate(**inputs, max_new_tokens=40)
# print(tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:]))

print(pipe(messages))