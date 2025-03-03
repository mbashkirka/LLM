import os
from time import sleep
from playwright.sync_api import sync_playwright

from utils.inference import generate_text
from utils.description_refinementt import refine_description, generate_style_description
from utils.id_utils import get_input_by_id, get_id_dir, save_refined_prompts


def count_completions() -> int:
    log_path = os.getenv('OLLAMA_LOG_PATH', 'ollama_log.txt')
    with open(log_path, 'r') as file:
        logs = file.read()
        # this appears in the logs every time ollama is done generating text for openui
        return logs.count("/v1/chat/completions")
    return 0


def generate_image(prompt : str, output_path : str):
    with sync_playwright() as p:
        old_completions = count_completions()

        browser = p.firefox.launch()
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})

        page.goto('http://localhost:7878/ai/new/')

        page.locator("[class='h-4 w-4']").nth(1).click(); # settings click
        page.screenshot(path=output_path)
        sleep(1)

        page.locator("[role='combobox']").nth(0).click(); # drop-down click
        page.screenshot(path=output_path)
        sleep(1)

        page.get_by_text("Qwen2.5").nth(0).click()
        page.screenshot(path=output_path)
        sleep(1)

        page.get_by_text("Update").dispatch_event("click")
        page.screenshot(path=output_path)
        sleep(1)

        page.locator("[name='query']").fill(prompt)
        page.screenshot(path=output_path)
        sleep(1)

        page.locator("[type='submit']").dispatch_event("click");
        page.screenshot(path=output_path)
        sleep(1)

        page.get_by_role("button", name="Toggle mobile view").last.dispatch_event("click")

        while (old_completions == count_completions()):
            page.get_by_title("HTML preview").screenshot(path=output_path)
            sleep(1)

        sleep(1)
        page.get_by_title("HTML preview").screenshot(path=output_path)

        browser.close()


def generate_multiple_images(prompts : list[str], style_prompt : str, output_dir : str) -> None:
    for ind, screen_description in enumerate(prompts):
        print(screen_description)
        output_path = f"{output_dir}/{ind+1}.png"

        generate_image(
            screen_description + ' ' + style_prompt,
            output_path
        )

    return


def open_ui(
    id : str | int,
    reference_image_path : str | None = None,
    screens : int = 5,
    output_dir : str = "output_data/open_ui"
) -> str:

    if type(id) is str:
        prompt = id
        refined_prompts = refine_description(prompt, screens, force_llama_backend=True)
    else:
        prompt, reference_image_path = get_input_by_id(id)
        refined_prompts = refine_description(prompt, screens, force_llama_backend=True)

    style_prompt = generate_style_description(prompt)

    id_dir = get_id_dir(output_dir, id)
    save_refined_prompts(refined_prompts, style_prompt, id_dir)

    generate_multiple_images(refined_prompts, style_prompt, id_dir)

    return id_dir
