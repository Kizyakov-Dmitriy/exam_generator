import os
import pathlib
from typing import Union
import numpy as np
from PyPDF2 import PdfFileReader
import shutil

def get_head(font_size: int = 12) -> str:
    """

    :param font_size: int - размер шрифта
    :return: libs: str - часть шапки документа формата latex, которая отвечает за размер шрифта
    """
    libs_begin = "\\documentclass[a4paper," + f"{font_size}" + "pt]{article}" + "\n" + "\\usepackage[" + f"{font_size}" + "pt]{extsizes}" + 5 * "\n"
    return libs_begin


def parse_file(file_path: Union[str, pathlib.Path]) -> tuple:
    """

    :param file_path: Union[str, pathlib.Path] - путь к файлу
    :return: tuple[str] - задания и ответы, содержащиеся в данном файле
    """
    with open(file_path, "r", encoding="utf-8") as f:
        all_text = f.read()
    tasks = []
    answers = []
    for i in all_text.split("\\end{solution}"):
        if i.replace("\n", "") == "":
            break
        tasks.append(i.split("\\end{problem}")[0].replace("\\begin{problem}", ""))
        answers.append(i.split("\\end{problem}")[1].replace("\\begin{solution}", ""))
    return tasks, answers


def get_tasks_and_solutions(task_number: int, Base_path: Union[str, pathlib.Path]) -> tuple:
    """

    :param task_number: int - номер задания, информацию для которого необходимо получить
    :param Base_path: Union[str, pathlib.Path] - 
    :return: tuple[list[str]] - задания и ответы
    """
    tasks = []
    solutions = []
    folder_name = 'Q' + str(task_number)
    folder_path = pathlib.Path(Base_path, folder_name)
    for file_path in folder_path.iterdir():
        if str(file_path).split(".")[-1] == 'txt':
            current_tasks, current_answers = parse_file(file_path)
            tasks.extend(current_tasks)
            solutions.extend(current_answers)
    return tasks, solutions


def gen_tasks_and_solutions(number_of_bils: int, Base_path: Union[str, pathlib.Path], task_number: int = 1) -> tuple:
    """

    :param number_of_bils: int - количество требуемых билетов
    :param task_number: int - номер рассматриваемого задания
    :param Base_path: Union[str, pathlib.Path] - путь к директории Base
    :return: tuple[list[str]] - нужнное количество заданий и ответов для задания типа task_number
    """
    all_tasks, all_solutions = get_tasks_and_solutions(task_number, Base_path)
    indexes = [np.random.randint(len(all_tasks)) for _ in range(number_of_bils)]

    all_tasks_in_string = ""
    all_solutions_in_string = ""
    all_files_tasks = [[] for _ in range(len(all_tasks))]
    all_files_solutions = [[] for _ in range(len(all_tasks))]

    for i, current_task in enumerate(all_tasks):
        for line in current_task.split("\n"):
            if r"%\folder" in line:
                file_line = line[9:]
                file_line = file_line.split(",")
                all_files_tasks[i].extend(file_line)

    for i, current_solution in enumerate(all_solutions):
        for line in current_solution.split("\n"):
            if r"%\folder" in line:
                file_line = line[9:]
                file_line = file_line.split(",")
                all_files_solutions[i].extend(file_line)

    for current_task in all_tasks:
        all_tasks_in_string += "\n\\item\n" + current_task + 2*"\n"
    for current_solution in all_solutions:
        all_solutions_in_string += "\n\\item\n" + current_solution + 2*"\n"

    generated_tasks = [all_tasks[index] for index in indexes]
    generated_solutions = [all_solutions[index] for index in indexes]
    files_tasks = [all_files_tasks[index] for index in indexes]
    files_solutions = [all_files_solutions[index] for index in indexes]
    return generated_tasks, generated_solutions, all_tasks_in_string, all_solutions_in_string, files_tasks, files_solutions, all_files_tasks, all_files_solutions


def get_row_text(text: str, font_size: int) -> str:
    """

    :param text: str - основной текст билета, не влияющих на размер шрифта
    :param font_size: str - текст билета, который определяет размер шрифта
    :return: str - голова и тело итогового билета
    """
    return get_head(font_size) + text


