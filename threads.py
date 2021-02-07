from tkinter import *
import sqlite3
import os
from tkinter import messagebox
from tkinter import filedialog
from PIL import ImageTk, Image


global root_pos_x, root_pos_y, loaded
new_window = None
loaded = "no"

# Create Database
conn = sqlite3.connect("threads.db")

# Create Cursor
c = conn.cursor()

# Create a Table DMC
##c.execute("""CREATE TABLE dmc (
##            name integer,
##            number integer
##        )
##""")
##
## Create a Table Anchor
##c.execute("""CREATE TABLE anchor (
##            name integer,
##            number integer
##        )
##""")

# Commit changes
conn.commit()

# Close Database
conn.close()

root = Tk()
root.title("Threads Database")
root.option_add('*Font', 'ComicSansMS 11')
root.geometry("500x600")
root.resizable(False, False)

##frame_color = "#923c66" PURPLE WINE
##entry_color = "#f3e6fa" LIGHT PURPLE
##color1 = "#f0d4ff"
##color2 = "#cda8e0"

##ffb3c6

frame_color = "#fbe4ea"
entry_color = "#fff5f7"
button_color = "#fca2b8"
color1 = "#fcc0cf"
color2 = "#ffd1dc"


##bg = PhotoImage(file = "/images/bg.png")

bg = ImageTk.PhotoImage(Image.open("images/bg_pink.jpg"))
bg_label = Label(root, image=bg)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

def info_popup(message):
    messagebox.showinfo("Info Box", message)

def warning_popup(warning):
    messagebox.showwarning("Warning", warning)

def clear_history():
    """Removes string in the output window"""
    output_text.configure(state="normal")
    output_text.delete(1.0, END)
    counter_update()
    output_text.configure(state="disabled")

def create_new_window(dmc, anchor):
    # Open new window and destroy existing one
    global new_window, root_pos_x, root_pos_y
    
    if new_window is not None:
        new_window.destroy()
    new_window = Toplevel()
    new_window.title("All records")
    new_window.configure(bg=frame_color)

    # Open new window relatively to main window
    root_pos_x = root.winfo_x()
    root_pos_y = root.winfo_y()
    new_window.geometry("+%d+%d" % (root_pos_x + 540, root_pos_y + 25))
    new_window.resizable(False, False)

    # Create output box in the new window
    output_text = Text(new_window, height=38, width=25, padx=5, pady=5, bg=entry_color)
    output_text.grid(row=0, column=0, padx=5, pady=1)

    # format records from the tables
    dmc_output_format = ""
    anchor_output_format = ""
    space = ""
    
    for record in dmc:
        space = " " * (6 - len(str(record[0])))
        dmc_output_format += f"dmc {record[0]}.{space}Number: {record[1]}\n"

    for record in anchor:
        space = " " * (6 - len(str(record[0])))
        anchor_output_format += f"anchor {record[0]}. Number: {record[1]}\n"

    final_output = "DMC Threads\n" + dmc_output_format + "\n\n" + "ANCHOR Threads\n" + anchor_output_format

    output_text.insert(END, final_output)

def database_start():
    # Create Database
    conn = sqlite3.connect("threads.db")
    # Create Cursor
    c = conn.cursor()
    return conn, c

def database_finish(connection):
    # Commit changes
    connection.commit()
    # Close Database
    connection.close()
    
def show_entry():
    """After click on "Change" radio button will appear entry box for number set"""
    global thread_number_entry
    entry_box_list = entry_box_frame.grid_slaves()

    if len(entry_box_list) == 2:
    # Thread number label
        thread_number_label = Label(entry_box_frame, text="Set Number:", bg=color1)    
        thread_number_label.grid(row=1, column=0)

    # Thread number Entry
        thread_number_entry = Entry(entry_box_frame, width=10, bg=entry_color)
        thread_number_entry.grid(row=1, column=1, padx=10, pady=10)

def hide_entry():
    """After click on the "Search" radio button will disapear entry box for number"""
    global thread_number_entry
    thread_number_entry.delete(0, END)
    entry_box_list = entry_box_frame.grid_slaves()
    if len(entry_box_list) == 4:
        entry_box_list[0].grid_forget()
        entry_box_list[1].grid_forget()

