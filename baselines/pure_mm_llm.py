from playwright.sync_api import sync_playwright

from utils.inference import generate_text
from utils.description_refinementt import refine_description, generate_style_description
from utils.id_utils import get_input_by_id, get_id_dir, save_refined_prompts


def extract_html(text : str) -> str:
    start = text.find("<!DOCTYPE html>")
    end = text.find("</html>")
    if start == end: return ""
    end += len("</html>")
    return text[start:end]


def generate_multiple_images(prompts : list[str], style_prompt : str, image_path : str | None, output_dir : str) -> None:
    # expects a newline separated screen descriptions
    for ind, screen_description in enumerate(prompts):
        print(screen_description)

        prompt = "You are a professional front-end developer. Generate HTML code for a: " + screen_description
        if image_path is not None:
            prompt += " Use image provided as a style reference."
        else:
            # we define some style here to hopefully improve consistency
            prompt += " " + style_prompt

        response = generate_text(
            prompt,
            image_path = image_path
        )

        html = extract_html(response)
        with open(f"{output_dir}/{ind+1}.html", 'w', encoding="utf-8") as file:
            file.write(html)

        with sync_playwright() as p:
            browser = p.firefox.launch()
            page = browser.new_page()
            page.set_viewport_size({"width": 512, "height": 1024})
            page.set_content(html)
            page.screenshot(path=f"{output_dir}/{ind+1}.png")

    return


def pure_mm_llm(
    id : str | int,
    reference_image_path : str | None = None,
    screens : int = 5,
    output_dir : str = "output_data/pure_mm_llm"
) -> str:
    if type(id) == str:
        prompt = id
        refined_prompts = refine_description(prompt, screens)
    else:
        prompt, reference_image_path = get_input_by_id(id)
        refined_prompts = refine_description(prompt, screens)

    id_dir = get_id_dir(output_dir, id)

    if reference_image_path is None:
        style_prompt = generate_style_description(prompt)
    else:
        style_prompt = ""

    save_refined_prompts(refined_prompts, style_prompt, id_dir)

    generate_multiple_images(refined_prompts, style_prompt, reference_image_path, id_dir)

    return id_dir
