import os
import re
import csv

from utils.inference import generate_text


def evaluation_module(image_path: str, baseline_name: str, case_ID: str | int):
    text_prompt = "You are a highly experienced UI/UX expert specializing in evaluating graphical user interfaces (GUIs). Your task is to analyze only the given UI screenshot (first screenshot) and provide a detailed assessment based on the following criteria: 1. Aesthetics Rating (1-10): Evaluate the visual appeal of the UI, considering color scheme, typography, spacing, and overall design harmony; 2. Learnability (1-5): Assess how intuitive the interface is for new users. Is it easy to understand without prior knowledge? Are visual cues and structure clear? 3. Efficiency (1-5): Measure how quickly users can complete key tasks. Is the layout optimized for fast interaction? 4. Usability Rating (1-10): Rate how easy and convenient it is to use the interface. Are there any friction points or usability issues? 5. Design Quality Rating (1-10): Provide an overall design quality score, considering both aesthetics and usability. Identify strengths and weaknesses, and provide actionable recommendations for improvement based on UI/UX best practices. Focus on clarity, consistency, accessibility, and user experience optimization. Your answer should look as follows: ‘Aesthetics Rating: {(1-10)}, Learnability Rating: {(1-5)}, Efficiency Rating: {(1-5)}, Usability Rating: {(1-10)}, Design Quality Rating: {(1-10)}."

    response_text = generate_text(text_prompt, image_path)

    output_folder = f"output_data/{baseline_name}/evaluation"
    os.makedirs(output_folder, exist_ok=True)
    csv_path = os.path.join(output_folder, "evaluation.csv")

    rating_patterns = {
    	'Aesthetics': re.compile(r'Aesthetics Rating[:\s]*(\d+)'),
    	'Learnability': re.compile(r'Learnability Rating[:\s]*(\d+)'),
    	'Efficiency': re.compile(r'Efficiency Rating[:\s]*(\d+)'),
    	'Usability': re.compile(r'Usability Rating[:\s]*(\d+)'),
    	'Design Quality': re.compile(r'Design Quality Rating[:\s]*(\d+)')
    }


    extracted_scores = {}
    for rating_name, pattern in rating_patterns.items():
        match = pattern.search(response_text)
        if match:
            extracted_scores[rating_name] = match.group(1)
        else:
            extracted_scores[rating_name] = None

    file_exists = os.path.isfile(csv_path)
    with open(csv_path, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)

        if not file_exists or os.stat(csv_path).st_size == 0:
            writer.writerow([
    			"Case_ID",
    			"Aesthetics",
    			"Learnability",
    			"Efficiency",
    			"Usability",
    			"Design_Quality"
    		])

        writer.writerow([
            case_ID,
            extracted_scores["Aesthetics"],
            extracted_scores["Learnability"],
            extracted_scores["Efficiency"],
            extracted_scores["Usability"],
            extracted_scores["Design Quality"]
        ])

        print(
            case_ID,
            extracted_scores["Aesthetics"],
            extracted_scores["Learnability"],
            extracted_scores["Efficiency"],
            extracted_scores["Usability"],
            extracted_scores["Design Quality"]
        )

if __name__ == "__main__":
    image_path = "path/input.jpg"
    baseline_name = "baseline_name"
    case_ID = 0
    evaluation_module(image_path, baseline_name, case_ID)