def sort_records_by_name(records_no_order):
    """Sorts records by its name in ascent order"""
    decimal_records = []
    non_decimal_records = []
    
    for name, number in records_no_order:
        if name.isdecimal():
            decimal_records.append([int(name), number])
        else:
            non_decimal_records.append([name, number])
    
    decimal_records.sort(key=lambda x: x[0])
    records = decimal_records + non_decimal_records

    return records
    

def show_all_records():
    """Prints every record from database to the output window"""
    conn, c = database_start()

    c.execute("SELECT * FROM dmc")
    dmc_records_no_order = c.fetchall()

    c.execute("SELECT * FROM anchor")
    anchor_records_no_order = c.fetchall()

    # Sorting records by its name in ascent order
    dmc_records = sort_records_by_name(dmc_records_no_order)
    anchor_records = sort_records_by_name(anchor_records_no_order)

    create_new_window(dmc_records, anchor_records)

    database_finish(conn)

def submit_action(search_change, thread_type, name, number):
    """Based on action type will search or change/add"""
    global loaded
    
    if loaded == "yes":
        clear_history()
        loaded = "no"
    if search_change == "search":
        search_action(thread_type, name)
    elif search_change == "change":
        change_add_action(thread_type, name, number)
    elif search_change == "delete":
        delete_action(thread_type, name)
    elif search_change == "plus_minus":
        plus_minus_action(thread_type, name, number)

def update_output_window(text):
    output_text.configure(state="normal")
    output_string = output_text.get("1.0", "end-1c")
    output_text.delete(1.0, END)
    output_format = f"{text}\n" + output_string
    output_text.insert(END, output_format)
    output_text.configure(state="disabled")

def plus_minus_action(thread_type, name, number):
    conn, c = database_start()

    if len(name) > 0:
        c.execute(f"SELECT number FROM {thread_type} WHERE name='{name}'")
        record = c.fetchall()

        if len(number) > 0:
            if len(record) > 0:
                number_record = list(record[0])[0]
                number_record += int(number)
                c.execute(f"UPDATE {thread_type} SET number={number_record} WHERE name='{name}'")

##                output_format = f"{thread_type} {name} was updated to {number_record}"
##                update_output_window(output_format)

                info_popup("The record successfully updated!")
                database_finish(conn)

                # Reopen all records if already opened
                if Toplevel.winfo_exists(new_window) == 1:
                    show_all_records()
            else:
                info_popup("No record found!")
        else:
            warning_popup("Invalid number!")
    else:
        warning_popup("Invalid name!")

def delete_action(thread_type, name):
    conn, c = database_start()

    # Executes only if the thread name is filled, else show popup
    if len(name) > 0:
        c.execute(f"SELECT * FROM {thread_type} WHERE name='{name}'")
        record = c.fetchall()

        # Delete only if there is any match record, else show popup
        if len(record) > 0:
            c.execute(f"DELETE FROM {thread_type} WHERE name='{name}'")
            info_popup(f"{thread_type} {name} successfully deleted!")

##            output_format = f"{thread_type} {name} deleted"
##            update_output_window(output_format)

            database_finish(conn)

            # Reopen all records if already opened
            if Toplevel.winfo_exists(new_window) == 1:
                show_all_records()
        else:
            info_popup("No record found!")
    else:
        warning_popup("Invalid name")

def regroup_window():
    # extract everything from the output window
    string = output_text.get("1.0", "end-2c")

    # Remove duplicated lines
    string_to_regroup = delete_duplicates(string)
    
    # split every line to the list of lines
    string_list = string_to_regroup.split("\n")

    # sort availible and not availible line into two lists
    availible = []
    not_availible = []
    for item in string_list:
        if "." in item:
            if item.split(".")[1] == " Not Available":
                not_availible.append(item)
            else:
                availible.append(item)
            
    output_text.configure(state="normal")
    output_text.delete(1.0, END)

    # print availible and not availible seperetly to the window
    for item in availible:
        output_text.insert(END, str(item) + "\n")

    output_text.insert(END, "\n")
        
    for item in not_availible:
        output_text.insert(END, str(item) + "\n")

    # Remove first line if its blank
    window_string = output_text.get("1.0", "end-1c")
    new_string = ""
    if window_string.split("\n")[0] == "":
        without_first_index = window_string.split("\n")[1:]
        new_string = "\n".join(without_first_index)
        
        output_text.delete(1.0, END)
        output_text.insert(END, new_string)
        
    output_text.configure(state="disabled")

