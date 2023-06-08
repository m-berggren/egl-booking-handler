import builtins
import threading
import tkinter as tk
from tkinter import ttk, messagebox

from eglhandler.src.sqlite.sqlite_db import SqliteDB
import egl_booking_handler.widget.test8 as test8

MS_DELAY = 1000  # Milliseconds between updates
FOREST_THEME = "forest-light.tcl"

window = tk.Tk()
window.option_add("*tearOff", False)

window.tk.call('source', FOREST_THEME)

style = ttk.Style(window)
style.theme_use('forest-light')

window.title("EVERGREEN")

content = ttk.Frame(window)

""" Set the window position. """

# Geometry: width x height + x_offset + y_offset
window.geometry("244x1009+-7+0")
window.resizable(False, False)

""" First crucial functions. """

def run_main_program():
    event_button.config(state=tk.DISABLED)
    delete_text()

    thread = threading.Thread(target=main.execute_parser)
    thread.start()
    
    window.after(MS_DELAY, check_if_ready, thread)

def run_no_voy_navis_program():
    no_voy_button.config(state=tk.DISABLED)
    delete_text()


    bookings = get_values_from_no_navis_bookings(no_voy_tree)

    thread = threading.Thread(target=test8.run_loop)
    thread.start()

    window.after(MS_DELAY, check_if_ready, thread)


""" Create the widgets. """

event_label = ttk.Label(content, text="Evergreen-bokningar", font=("Calibri Light", 16, "bold", "underline"), padding=(0, 5, 0, 5))
event_button = ttk.Button(content, text="Hantera bokningar", width=30, style="Accent.TButton", command=run_main_program)
event_text = tk.Text(content, width=32, height=20, font=("Calibri Light", 10), border=3)

no_voy_label = ttk.Label(content, text="Bokningar utan resa i Navis", font=("Calibri Light", 11, "bold", "underline"), padding=(0, 15, 0, 0), justify=tk.CENTER)
no_voy_label2 = ttk.Label(content, text="(saknas resa)", font=("Calibri Light", 8), padding=(0, 0, 0, 0), justify=tk.CENTER)
no_voy_label3 = ttk.Label(content, text="Markera de bokningar du vill köra", font=("Calibri Light", 8), padding=(0, 5, 0, 5), justify=tk.CENTER)
no_voy_button = ttk.Button(content, text="Hantera markerade bokningar", width=30, style="Accent.TButton", command=run_no_voy_navis_program)
no_voy_tree = ttk.Treeview(content, columns=("Bokning", "Voyage"), show="headings", height=14)

no_terminal_label = ttk.Label(content, text="Bokningar utan terminal", font=("Calibri Light", 11, "bold", "underline"), padding=(0, 15, 0, 0), justify=tk.CENTER)
no_terminal_label2 = ttk.Label(content, text="(kan kopieras)", font=("Calibri Light", 8), padding=(0, 0, 0, 5), justify=tk.CENTER)
no_terminal_tree = ttk.Treeview(content, columns=("Bokning"), show="headings", height=3)


""" Pack the widgets. """

# Frame first
content.pack(side=tk.TOP)

# Then event log
event_label.pack(side=tk.TOP)
event_button.pack(side=tk.TOP)
event_text.pack(side=tk.TOP)

# Then no voyage tree
no_voy_label.pack(side=tk.TOP)
no_voy_label2.pack(side=tk.TOP)
no_voy_label3.pack(side=tk.TOP)
no_voy_button.pack(side=tk.TOP)
no_voy_tree.pack(side=tk.TOP)

# Lastly no terminal tree
no_terminal_label.pack(side=tk.TOP)
no_terminal_label2.pack(side=tk.TOP)
no_terminal_tree.pack(side=tk.TOP)


""" Adjust column widths and headings. """

no_voy_tree.column("Bokning", width=96, anchor=tk.W)
no_voy_tree.heading("Bokning", text="Bokning")
no_voy_tree.column("Voyage", width=96, anchor=tk.W)
no_voy_tree.heading("Voyage", text="Navis-resa")

no_terminal_tree.column("Bokning", width=115, anchor=tk.W)
no_terminal_tree.heading("Bokning", text="Bokning")


""" Functions below. """

def get_values_from_no_navis_bookings(treeview):
    selected_items = no_voy_tree.selection()
    return ', '.join([str(treeview.item(i)['values'][0]) for i in selected_items])

def copy_treeview(treeview):
    selected_items = treeview.selection()
    window.clipboard_clear()

    window.clipboard_append('\n'.join([str(treeview.item(i)['values'][0]) for i in selected_items]))


# Function to redirect print statements to a Text widget
def redirect_print(text_widget):
    def write_to_text(*args, **kwargs):
        end = kwargs.get('end', 'end-1c')
        text_widget.configure(state='normal')
        text_widget.insert(end, ' '.join(map(str, args)) + '\n')
        text_widget.configure(state='disabled')
        text_widget.see(tk.END)  # Scroll to the end of the text widget

    # Replace the standard print function
    builtins.print = write_to_text


def check_if_ready(thread):
    if thread.is_alive():
        window.after(MS_DELAY, check_if_ready, thread)
    else:
        messagebox.showinfo("Klar", "Klar")
        event_button.config(state=tk.NORMAL)
        no_voy_button.config(state=tk.NORMAL)
        

def delete_text():
    event_text.configure(state='normal')
    event_text.delete("1.0", tk.END)


# Redirect print statements to the Text widget
redirect_print(event_text)

conn = db.create_connection("egl_booking_handler\sqlite\sqlite_egl.db")
bookings_not_in_navis = db.get_bookings_where_values_not_in_db(conn, navis=True)
terminal_not_in_bookings = db.get_bookings_where_values_not_in_db(conn, terminal=True)

no_terminal_tree.bind("<Control-c>", lambda x: copy_treeview(no_terminal_tree))
no_voy_tree.bind("<Control-c>", lambda x: copy_treeview(no_voy_tree))

for booking in bookings_not_in_navis:
    no_voy_tree.insert("", tk.END, values=booking)

for booking in terminal_not_in_bookings:
    no_terminal_tree.insert("", tk.END, values=booking)

#print(f"There are {count_evergreen_bookings()} e-mail(s) in Evergreen's inbox.")
print(f"There are X e-mail(s) in Evergreen's inbox.")

window.mainloop()