"""
Date - 02-08-2023
Developer - scihack/powerpizza
Purpose - to sort the txt unsorted data in a excel file.
"""


import tkinter, json
from tkinter import *
from tkinter import filedialog, messagebox
from string_helper_funcs import *
from other_functions import *
from openpyxl import workbook
from openpyxl.styles import Alignment, PatternFill
import webbrowser

print("Starting . . . .")
root = tkinter.Tk()
root.geometry("900x600")
root.title("Result Analyzer")
root.state("zoomed")
root.iconphoto(True, PhotoImage(file="software_icon.png", master=root))

# --------------- constants and variables ------------
selected_file = None
subject_by_code = json.load(open("subject_code_refer.json", "r"))
prv_next_step = 2
configs_ = json.load(open("configs.json", "r"))
file_lines = None
all_processed_data = None
status_area_frame = None
# --------------------- END -----------------------

# ----------------- functions of DRY --------------
def extract_first_line(line_):
    # First line includes roll number, name, subject codes, grades, pass or fail
    to_ret = {
        "roll_no": None,
        "name": "",
        "subject_codes": [],
        "result": "",
        "comp_subjects": []
    }
    # extracting roll number.
    line_chunks = list_formatter(line_.split(" "))
    to_ret["roll_no"] = int(line_chunks[0])

    # extracting name and subject code format
    name_done = False
    for xo in range(1, len(line_chunks)):
        if line_chunks[xo] == "COMP":
            break
        if line_chunks[xo].replace(" ", "").isnumeric():
            to_ret["subject_codes"].append(line_chunks[xo])
            name_done = True  # it's obvious by valid data format that if subject code is there so name should have been done.
        else:
            if not name_done:
                to_ret["name"] += " "+line_chunks[xo]

    # extracting gender from name
    gender_n_name = list_formatter(to_ret["name"].split(" "))
    if "F" in gender_n_name[0]:
        to_ret["gender"] = "Female"
    elif "M" in gender_n_name[0]:
        to_ret["gender"] = "Male"
    gender_n_name.pop(0)
    to_ret["name"] = " ".join(gender_n_name)

    # extracting result pass or fail
    to_ret["result"] = line_chunks[-1]

    if "COMP" in line_chunks:
        to_ret["result"] = "COMP"
        comp_subjs = line_chunks[line_chunks.index("COMP")+1: ]
        for itm in comp_subjs:
            to_ret["comp_subjects"].append(f"{subject_by_code[itm]['Name']} ({itm})")

    return to_ret


def subcode_to_subname(code_list):
    to_ret = []
    for itm in code_list:
        to_ret.append(subject_by_code[itm]["Name"])
    return to_ret

# -------------------- END -----------------------

header_canva = Canvas(root, bg="#FFFFFF", highlightthickness=2, highlightbackground="#000000")
def on_add_data_file():
    global selected_file, status_area_frame
    if status_area_frame:
        status_area_frame = status_area_frame.destroy()

    selected_file = filedialog.askopenfile("r", filetypes=[("text files", "*.txt")])
    if selected_file:
        try:
            status_area_frame = begin_status()
        except BaseException as e:
            messagebox.showerror("Invalid File", f"File format is invalid please provide a valid file.\nerror : {e}")

add_data_file_opt = Button(header_canva, text="Add Data File", font=("Helvetica", 12), command=on_add_data_file)
add_data_file_opt.pack(padx=2, pady=2, side=LEFT)


