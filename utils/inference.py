import os


def generate_text(message : str, image_path = None) -> str:
    use_transformers = os.getenv('USE_TRANSFORMERS', '0')
    if use_transformers == '1':
        return generate_text_transformers(message, image_path)
    else:
        return generate_text_llama(message, image_path)


def generate_text_llama(message : str, image_path : str | None) -> str:
    import ollama

    # waiting llama.cpp to merge support for qwen2.5-vl
    # https://github.com/ollama/ollama/issues/6564
    model_name = "qwen2.5" if image_path is None else "llava"

    if image_path is not None:
        messages = [{'role': 'user', 'content': message, 'images': [image_path]}]
    else:
        messages = [{'role': 'user', 'content': message}]

    response = ollama.chat(model=model_name, messages=messages)
    # options={'temperature': 0}

    if response.message.content is None: return ""
    return response.message.content


def generate_text_transformers(message : str, image_path : str | None) -> str:
    import torch
    from transformers import Qwen2_5_VLForConditionalGeneration, AutoTokenizer, AutoProcessor
    from qwen_vl_utils import process_vision_info

    model_name = "Qwen/Qwen2.5-VL-7B-Instruct-AWQ"

    if image_path is None:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": message},
                ],
            },
        ]
    else:
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": image_path,
                    },
                    {"type": "text", "text": message},
                ],
            },
        ]

    try:
        text = generate_text_transformers.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        image_inputs, video_inputs = process_vision_info(messages)

        inputs = generate_text_transformers.processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        ).to(generate_text_transformers.model.device)

        generated_ids = generate_text_transformers.model.generate(**inputs, max_new_tokens=8000)
        generated_ids_trimmed = [
            out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = generate_text_transformers.processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )
        return output_text[0]

    except AttributeError:
        generate_text_transformers.processor = AutoProcessor.from_pretrained(model_name)
        generate_text_transformers.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            attn_implementation="flash_attention_2",
            device_map="auto",
        )
        return generate_text_transformers(message, image_path)
