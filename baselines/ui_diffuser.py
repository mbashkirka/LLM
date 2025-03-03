import os
import subprocess

from utils.inference import generate_text
from utils.description_refinementt import refine_description, generate_style_description
from utils.id_utils import get_input_by_id, get_id_dir, save_refined_prompts


def generate_image(prompt : str, output_path : str) -> None:
    use_diffusers = os.getenv('USE_DIFFUSERS', '0')
    if use_diffusers=='1':
        generate_image_diffusers(prompt, output_path)
    else:
        generate_image_stable_diffusion_cpp(prompt, output_path)
    return


def generate_image_stable_diffusion_cpp(prompt : str, output_path : str) -> None:
    pre = "sd -m models/512-base-ema.safetensors -p \"";
    post = "<lora:pytorch_lora_weights:1>\" --lora-model-dir models --steps 20 --seed -1 --type f16 -H 512 -W 256 -o "
    command = pre + prompt.replace('\n', ' ').replace('\"', '\'') + post + '\"' + output_path + '\"'
    print(command)
    ret = os.system(command)
    if ret == 1:
        raise RuntimeError("stable-diffusion.cpp error. Make sure you have installed models and that sd is on path!")
    return


def generate_image_diffusers(prompt : str, output_path : str) -> None:
    import torch
    from diffusers import StableDiffusionPipeline
    from pathlib import Path

    # its done this way because python has no static vars
    try:
        image = generate_image.pipe(
            prompt=prompt,
            width = 256,
            height = 512,
        ).images[0]
        image.save(output_path)
    except AttributeError:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print("Diffusion pipleline on", device)
        generate_image.pipe = StableDiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-2-base").to(device)
        generate_image.pipe.load_lora_weights("Jl-wei/ui-diffuser-v2")
        generate_image(prompt, output_path)

    return


def generate_multiple_images(prompts : list[str], style_prompt : str, output_dir : str) -> None:
    for ind, screen_description in enumerate(prompts):
        print(screen_description)
        output_path = f"{output_dir}/{ind+1}.png"
        # this follows original's prompting tech
        generate_image(
            "Mobile UI: " + screen_description + " " + style_prompt,
            output_path
        )
    return


def ui_diffuser(
    id : str | int,
    reference_image_path : str | None = None,
    screens : int = 5,
    output_dir : str = "output_data/ui_diffuser"
) -> str:

    if type(id) == str:
        prompt = id
        refined_prompts = refine_description(prompt, screens)
    else:
        prompt, reference_image_path = get_input_by_id(id)
        refined_prompts = refine_description(prompt, screens)

    style_prompt = generate_style_description(prompt)

    id_dir = get_id_dir(output_dir, id)
    save_refined_prompts(refined_prompts, style_prompt, id_dir)

    generate_multiple_images(refined_prompts, style_prompt, id_dir)

    return id_dir