def on_export_data():
    if not selected_file:
        messagebox.showerror("Failed", "Please import some data first.")
        return

    export_file = filedialog.asksaveasfile(filetypes=(("Excel file", "*.xlsx"), ("JSON files", "*.json"), ("All files", "*.*")), defaultextension=".xlsx")
    if not export_file:
        return

    if export_file and export_file.name.endswith(".json"):
        to_write = {}
        idx = 0
        for itm in all_processed_data:
            idx += 1
            to_write[f"Student_{idx}"] = itm
        json.dump(to_write, export_file)
        export_file.close()
        # print(export_file.name)

    elif export_file and export_file.name.endswith(".xlsx"):
        dominant_subjects = configs_["dominant_subjects"]
        available_sub_code = {}
        for datas_ in all_processed_data:
            available_sub_code = set(list(available_sub_code) + datas_["subject_codes_format"])

        for sub_code in available_sub_code:  # dominant subjects first then left subjects like first science then commerence etc.. at last some subjects like germany language etc.
            if sub_code not in dominant_subjects:
                dominant_subjects.append(sub_code)

        for sub_code2 in dominant_subjects.copy():  # removing all the dominant subjects which do not exist in any student's result generally physiology
            if sub_code2 not in available_sub_code:
                dominant_subjects.remove(sub_code2)
        available_sub_code = dominant_subjects

        available_sub_name = subcode_to_subname(available_sub_code)

        wb = workbook.Workbook()
        ws = wb.active
        subject_wise_columns = {}

        # ------------------ EXCEL DATASHEET FORMAT MAKING ------------------
        top_front_cols = ["Roll No.", "Student Name", "Gender", ""]
        ws.append(top_front_cols)

        h1 = 0
        for itm in available_sub_name:  # top middle cols
            ws.merge_cells(start_row=1, end_row=1, start_column=len(top_front_cols)+h1, end_column=len(top_front_cols)+h1+1)
            cell_to_edit = ws.cell(row=1, column=h1 + len(top_front_cols))
            cell_to_edit.value = itm
            cell_to_edit.alignment = Alignment(horizontal="center")
            ws.cell(row=2, column=cell_to_edit.col_idx, value="Marks")
            ws.cell(row=2, column=cell_to_edit.col_idx + 1, value="Grade")
            subject_wise_columns[itm] = {"column_idx": cell_to_edit.col_idx}
            h1 += 2

        top_back_cols = ["Max Marks", "Marks Obtain", "Best (5)\n(Best4 + English)" ,"Percentage all", "Average all", "Result", "Compartment"]
        cols_best_sub = ["Max Marks", "Marks Obtain", "Percentage", "Average"]

        result_column_index = None
        col_indexer = len(list(ws.iter_rows(0, 1))[0])+1
        for itm2 in top_back_cols:
            if itm2 == top_back_cols[2]:
                ws.merge_cells(start_row=1, end_row=1, start_column=col_indexer, end_column=col_indexer+3)
                ws.cell(1, col_indexer).value = itm2
                ws.cell(1, col_indexer).alignment = Alignment("center")

                for itm3 in cols_best_sub:
                    ws.cell(2, col_indexer).value = itm3
                    col_indexer += 1
            else:
                col_indexer += 1
                ws.cell(1, col_indexer).value = itm2
                if itm2 == "Result":
                    result_column_index = ws.cell(1, col_indexer).column
        # ----------------------------- END -------------------------------


        # ------------------------ DATA WRITING ----------------------------
        starting_row = 3
        row_indexer = 0
        for info in all_processed_data:  # adds data student wise
            row_indexer += 1
            ws.cell(starting_row, 1, info["roll_no"])
            ws.cell(starting_row, 2, info["student_name"])
            ws.cell(starting_row, 3, info["gender"])

            for sub_code in info["CMG"]:
                mg_sub_col = subject_wise_columns[subject_by_code[sub_code]["Name"]]["column_idx"]
                ws.cell(starting_row, mg_sub_col, info["CMG"][sub_code]["marks"]).alignment = Alignment(horizontal="right")
                ws.cell(starting_row, mg_sub_col+1, info["CMG"][sub_code]["grade"]).alignment = Alignment(horizontal="right")

            row_len = len(list(ws.iter_rows(starting_row, starting_row))[0]) - len(top_back_cols + cols_best_sub) + 1

            if configs_["main_subject_code"] not in info["subject_codes_format"]:
                messagebox.showerror("Invalid Main Subject Code", f"Main subject is not present in entry {row_len}\nPlease provide a main subject code which is common in all entries.")
                return
            elif configs_["max_best_sub_range"] > len(info["subject_codes_format"]):
                messagebox.showerror("out of range", "Max best subject range is out of range please enter valid values.")
                return

            if info["result"] != "ABST":
                marks_no_main_sub = info["marks"]
                marks_no_main_sub.pop(info["subject_codes_format"].index(str(configs_["main_subject_code"])))
                best_sub_total = [info["CMG"][str(configs_["main_subject_code"])]["marks"]] + sorted(marks_no_main_sub)[-(configs_["max_best_sub_range"]-1): ]
                # best_sub_total - change index -4 to the n for which you want to take subjects n is the no. of subjects

                mm_total = configs_["max_marks_1_subject"] * len(info["subject_codes_format"])
                mm_best_sub = configs_["max_marks_1_subject"] * configs_["max_best_sub_range"]

                data_end_row = [mm_total, info["total_marks"], mm_best_sub, sum(best_sub_total) , "%.1f" % (sum(best_sub_total)/(configs_["max_marks_1_subject"]*configs_['max_best_sub_range'])*100),
                                "%.1f" % (sum(best_sub_total) / configs_['max_best_sub_range']), "%.1f" % info["percentage"],
                                "%.1f" % info["average"], info["result"], ", ".join(info["comp_subjects"])]  # data W.R.T top_back_cols.
                for itm4 in data_end_row:
                    row_len += 1
                    ws.cell(starting_row, row_len, itm4)

            if info["result"] == "COMP":
                for itm in ws[starting_row]:
                    itm.fill = PatternFill(start_color="ffd000", end_color="ffd000", fill_type="solid")
            elif info["result"] == "ABST":
                ws.cell(starting_row, result_column_index, info["result"])
                for itm in ws[starting_row]:
                    itm.fill = PatternFill(start_color="ff866e", end_color="ff866e", fill_type="solid")
            starting_row += 1

        starting_row += 1
        ws.merge_cells(start_row=starting_row, end_row=starting_row, start_column=1, end_column=3)
        cell_total_std = ws.cell(starting_row, 1, f"Total Student : {len(all_processed_data)}")
        cell_total_std.fill = PatternFill(start_color="FFFF00", end_color="CDFFBD", fill_type="solid")

        starting_row += 1
        ws.merge_cells(start_row=starting_row, end_row=starting_row, start_column=1, end_column=3)
        cell_sub_total = ws.cell(starting_row, 1, f"Subject Total(s)")
        cell_sub_total.fill = PatternFill(start_color="FFFF00", end_color="CDFFBD", fill_type="solid")

        ws.merge_cells(start_row=starting_row+1, end_row=starting_row+1, start_column=1, end_column=3)
        cell_sub_avg = ws.cell(starting_row, 1, f"Subject Average(s)")
        cell_sub_avg.fill = PatternFill(start_color="FFFF00", end_color="CDFFBD", fill_type="solid")

        for sub_idx in subject_wise_columns:
            one_sub_total = list(ws.iter_cols(subject_wise_columns[sub_idx]["column_idx"], subject_wise_columns[sub_idx]["column_idx"], 3))[0] # starting reading marks from row 2 to end.
            sum_marks = 0
            no_of_students = 0 # no of student own the subject
            for nums in one_sub_total:
                if nums.value and str(nums.value).isnumeric():
                    sum_marks += int(nums.value)
                    no_of_students += 1
            if not no_of_students : no_of_students = 1

            ws.cell(starting_row-1, subject_wise_columns[sub_idx]["column_idx"], sum_marks)
            ws.cell(starting_row, subject_wise_columns[sub_idx]["column_idx"], '%.1f' % (sum_marks/no_of_students))
        # ----------------------- END ---------------------------------
        wb.save(export_file.name)


    messagebox.showinfo("Successful", "File saved.")