def delete_duplicates(window_string):
    """Takes multiline string, removes same lines and returns new multiline string without duplicates"""
    lines = set(window_string.split("\n"))
    list_lines = list(lines)
    new_string = "\n".join(list_lines)

    return new_string

def search_action(thread_type, name):
    """Finds all records in the table based on the given thread type and name"""
    conn, c = database_start()

    # Search only if the entry box is filled, else show fail popup
    if len(name) > 0:
        c.execute(f"SELECT * FROM {thread_type} WHERE name='{name}'")
        
        records = c.fetchall()

        if len(name) <= 5:
            # Show any match record in the output window, else show popup and write "not available" to the output window
            if len(records) > 0:
                output_format = f"{thread_type} {records[0][0]}. Available: {records[0][1]}"
            else:
                info_popup("No record found!")
                output_format = f"{thread_type} {name}. Not Available."
            update_output_window(output_format)
            regroup_window()
            counter_update()
        else:
            warning_popup("The name is too long!")
    else:
        warning_popup("Invalid name entered!")

    database_finish(conn)

def change_add_action(thread_type, name, number):
    """Searches all records based on the given thread type and name. After decide next action -> change record or add new record"""
    conn, c = database_start()

    # Executes only if the thread name and thread number is filled, else popup
    if len(name) > 0:
        c.execute(f"SELECT * FROM {thread_type} WHERE name='{name}'")
        
        records = c.fetchall()

        # Decides to change record or add new one 
        if len(records) > 0:
            change_action(thread_type, name, number)
        else:
            add_action(thread_type, name, number)
    else:
        warning_popup("No name or number entered!")

    database_finish(conn)

def add_action(thread_type, name, number):
    conn, c = database_start()

    # Executes only when the thread number is filled, else popup
    if len(number) > 0 and int(number) >= 0:
        if len(name) <= 5:
            if len(number) <= 3:
                c.execute(f"INSERT INTO {thread_type} VALUES (:name, :number)",
                        {
                        "name": name,
                        "number": number,
                            }
                          )
                info_popup("The record successfully added!")

                # Show added info in the output window
##                output_format = f"{thread_type} {name} added!"
##                update_output_window(output_format)
                
                database_finish(conn)

                # Reopen all records if already opened
                if Toplevel.winfo_exists(new_window) == 1:
                    show_all_records()
            else:
                warning_popup("The number is too high!")
        else:
            warning_popup("Invalid name!")
    else:
        warning_popup("Invalid number!")

def change_action(thread_type, name, number):
    conn, c = database_start()

    # Executes only if changed number is positive and not longer than 3 decimal spaces
    if int(number) >= 0:
        if len(number) <= 3:
            c.execute(f"UPDATE {thread_type} SET number={number} WHERE name='{name}'")
            info_popup(f"{thread_type} {name} successfully updated!")
            database_finish(conn)

            # Show update info in the output window
##            output_format = f"{thread_type} {name} updated!"
##            update_output_window(output_format)

            # Reopen all records if already opened
            if Toplevel.winfo_exists(new_window) == 1:
                show_all_records()
        else:
            warning_popup("The number is too high!")
    else:
        warning_popup("The number cannot be negative!")

def save_history(name):
    if len(name) > 0:
        if not name.isnumeric():
            output_text.configure(state="normal")
            string_to_save = output_text.get("1.0", "end-1c")
            output_text.configure(state="disabled")

            # if history is there to save it is saved then to a file.
            if len(string_to_save) > 0:
                if not os.path.exists(f"/Users/patrik/Desktop/Thread_database/saved_files/{name}.txt"):
                    with open(f"/Users/patrik/Desktop/Thread_database/saved_files/{name}.txt", "w") as file:
                        file.write(string_to_save)
                    info_popup("History successfully saved!")
                else:
                    warning_popup("File with the same name already exists!")
            else:
                warning_popup("Nothing to save!")
        else:
            warning_popup("The name cannot be a number!")
    else:
        warning_popup("Write file name to the 'Thread name'")

