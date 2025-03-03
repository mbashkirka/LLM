from utils.inference import generate_text, generate_text_llama


def refine_description(prompt : str, screens, force_llama_backend : bool = False, retries : int = 5) -> list[str]:
    # @TODO: add better prompting
    message = f"{prompt} Output short descriptions for {screens} screens AND NOTHING ELSE."
    if force_llama_backend:
        response = generate_text_llama(message, None)
    else:
        response = generate_text(message, None)

    ans = [line for line in response.split('\n') if len(line) > 3]
    if len(ans) > screens:
        if retries > 0:
            print("Description refinement error")
            return refine_description(prompt, screens, force_llama_backend, retries-1)
        else:
            return []
    return ans


def generate_style_description(prompt : str, force_llama_backend : bool = False) -> str:
    message = f"{prompt} Output short color theme description AND NOTHING ELSE."
    if force_llama_backend:
        response = generate_text_llama(message, None)
    else:
        response = generate_text(message, None)

    print(response)
    return response
