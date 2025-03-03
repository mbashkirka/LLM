import csv
import os

from baselines.open_ui import open_ui
from baselines.pure_mm_llm import pure_mm_llm
from baselines.ui_diffuser import ui_diffuser
from baselines.retrieval_baseline import retrieval_baseline
from ui_evaluation.llm_evaluation import evaluation_module


def run_tests_by_id(baseline_func, id_list : list[int]) -> None:
    for id in id_list:
        output_dir = baseline_func(id)
        for filename in os.listdir(output_dir):
            extention = filename.split('.')[-1]
            if extention != "png" and extention != "jpg": continue
            image_path = f"{output_dir}/{filename}"
            evaluation_module(image_path, baseline_func.__name__, image_path)
    return


if __name__ == "__main__":
    with open('data_storage/experimental_setup.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader)
        id_list = []
        for row in reader:
            id_list.append(int(row[0]))

        """run_tests_by_id(retrieval_baseline, id_list)"""

        run_tests_by_id(open_ui, id_list)

        run_tests_by_id(pure_mm_llm, id_list)

        run_tests_by_id(ui_diffuser, id_list)