export_data_file_opt = Button(header_canva, text="Export Data File", font=("Helvetica", 12), command=on_export_data)
export_data_file_opt.pack(padx=2, pady=2, side=LEFT)

def on_configs():
    configs_opt.config(state="disabled")

    config_canva = Canvas(content_left_canva, bg="#FFFFFF", highlightthickness=2, highlightbackground="#000000")
    def on_close_config():
        config_canva.destroy()
        configs_opt.config(state="normal")
    btn_close = Button(config_canva, text="Close", bg="#FF0000", fg="#FFFFFF", activebackground="#FF0000", activeforeground="#FFFFFF", command=on_close_config)
    btn_close.pack(anchor="e", pady=2)

    lbl_configs = Label(config_canva, text="Global Configurations", font=("Arial", 16, "bold", "underline"), bg="#FFFFFF")
    lbl_configs.pack(pady=2)

    # ---------------------- ADD SUBJECT EDITOR -------------------------
    sub_name_var = StringVar()
    sub_code_var = StringVar()

    frame_add_sub = Frame(config_canva, bg="#FFFFFF", highlightthickness=1, highlightbackground="#000000")
    lbl_add_sub = Label(frame_add_sub, text="Global Subject Code", bg="#FFFFFF", font=("Arial", 14))
    lbl_add_sub.pack(anchor="nw")

    frame_add_sub_E1 = Frame(frame_add_sub, bg="#FFFFFF")
    lbl_code = Label(frame_add_sub_E1, text="Subject Code", bg="#FFFFFF", font=("Arial", 12))
    lbl_code.pack(side=LEFT)
    entry_code = Entry(frame_add_sub_E1, highlightthickness=1, highlightcolor="#0000FF", textvariable=sub_code_var)
    entry_code.pack(side=LEFT)
    frame_add_sub_E1.pack()

    frame_add_sub_E2 = Frame(frame_add_sub, bg="#FFFFFF")
    lbl_name = Label(frame_add_sub_E2, text="Subject Name", bg="#FFFFFF", font=("Arial", 12))
    lbl_name.pack(side=LEFT)
    entry_name = Entry(frame_add_sub_E2, highlightthickness=1, highlightcolor="#0000FF", textvariable=sub_name_var)
    entry_name.pack(side=LEFT)
    frame_add_sub_E2.pack()

    frame_add_sub_o1 = Frame(frame_add_sub, bg="#FFFFFF")
    def on_add_sub():
        # subject_by_codes has already loaded the subject_code_refer file but that variable is editing some value in runtime so that below I again loading the file.
        all_subject_by_codes = json.load(open("subject_code_refer.json", "r"))
        if sub_code_var.get() in all_subject_by_codes:
            if not messagebox.askokcancel("Already exists", f"This code already exist with subject name {all_subject_by_codes[sub_code_var.get()]['Name']} do you like to change it with {sub_name_var.get()}?"):
                return
        all_subject_by_codes[sub_code_var.get()] = {"Name": sub_name_var.get()}
        json.dump(all_subject_by_codes, open("subject_code_refer.json", "w"))
        messagebox.showinfo("successful", "subject added successfully RESTART the software to commit changes.")

    add_sub = Button(frame_add_sub_o1, text="Add", bg="#90EE90", width=14, command=on_add_sub)
    add_sub.pack(side=LEFT)

    def on_remove_sub():
        # subject_by_codes has already loaded the subject_code_refer file but that variable is editing some value in runtime so that below I again loading the file.
        all_subject_by_codes = json.load(open("subject_code_refer.json", "r"))
        if sub_code_var.get() in all_subject_by_codes:
            del all_subject_by_codes[sub_code_var.get()]
            json.dump(all_subject_by_codes, open("subject_code_refer.json", "w"))
            messagebox.showinfo("successful", f"subject deleted successfully RESTART the software to commit changes.")
        else:
            messagebox.showerror("Not fount", f"No subject with code {sub_code_var.get()} found.")
    remove_sub = Button(frame_add_sub_o1, text="Remove", bg="#ffcccb", width=14, command=on_remove_sub)
    remove_sub.pack(side=LEFT)
    frame_add_sub_o1.pack()

    frame_add_sub.pack(padx=3, pady=2, anchor="w", ipadx=10)
    # -------------------------------- END ---------------------------------------


    # ------------------------- EDIT MAX MARKS CONSTANT -----------------------
    mm_text_var = IntVar(value=configs_["max_marks_1_subject"])
    frame_edit_mm = Frame(config_canva, bg="#FFFFFF", highlightthickness=1, highlightbackground="#000000")
    lbl_edit_mm = Label(frame_edit_mm, text="Global Max Marks Per Subject", bg="#FFFFFF", font=("Arial", 14))
    lbl_edit_mm.pack(anchor="nw")

    frame_edit_mm_E1 = Frame(frame_edit_mm, bg="#FFFFFF")
    lbl_max_marks = Label(frame_edit_mm_E1, text="Max Marks of Single Subject", bg="#FFFFFF", font=("Arial", 12))
    lbl_max_marks.pack(side=LEFT)
    entry_max_marks = Entry(frame_edit_mm_E1, highlightthickness=1, highlightcolor="#0000FF", textvariable=mm_text_var)
    entry_max_marks.pack(side=LEFT)
    frame_edit_mm_E1.pack()

    def on_save_mm():
        configs_["max_marks_1_subject"] = mm_text_var.get()
        json.dump(configs_, open("configs.json", "w"))
        messagebox.showinfo("Successful", f"Changed max marks to {configs_['max_marks_1_subject']}")

    save_mm =Button(frame_edit_mm, text="Save", bg="#90EE90", width=14, command=on_save_mm)
    save_mm.pack()

    frame_edit_mm.pack(padx=3, pady=2, anchor="w", ipadx=10)

    # --------------------------------- END ------------------------------


    # -------------------------- EDIT MAIN SUBJECT CODE ----------------
    main_sub_name = StringVar(value=configs_["main_subject_code"])

    frame_edit_MS = Frame(config_canva, bg="#FFFFFF", highlightthickness=1, highlightbackground="#000000")
    lbl_edit_MS = Label(frame_edit_MS, text="Global Main Subject", bg="#FFFFFF", font=("Arial", 14))
    lbl_edit_MS.pack(anchor="nw")

    frame_edit_MS_E1 = Frame(frame_edit_MS, bg="#FFFFFF")
    lbl_main_subject = Label(frame_edit_MS_E1, text="Main Subject", bg="#FFFFFF", font=("Arial", 12))
    lbl_main_subject.pack(side=LEFT)
    menu_subjects = OptionMenu(frame_edit_MS_E1, main_sub_name, *subject_by_code.keys())
    menu_subjects.pack(side=LEFT)
    frame_edit_MS_E1.pack()

    def on_save_mm():
        configs_["main_subject_code"] = main_sub_name.get()
        json.dump(configs_, open("configs.json", "w"))
        messagebox.showinfo("Successful", f"Changed main subject to {configs_['main_subject_code']}")

    save_mm = Button(frame_edit_MS, text="Save", bg="#90EE90", width=14, command=on_save_mm)
    save_mm.pack()

    frame_edit_MS.pack(padx=3, pady=2, anchor="w", ipadx=10)

    # ------------------------------- END ------------------------------

    # -------------------------- EDIT MAX BEST SUBJECT RANGE ----------------
    max_best_subs = IntVar(value=configs_["max_best_sub_range"])

    frame_edit_MBS = Frame(config_canva, bg="#FFFFFF", highlightthickness=1, highlightbackground="#000000")
    lbl_edit_MBS = Label(frame_edit_MBS, text="Global Max Best Subject Range", bg="#FFFFFF", font=("Arial", 14))
    lbl_edit_MBS.pack(anchor="nw")

    frame_edit_MBS_E1 = Frame(frame_edit_MBS, bg="#FFFFFF")
    lbl_best_subjects = Label(frame_edit_MBS_E1, text="Max Best Subject Range\n(include 1 main subject)", bg="#FFFFFF", font=("Arial", 12))
    lbl_best_subjects.pack(side=LEFT)
    entry_best_subjects = Entry(frame_edit_MBS_E1, highlightthickness=1, highlightcolor="#0000FF", textvariable=max_best_subs)
    entry_best_subjects.pack(side=LEFT)
    frame_edit_MBS_E1.pack()

    def on_save_mm():
        configs_["max_best_sub_range"] = max_best_subs.get()
        json.dump(configs_, open("configs.json", "w"))
        messagebox.showinfo("Successful", f"Changed max best subjects range to {configs_['max_best_sub_range']}")

    save_mm = Button(frame_edit_MBS, text="Save", bg="#90EE90", width=14, command=on_save_mm)
    save_mm.pack()

    frame_edit_MBS.pack(padx=3, pady=2, anchor="w", ipadx=10)
    # ------------------------------- END ------------------------------


    # ------------------------- Dominant subjects ----------------------
    dominant_subs_csv = StringVar(value=",".join(configs_["dominant_subjects"]))

    frame_edit_DS = Frame(config_canva, bg="#FFFFFF", highlightthickness=1, highlightbackground="#000000")
    lbl_edit_DS = Label(frame_edit_DS, text="Global Dominant Subject", bg="#FFFFFF", font=("Arial", 14))
    lbl_edit_DS.pack(anchor="nw")

    frame_edit_DS_E1 = Frame(frame_edit_DS, bg="#FFFFFF")
    lbl_dominant_subject = Label(frame_edit_DS_E1, text="Dominant Subjects\n(separated by ',')", bg="#FFFFFF", font=("Arial", 12))
    lbl_dominant_subject.pack(side=LEFT)
    dominant_subject = Entry(frame_edit_DS_E1, textvariable=dominant_subs_csv, highlightthickness=1, highlightcolor="#0000FF")
    dominant_subject.pack(side=LEFT)
    frame_edit_DS_E1.pack()

    def on_save_mm():
        configs_["dominant_subjects"] = list_formatter(dominant_subs_csv.get().replace(" ", "").split(","))
        for cds in configs_["dominant_subjects"]:
            if cds not in subject_by_code:
                messagebox.showerror("Failed", f"Subject code '{cds}' not exists please add this subject code first.")
                return
        json.dump(configs_, open("configs.json", "w"))
        messagebox.showinfo("Successful", f"Successfully edited dominant subjects.")

    save_DS = Button(frame_edit_DS, text="Save", bg="#90EE90", width=14, command=on_save_mm)
    save_DS.pack()

    frame_edit_DS.pack(padx=3, pady=2, anchor="w", ipadx=10)
    # ------------------------- END ------------------------------------

    config_canva.place(x=0, y=0, relwidth=1.0, relheight=1.0)