def write_adjust_pdf(text: str, folder_path: str, file_name: str) -> None:
    """

    :param text: str - основной текст билета, не влияющий на размер шрифта
    :param file_name: str - имя файла, в который нужно записать итог работы программы
    """
    font_sizes = [8, 9, 10, 11, 12, 14, 17, 20]
    left_font_index = 0
    right_font_index = len(font_sizes)
    while right_font_index - left_font_index > 1:
        mid_font_index = left_font_index + (right_font_index - left_font_index) // 2
        mid = font_sizes[mid_font_index]
        tex_code = get_row_text(text, font_size=mid)
        write_pdf(tex_code=tex_code, folder_path=folder_path,
                  file_name=file_name)
        with open(pathlib.Path(folder_path, file_name + ".pdf"),
                  'rb') as input_file:
            bil_in_pdf = PdfFileReader(input_file, "rb")
            if bil_in_pdf.getNumPages() > 1:
                right_font_index = mid_font_index
            else:
                left_font_index = mid_font_index
    tex_code = get_row_text(text, font_size=font_sizes[left_font_index])
    write_pdf(tex_code=tex_code, folder_path=folder_path, file_name=file_name)


def remove_previous_pdf(folder_path: Union[str, pathlib.Path], file_name: str) -> None:
    """

    :param folder_path: Union[str, pathlib.Path] - путь к директории
    :param file_name: str - имя файла
    """
    try:
        os.remove(pathlib.Path(folder_path, file_name + ".pdf"))
    except OSError:
        pass


def write_pdf(tex_code: str, folder_path: Union[str, pathlib.Path], file_name: str) -> None:
    """

    :param tex_code: str - код билета на языке atex
    :param folder_path: Union[str, pathlib.Path] - имя папки
    :param file_name: str - имя файла
    """
    remove_previous_pdf(folder_path, file_name)
    with open(pathlib.Path(folder_path, file_name + ".tex"), "w", encoding="utf-8") as f:
        f.write(tex_code)
    command = "pdflatex -output-directory " + str(folder_path) + " " + str(
        pathlib.Path(folder_path, file_name + ".tex")) + " >nul"
    os.system(command)


def create_pdf(bils: list, answers: list, BilPdf_path: Union[str, pathlib.Path], 
               AnsPdf_path: Union[str, pathlib.Path], bil_prefix: str, ans_prefix: str,
               start_bil_number: int = 1) -> None:
    """

    :param bils: list[str] - билеты
    :param answers: list[str] - ответы
    :param start_bil_number: int - нумерацию билетов начать с билета с этим номером
    """
    for bil_number in range(start_bil_number, start_bil_number + len(bils)):
        write_adjust_pdf(
            bils[bil_number - start_bil_number],
            folder_path=pathlib.Path(BilPdf_path, "trash"),
            file_name=bil_prefix + str(bil_number)
        )

        write_pdf(
            tex_code=get_row_text(text=answers[bil_number - start_bil_number], font_size=14),
            folder_path=pathlib.Path(pathlib.Path(AnsPdf_path, "trash")),
            file_name=ans_prefix + str(bil_number)
        )



def clear_directory(folder_path: Union[str, pathlib.Path]) -> None:
    """
    
    :param folder_path: Union[str, pathlib.Path] - путь к директории
    """
    shutil.rmtree(folder_path)
    folder_path.mkdir()


def replace_pdf(folder_path: Union[str, pathlib.Path], prefix: str, save_tex = True, global_files: list = []) -> None:
    """

    :param folder_path - путь к папке
    :param prefix: str - начало названия файла
    :param save_tex: bool - нужно ли оставлять источники в виде .tex
    :param global_files: list - список имён файлов, которые должны быть помещены в глобальные папки
    """
    for file in pathlib.Path(folder_path, "trash").iterdir():
        if file.stem.startswith(prefix) and ((file.suffix == '.pdf') or (save_tex and file.suffix == '.tex')):
            copy_file(path_in=file,
                      path_out=pathlib.Path(folder_path, file.stem.replace(prefix, "")))
            continue
        if file.stem in global_files and ((file.suffix == '.pdf') or (save_tex and file.suffix == '.tex')):
            copy_file(path_in=file,
                      path_out=folder_path)
        
            
            