def update_line(thread_type, name):
    """Changes line from the loaded file where is change in database and returns new line"""
    conn, c = database_start()

    c.execute(f"SELECT * FROM {thread_type} WHERE name='{name}'")
    records = c.fetchall()

    if len(records) > 0:
        new_name = f"{thread_type} {name}. Available: {records[0][1]}.\n"
    else:
        new_name = f"{thread_type} {name}. Not Available.\n"

    database_finish(conn)

    return new_name

def update_history(line):
    """Takes a line and split it into 'thread type' and its 'name'"""
    if "dmc" in line or "anchor" in line:
        full_name = line.split(".")[0]
        thread_type = full_name.split(" ")[0]
        name = full_name.split(" ")[1]

        new_line = update_line(thread_type, name)
    else:
        new_line = "\n"

    return new_line

def load_history():
    global loaded
    
    # Choose file and save its path to the "file_path"
    file_path = filedialog.askopenfilename(initialdir="/Users/patrik/Desktop/Thread_database/saved_files",
                                           title="Select a file",
                                           filetypes=(("txt files", "*.txt"), ("All files", "*.*")))

    if len(file_path) > 0:
        loaded = "yes"
        file_name = file_path.split("/")[-1]
        
        output_text.configure(state="normal")
        output_text.delete(1.0, END)

        # Read the file line by line and insert it to the output window
        with open(file_path, "r") as source:
            for line in source.readlines():
                # If there are any changes in the database it will automaticaly update loaded file with changes
                new_line = update_history(line)
                output_text.insert(END, new_line)

        counter_update()
        regroup_window()

        # Automaticaly save the changes into the file
        output_text.configure(state="normal")
        string_to_save = output_text.get("1.0", "end-1c")
        output_text.configure(state="disabled")

        with open(f"/Users/patrik/Desktop/Thread_database/saved_files/{file_name}", "w") as file:
            file.write(string_to_save)

def delete_file():
    # Choose file and save its path to the "file_path"
    file_path = filedialog.askopenfilename(initialdir="/Users/patrik/Desktop/Thread_database/saved_files",
                                           title="Select a file",
                                           filetypes=(("txt files", "*.txt"), ("All files", "*.*")))
    
    # If file exists extracts its name and remove it
    if len(file_path) > 0:
        file_name = file_path.split("/")[-1]
        
        os.remove(file_path)
        info_popup(f"{file_name} successfully deleted!")

def counter_update():
    string = output_text.get("1.0", "end-2c")
    number = string.count("Not Available")
    
    counter_label = Label(output_text, text=f"Not Available: {number}", bg=color1)
    counter_label.place(x=330, y=0)

def on_enter(e):
    e.widget['foreground'] = 'white'

def on_leave(e):
    e.widget['foreground'] = 'black'


# Tkinter Variables

thread_type = StringVar()
thread_type.set("dmc")

search_change_var = StringVar()
search_change_var.set("search")

# Create new window with all records
show_all_records()

# Create Frames

    # Thread type frame
thread_type_frame = LabelFrame(root, padx=10, pady=10, bg=frame_color, relief=SUNKEN)
thread_type_frame.grid(row=0, column=0, padx=5, pady=5)

    # Entry box frame
entry_box_frame = LabelFrame(root, padx=5, pady=5, bg=frame_color, relief=SUNKEN)
entry_box_frame.grid(row=0, column=1, padx=5, pady=5)

    # Search or Change radio Frame
search_change_frame = LabelFrame(root, padx=5, pady=5, bg=frame_color, relief=SUNKEN)
search_change_frame.grid(row=1, column=0, padx=5, pady=5)

    # Buttons frame
buttons_frame = LabelFrame(root, padx=5, pady=5, bg=frame_color, relief=SUNKEN)
buttons_frame.grid(row=1, column=1, padx=5, pady=5)

    # Output text frame
output_text_frame = LabelFrame(root, padx=5, pady=5, bg=frame_color, relief=SUNKEN)
output_text_frame.grid(row=2, column=0, columnspan=2, padx=25, pady=10)

    # Save/Load/delete/clear history frame
save_load_frame = LabelFrame(root, padx=5, pady=5, bg=frame_color, relief=SUNKEN)
save_load_frame.grid(row=3, column=0, columnspan=2, padx=14, pady=5)
    