configs_opt = Button(header_canva, text="Config", font=("Helvetica", 12), command=on_configs)
configs_opt.pack(padx=2, pady=2, side=LEFT)


def on_click_about():
    about_opt.config(state="disabled")

    text_to_show = """
    ------------------------------- Function of software --------------------------------
    This software is personally build for sort and structuring data of CBSE board examinations result of students. It requires a txt file 
    which contain data in a format describe below then this software will sort students, their gender, their roll number and
    percentage average etc. Sorted data can be exported as an Excel or JSON file.
    
    ------------------------------- Data format required --------------------------------
    DATA_LINE1 :- ROLL_NO GENDER STUDENT_NAME SUB_CODE1 SUB_CODE2 SUB_CODE3......SUB_CODE(n) GRADE1 GRADE2 GRADE3 RESULT COMPARTMENT_SUBJECT_CODES
    DATA_LINE2 :- SUB1_MARKS SUB1_GRADE SUB2_MARKS SUB2_GRADE ...... SUB(n)_MARKS SUB(n)_GRADE
    
    > how should be DATA_LINE1 ?
    1. ROLL_NO must be of 7 digits only.
    2. Gender M for male, F for female
    3. NAME can contain white spaces.
    4. SUB_CODE1 to infinity works just remember that DATA_LINE2 should contain marks and grade of SUB_CODE(n) in proper format.
    5. (optional) GRADE1 GRADE2 GRADE3 not actually required software works same if its present of not.
    6. RESULT it should be FAIL or PASS or COMP or ABST and its required.

    > how should be DATA_LINE2
    1. SUB(n)_MARKS and SUB(n)_GRADE represents the marks and grade with respect to SUB_CODE(n).
    
    Note : DATA_LINE1 and DATA_LINE2 both are required if any of one missing so software will delete that entry and proceed for next proper paired data lines.
    
    ------------------------------- Configurations --------------------------------
    1. Global Subject Code : Here you can add new subject code and its name in software.
        
    2. Global Max Marks Per Subject : It represents the max marks of which paper held. Like a student got 40 out of 80 so 80
    is the max marks. It will be same for all subjects.
    
    3. Global Main Subject : It represents the main subject which is common in all the sides for example english is language
    subject which is same for all the fields (science, arts etc.).
    
    4. Global Max Best Subject Range : It represents how many top best subject marks of a student will be consider for
    calculate variable columns like average(n), percentage(n) etc. its value should be no_of_best_subjects + 1
    for example : 4 + 1 = 5 where no_of_best_subjects = 4 and the 1 here for english/main subject so value of GLOBAL will be 5.
    
    5. Global Dominant Subjects : Its helps to control the column format of table like if we want subject format english
    then Physics chemistry .... so we can use this entry to do that. Just provide subject codes and seperate them
    using ','.
    """

    about_canva = Canvas(content_left_canva, bg="#FFFFFF", highlightthickness=2, highlightbackground="#000000")
    def on_close_about():
        about_canva.destroy()
        about_opt.config(state="normal")
    btn_close = Button(about_canva, text="Close", bg="#FF0000", fg="#FFFFFF", activebackground="#FF0000", activeforeground="#FFFFFF", command=on_close_about)
    btn_close.pack(anchor="e", pady=2)

    lbl_about_head = Label(about_canva, text="About", bg="#FFFFFF", font=("Arial", 18, "bold", "underline"))
    lbl_about_head.pack()

    text_ar = Text(about_canva, highlightthickness=1, highlightcolor="#000000", bg="#FFFFFF", fg="#000000", font=("Arial", 12))
    text_ar.insert(END, text_to_show)
    text_ar.config(state="disabled")
    text_ar.focus()
    text_ar.pack(fill=BOTH, padx=3, expand=True)

    def on_developer():
        webbrowser.open("https://github.com/PowerPizza")

    btn_developer = Button(about_canva, text="DEVELOPER", bg="blue", fg="yellow", command=on_developer)
    btn_developer.pack(anchor="e", pady=3, padx=3)

    about_canva.place(x=0, y=0, relwidth=1.0, relheight=1.0)


