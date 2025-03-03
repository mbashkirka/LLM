from time import sleep
from playwright.sync_api import sync_playwright

from utils.inference import generate_text
from utils.description_refinementt import refine_description, generate_style_description
from utils.id_utils import get_input_by_id, get_id_dir, save_refined_prompts
from utils.gmail_utils import get_login_code


def generate_image(prompt : str, image_path : str | None, output_path : str):
    with sync_playwright() as p:
        old_code = get_login_code()

        browser = p.firefox.launch()
        context = browser.new_context()

        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})

        page.goto("https://v0.dev/")
        page.screenshot(path=output_path)

        page.get_by_text("Sign in").click()

        page.get_by_placeholder("Work Email").click()
        page.get_by_placeholder("Work Email").fill("your-adress@gmail.com")
        page.screenshot(path=output_path)

        page.get_by_text("Continue with email").click()

        page.screenshot(path=output_path)

        new_code = get_login_code()
        while(old_code == new_code):
            sleep(5)
            page.screenshot(path=output_path)
            new_code = get_login_code()

        print("Login code recieved", new_code)

        page.locator("[autocomplete='one-time-code']").fill(new_code)   #code input
        # page.get_by_text("Accept and Continue").nth(1).click()
        page.screenshot(path=output_path)

        # page.get_by_placeholder("Ask v0 a question...").click()
        page.get_by_placeholder("Ask v0 a question...").fill(prompt)
        sleep(2)
        page.screenshot(path=output_path)

        page.locator("[class='shrink-1 min-w-0 grow-0']").click()
        sleep(2)
        page.screenshot(path=output_path)

        # page.get_by_title("HTML preview").screenshot(path=output_path)
        print(context.cookies())

        context.close()
        browser.close()
    return


def generate_multiple_images(prompts : list[str], style_prompt : str, image_path : str | None, output_dir : str) -> None:
    for ind, screen_description in enumerate(prompts):
        print(screen_description)
        output_path = f"{output_dir}/{ind+1}.png"

        if image_path is None: screen_description += ' ' + style_prompt

        generate_image(
            screen_description,
            image_path,
            output_path
        )

    return


def v0(
    id : str | int,
    reference_image_path : str | None = None,
    screens : int = 5,
    output_dir : str = "output_data/v0"
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

    generate_multiple_images(refined_prompts, style_prompt, reference_image_path, id_dir)

    return id_dir