def read_file(file_path: Union[str, pathlib.Path]) -> str:
    """

    :param file_path: Union[str, pathlib.Path] - имя файла
    :return: str - текст внутри файла
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def copy_file(path_in: Union[str, pathlib.Path], path_out: Union[str, pathlib.Path]) -> None:
    """

    :param path_in: Union[str, pathlib.Path] - путь к файлу для копирования
    :param path_out: Union[str, pathlib.Path] - путь к директории для вставки
    """
    command = "xcopy " +  str(path_in) + " " + str(path_out) + " /Y >nul"
    os.system(command)


def gen_exam(number_of_bils: int = 1, start_bil_number: int = 0, number_of_tasks: int = 1,
             semester_number: int = 1, date: str = "20-10-2022", 
             signature_graphics: list = ["Approved.png", "Prepared.png"],
             bil_prefix: str = 'bil-', ans_prefix: str = 'ans-') -> None:
    """

    :param number_of_bils: int - требуемое количество теха
    :param start_bil_number: int - номер билета, с которого начнется нумерация
    :param number_of_tasks: int - количество заданий в одном билете
    :param semester_number: int - номер семестра
    :param date: str - дата экзамена
    :param signature_graphics: list - список из файлов содержащих подписи
    :param bil_prefix: str - префикс используемый в начале названия каждого файла билета
    :param ans_prefix: str -префикс используемый в начале названия каждого файла ответов
    """
    Base_path = pathlib.Path(pathlib.Path.cwd().resolve(), "GEN", "_Base")
    BilPdf_path = pathlib.Path(pathlib.Path.cwd().resolve(), "GEN", "BilPdf")
    AnsPdf_path = pathlib.Path(pathlib.Path.cwd().resolve(), "GEN", "AnsPdf")
    
    libs = read_file(pathlib.Path(Base_path, "Q0", "lib.txt"))

    bils = [libs.replace("((n))", str(start_bil_number + i)) + 2 * "\n" for i in range(number_of_bils)]
    answers = [libs.replace("((n))", str(start_bil_number + i)) + 2 * "\n" for i in range(number_of_bils)]
    all_bils_tex_code = get_head() + libs.replace(r"\begin{enumerate}", "").replace(r"\textbf{Билет ((n))}", "")
    all_answers_tex_code = get_head() + libs.replace(r"\begin{enumerate}", "").replace(r"\textbf{Билет ((n))}", "")

    base_bils = get_head() + libs.replace(r"\textbf{Билет ((n))}", "")
    base_answers =get_head() + libs.replace(r"\textbf{Билет ((n))}", "")
    
    clear_directory(BilPdf_path)
    clear_directory(AnsPdf_path)
    
    folder_path = pathlib.Path(BilPdf_path, "trash")
    folder_path.mkdir(exist_ok=True)
    folder_path = pathlib.Path(AnsPdf_path, "trash")
    folder_path.mkdir(exist_ok=True)
    
    for signature in signature_graphics:
        copy_file(
            path_in=pathlib.Path(Base_path, "Qend", signature),
            path_out=pathlib.Path(BilPdf_path, "trash"))
        copy_file(
            path_in=pathlib.Path(Base_path, "Qend", signature),
            path_out=pathlib.Path(AnsPdf_path, "trash"))
    
        
    for bil_number in range(start_bil_number, start_bil_number + number_of_bils):
        folder_path = pathlib.Path(BilPdf_path, str(bil_number))
        folder_path.mkdir(exist_ok=True)
        folder_path = pathlib.Path(AnsPdf_path, str(bil_number))
        folder_path.mkdir(exist_ok=True)
        

    for task_number in range(1, number_of_tasks + 1):
        current_tasks, current_answers, all_tasks, all_answers, files_tasks, files_solutions, all_files_tasks, all_files_solutions = gen_tasks_and_solutions(number_of_bils=number_of_bils, Base_path = Base_path, task_number=task_number)
        
        for i in range(len(files_tasks)):
            for file in files_tasks[i]:
                copy_file(
                    path_in=pathlib.Path(Base_path, "Q"+str(task_number),file),
                    path_out=pathlib.Path(BilPdf_path, str(i+start_bil_number)))
                    
        for i in range(len(all_files_tasks)):
            for file in all_files_tasks[i]:
                copy_file(
                    path_in=pathlib.Path(Base_path, "Q" + str(task_number), file),
                    path_out=pathlib.Path(BilPdf_path, "trash"))

        for i in range(len(files_solutions)):
            for file in files_solutions[i]:
                copy_file(
                    path_in=pathlib.Path(Base_path, "Q"+str(task_number),file),
                    path_out=pathlib.Path(AnsPdf_path, str(i+start_bil_number)))
        
        for i in range(len(all_files_solutions)):
            for file in all_files_solutions[i]:
                copy_file(
                    path_in=pathlib.Path(Base_path, "Q" + str(task_number), file),
                    path_out=pathlib.Path(AnsPdf_path, "trash"))
        
        base_bils += all_tasks
        base_answers += all_answers
        bils = [bils[i] + "\\item\n" + current_tasks[i] + 2 * "\n" for i in range(number_of_bils)]
        answers = [answers[i] + "\\item\n" + current_tasks[i] + "\n\n" + current_answers[i] + 2 * "\n" for i in
                   range(number_of_bils)]


    references = read_file(pathlib.Path(Base_path, "Qend", "references.txt"))

    all_bils_tex_code += "\n\n".join([r"\section{Билет " + str(start_bil_number + i) + "}\n\n" + \
                             bils[i][bils[i].find(r"\begin{enumerate}"):] + "\n\\end{enumerate}" \
                             for i in range(number_of_bils)]) + references.replace(r"\end{enumerate}", "")

    all_answers_tex_code += "\n\n".join([r"\section{Билет " + str(start_bil_number + i) + "}\n\n" + \
                                answers[i][answers[i].find(r"\begin{enumerate}"):] + "\n\\end{enumerate}" \
                                for i in range(number_of_bils)]) + references.replace(r"\end{enumerate}", "")
    base_bils += "\n" + r"\end{enumerate}" + "\n" + "\end{document}"
    base_answers += "\n" + r"\end{enumerate}" + "\n" + "\end{document}"
    bils = [bils[i] + references + 2 * "\n" for i in range(number_of_bils)]
    answers = [answers[i] + references + 2 * "\n" for i in range(number_of_bils)]


    create_pdf(bils, answers, start_bil_number = start_bil_number,
               BilPdf_path = BilPdf_path, AnsPdf_path = AnsPdf_path,
               bil_prefix=bil_prefix, ans_prefix=ans_prefix)
    write_pdf(tex_code=base_bils, folder_path=pathlib.Path(BilPdf_path, "trash"),
              file_name="base_bil_all")
    write_pdf(tex_code=base_answers, folder_path=pathlib.Path(AnsPdf_path, "trash"),
              file_name="base_ans_all")
    write_pdf(tex_code=all_bils_tex_code, folder_path=pathlib.Path(BilPdf_path, "trash"),
              file_name="bil_all")
    write_pdf(tex_code=all_answers_tex_code, folder_path=pathlib.Path(AnsPdf_path, "trash"),
              file_name="ans_all")
    replace_pdf(folder_path=BilPdf_path, prefix=bil_prefix, save_tex=True, global_files=["bil_all", "base_bil_all"])
    replace_pdf(folder_path=AnsPdf_path, prefix=ans_prefix, save_tex=True, global_files=["ans_all", "base_ans_all"])
    shutil.rmtree(pathlib.Path(AnsPdf_path, "trash"))
    shutil.rmtree(pathlib.Path(BilPdf_path, "trash"))

    gen_exam(number_of_bils=2, 
         start_bil_number=101, 
         number_of_tasks=6, 
         signature_graphics = ["Approved.png", "Prepared.png"])