about_opt = Button(header_canva, text="About", font=("Helvetica", 12), command=on_click_about)
about_opt.pack(padx=2, pady=2, side=LEFT)

label_imported_file = Label(header_canva, text="", font=("Helvetica", 12), bg="#FFFFFF")
label_imported_file.pack(side=LEFT, pady=2, padx=2)
header_canva.pack(fill=X, ipadx=2, ipady=2, padx=2, pady=1)

content_left_canva = Canvas(root, bg="#FFFFFF", highlightthickness=2, highlightbackground="#000000")

def begin_status():
    global file_lines, all_processed_data
    file_lines = list(map(lambda data_: rm_extra_spaces(data_.replace("\n", "")), selected_file.readlines()))
    for line in file_lines.copy():
        if len(line) < 3:
            file_lines.remove(line)

    l1 = 0
    while l1 < len(file_lines):
        if len(file_lines[l1].split(" ")[0]) >= 7 and file_lines[l1].split(" ")[0].isnumeric():  # STARTSWITH ROLL NO CHECK (data line 1)
            if (len(file_lines[l1 + 1].split(" ")[0]) == 3 and file_lines[l1 + 1].split(" ")[0].isnumeric()) or (file_lines[l1].split(" ")[-1] == "ABST" and (len(file_lines[l1 + 1].split(" ")[0]) < 5)):  # STARTSWITH SUBJECT CODE CHECK (data line 2)
                l1 += 2
            else:
                messagebox.showwarning("unknown row", f"Data line 2 not found or garbage value exists between data lines\n Error At: {file_lines[l1]}")
                file_lines.pop(l1)
        else:
            file_lines.pop(l1)

    frame_status_area = Frame(content_left_canva, bg="#FFFFFF")
    lbl_file_name = Label(frame_status_area, text=f"File {selected_file.name}", bg="#FFFFFF", font=("Arial", 14))
    lbl_file_name.pack()

    i = 0
    def d_processor(proc_from=0, proc_to=len(file_lines)):
        for c1 in range(proc_from, proc_to, prv_next_step):
            processed_data = {
                "total_marks": "ABSENT",
                "average": "ABSENT",
                "percentage": "ABSENT",
                "lowest": "ABSENT",
                "highest": "ABSENT",
                "comp_subjects": "ABSENT"
            }
            data_no_spcs = file_lines[c1]

            data_stage_1 = extract_first_line(data_no_spcs)

            data_no_spcs2 = rm_extra_spaces(file_lines[c1 + 1]).replace("\n", "").split(" ")
            data_no_spcs2 = list_formatter(data_no_spcs2)

            processed_data["student_name"] = data_stage_1["name"]
            processed_data["gender"] = data_stage_1["gender"]
            processed_data["roll_no"] = data_stage_1["roll_no"]
            processed_data["subject_codes_format"] = data_stage_1["subject_codes"]
            processed_data["CMG"] = {}
            processed_data["marks"] = []
            processed_data["grades"] = []

            for k1 in range(len(data_no_spcs2) // 2):
                if data_stage_1["result"] == "ABST":
                    processed_data["CMG"][data_stage_1["subject_codes"][k1]] = {"marks": data_no_spcs2[k1 * 2],
                                                                                "grade": data_no_spcs2[k1 * 2 + 1]}
                    processed_data["marks"].append(data_no_spcs2[k1 * 2])
                    processed_data["grades"].append(data_no_spcs2[k1 * 2 + 1])
                else:
                    processed_data["CMG"][data_stage_1["subject_codes"][k1]] = {"marks": int(data_no_spcs2[k1 * 2]),
                                                                                "grade": data_no_spcs2[k1 * 2 + 1]}
                    processed_data["marks"].append(int(data_no_spcs2[k1 * 2]))
                    processed_data["grades"].append(data_no_spcs2[k1 * 2 + 1])

            processed_data["result"] = data_stage_1["result"]

            if data_stage_1["result"] != "ABST":
                processed_data["total_marks"] = sum(processed_data["marks"])
                processed_data["average"] = processed_data["total_marks"] / len(processed_data["marks"])
                processed_data["percentage"] = processed_data["total_marks"] / (configs_["max_marks_1_subject"] * len(processed_data["subject_codes_format"])) * 100

                processed_data["lowest"] = min(processed_data["marks"])
                processed_data["highest"] = max(processed_data["marks"])
                processed_data["comp_subjects"] = data_stage_1["comp_subjects"]

            yield processed_data

    def data_processor():
        data_line = list(d_processor(i, i+1))[0]

        set_roll_no.set(data_line["roll_no"])
        set_name.set(data_line["student_name"])

        sub_code_pattern = data_line["subject_codes_format"]
        def load_mg_entries():
            # it helps to load the entries and their label w.r.t subject codes in frame_mg_scd.
            nonlocal frame_mg_scd
            if frame_mg_scd:
                frame_mg_scd.destroy()
            frame_mg_scd = Frame(frame_mg_pri, bg="#FFFFFF")
            frame_mg_scd.pack(side=LEFT)
            for codes in sub_code_pattern:
                fr_row_mg = Frame(frame_mg_scd, bg="#FFFFFF")
                fr_column_m = Frame(fr_row_mg, bg="#FFFFFF")
                subject_by_code[codes]["marks_var"] = entry_creator(f'Marks {subject_by_code[codes]["Name"]}', "", master=fr_column_m)
                fr_column_m.pack(side=LEFT, padx=2)
                fr_column_g = Frame(fr_row_mg, bg="#FFFFFF")
                subject_by_code[codes]["grade_var"] = entry_creator(f'Grade {subject_by_code[codes]["Name"]}', "", master=fr_column_g)
                fr_column_g.pack(side=LEFT, padx=2)
                fr_row_mg.pack(anchor="nw")
        load_mg_entries()

        for j in range(len(data_line["marks"])):
            subject_by_code[sub_code_pattern[j]]["marks_var"].set(data_line["marks"][j])
            subject_by_code[sub_code_pattern[j]]["grade_var"].set(data_line["grades"][j])

        if data_line["result"] != "ABST":
            set_total_marks.set(data_line["total_marks"])
            set_percentage_marks.set("%.1f" % data_line["percentage"])
            set_average_marks.set("%.1f" % data_line["average"])
            set_lowest_marks.set(data_line["lowest"])
            set_highest_marks.set(data_line["highest"])

        lbl_page.config(text=f"Data Page : {i//2+1}")

    all_processed_data = list(d_processor())
    lbl_total_data = Label(frame_status_area, text=f"Total Data : {len(all_processed_data)}", bg="#FFFFFF", font=("Arial", 14))
    lbl_total_data.pack()

    result_area = Frame(frame_status_area, bg="#FFFFFF", highlightthickness=1, highlightbackground="#000000")
    def entry_creator( txt_, value_, master=result_area):
        text_var = StringVar(value=value_)
        frame_e1 = Frame(master, bg="#FFFFFF")
        lbl_entry = Label(frame_e1, text=txt_, font=("Helvetica", 12), bg="#FFFFFF")
        lbl_entry.pack(side=LEFT, padx=2)
        entry_e1 = Entry(frame_e1, textvariable=text_var, font=("Helvetica", 12), highlightthickness=1, highlightbackground="#000000")
        entry_e1.pack(side=LEFT, padx=2)
        frame_e1.pack(pady=2, fill=X)
        return text_var

    lbl_page = Label(result_area, text="Data Page : 0", font=("Helvetica", 12, "bold"), bg="#FFFFFF")
    lbl_page.pack(anchor="ne")

    set_roll_no = entry_creator("Roll. No.", "")
    set_name = entry_creator("Name", "")

    frame_mg_pri = Frame(result_area, bg="#FFFFFF")
    frame_mg_scd = None
    frame_mg_pri.pack(fill=X)

    set_total_marks = entry_creator("Marks Total", "")
    set_percentage_marks = entry_creator("Percentage", "")
    set_average_marks = entry_creator("Average", "")
    set_lowest_marks = entry_creator("Lowest", "")
    set_highest_marks = entry_creator("Highest", "")

    def on_prev():
        nonlocal i
        if i - prv_next_step > -1:
            button_next.config(state="normal")
            i -= prv_next_step
            data_processor()
        else:
            button_next.config(state="normal")
            button_prev.config(state="disabled")

    button_prev = Button(result_area, text="Previous", font=("Helvetica", 16), command=on_prev)
    button_prev.pack(side=LEFT, padx=1, pady=1)

    def on_next():
        nonlocal i
        if i + prv_next_step < len(file_lines):
            button_prev.config(state="normal")
            i+=prv_next_step
            data_processor()
        else:
            button_next.config(state="disabled")
            button_prev.config(state="normal")

    button_next = Button(result_area, text="Next", font=("Helvetica", 16), command=on_next)
    button_next.pack(side=RIGHT, padx=1, pady=1)

    result_area.pack(side=LEFT, anchor="nw", padx=12, fill=X, expand=True)
    data_processor()

    frame_status_area.pack(fill=BOTH, side=LEFT, expand=True, padx=2, pady=2)

    return frame_status_area

content_left_canva.pack(side=LEFT, fill=BOTH, expand=True, padx=2, pady=1)

root.mainloop()