# Create Radio buttons

    # thread types (dmc, anchor)
Radiobutton(thread_type_frame, text="DMC", variable=thread_type, indicator=0, value="dmc", padx=10, pady=11, bg=color1).grid(row=0, column=0, padx=15)
Radiobutton(thread_type_frame, text="Anchor", variable=thread_type, indicator=0, value="anchor", padx=4, pady=11, bg=color2).grid(row=1, column=0, padx=15)

    # search, change/add, delete radiobuttons
Radiobutton(search_change_frame, text="Search Thread", variable=search_change_var, indicator=0, value="search", command=hide_entry, padx=5, pady=5, bg=color1).grid(row=0, column=0)
Radiobutton(search_change_frame, text="Change/Add", variable=search_change_var, indicator=0, value="change", command=show_entry, padx=12, pady=5, bg=color2).grid(row=1, column=0)
Radiobutton(search_change_frame, text="Delete Thread", variable=search_change_var, indicator=0, value="delete", command=hide_entry, padx=5, pady=5, bg=color1).grid(row=1, column=1)
Radiobutton(search_change_frame, text="Plus/Minus", variable=search_change_var, indicator=0, value="plus_minus", command=show_entry, padx=15, pady=5, bg=color2).grid(row=0, column=1)
    

# Create Entry boxes

    # Thread name Entry
thread_name_entry = Entry(entry_box_frame, width=10, bg=entry_color)
thread_name_entry.grid(row=0, column=1, padx=10, pady=10)

    # Thread number Entry (invisible default)
thread_number_entry = Entry(entry_box_frame, width=10)

# Create Buttons

    # Change/add, delete or Search button
search_change_button = Button(buttons_frame, text="Submit Action", highlightbackground=button_color,
                              command=lambda: submit_action(search_change_var.get(), thread_type.get(), thread_name_entry.get(), thread_number_entry.get()),
                              width=16, padx=5, pady=5)
search_change_button.grid(row=0, column=0, pady=3, padx=29)

    # Show whole database button
show_database_button = Button(buttons_frame, text="Show Every Record", command=show_all_records, width=16, padx=5, pady=5, highlightbackground=button_color)
show_database_button.grid(row=1, column=0, pady=3)

    # Show clear history button
clear_history_button = Button(save_load_frame, text="Clear History", command=clear_history, width=12, padx=5, pady=5, highlightbackground=button_color)
clear_history_button.grid(row=1, column=0, pady=3)

    # Save button
save_button = Button(save_load_frame, text="Save History", command=lambda: save_history(thread_name_entry.get()), width=12, padx=5, pady=5, highlightbackground=button_color)
save_button.grid(row=0, column=0, pady=3)

    # Load button
load_button = Button(save_load_frame, text="Load History", command=load_history, width=12, padx=5, pady=5, highlightbackground=button_color)
load_button.grid(row=0, column=1, pady=3)

    # Delete file button
delete_file_button = Button(save_load_frame, text="Delete file", command=delete_file, width=12, padx=5, pady=5, highlightbackground=button_color)
delete_file_button.grid(row=1, column=1, pady=3)

# Buttons hover binds

search_change_button.bind("<Enter>", on_enter)
search_change_button.bind("<Leave>", on_leave)

show_database_button.bind("<Enter>", on_enter)
show_database_button.bind("<Leave>", on_leave)

clear_history_button.bind("<Enter>", on_enter)
clear_history_button.bind("<Leave>", on_leave)

save_button.bind("<Enter>", on_enter)
save_button.bind("<Leave>", on_leave)

load_button.bind("<Enter>", on_enter)
load_button.bind("<Leave>", on_leave)

delete_file_button.bind("<Enter>", on_enter)
delete_file_button.bind("<Leave>", on_leave)

# Create Output Text Window

output_text = Text(output_text_frame, height=15, width=60, bg=entry_color)
output_text.grid(row=0, column=0, columnspan=2)
output_text.configure(state="disabled")

# Create Labels

    # Thread name label
thread_name_label = Label(entry_box_frame, text="Thread Name:", bg=color1)
thread_name_label.grid(row=0, column=0)

    # Counter label
counter_label = Label(output_text, text="Not Available: 0", bg=color1)
counter_label.place(x=330, y=0)





root.mainloop()

















