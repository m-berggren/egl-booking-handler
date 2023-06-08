import tkinter as tk
from tkinter import ttk, messagebox

from eglhandler.src.sqlite.sqlite_db import SqliteDB

class EGLApp:
    """
    """

    window: tk.Tk
    style: ttk.Style
    MS_DELAY: int
    FOREST_THEME: str

    MS_DELAY = 1000  # Milliseconds between updates
    FOREST_THEME = r"app\eglhandler\src\widget\forest-light.tcl"

    def __init__(self) -> None:
    
        self.style = None
        self.content = None
        self.window = self.window()

    def window(self) -> None:
        """Create the main window. """

        self.window = tk.Tk()
        self.window.option_add("*tearOff", False)

        self.window.tk.call('source', self.FOREST_THEME)

        self.style = ttk.Style(self.window)
        self.style.theme_use('forest-light')

        self.window.title("EVERGREEN")

        self.content = ttk.Frame(self.window)

        """ Set the window position. """

        # Geometry: width x height + x_offset + y_offset
        self.window.geometry("244x1009+-7+0")
        self.window.resizable(False, False)
    

    def bookings_widget(self) -> tuple:
        
        lbl = ttk.Label(self.content, text="Evergreen-bokningar", font=("Calibri Light", 16, "bold", "underline"), padding=(0, 5, 0, 5))
        btn = ttk.Button(self.content, text="Hantera bokningar", width=30, style="Accent.TButton", command=self.run_main_program)
        txt = tk.Text(self.content, width=32, height=20, font=("Calibri Light", 10), border=3)
        
        return [lbl, btn, txt]

    def no_voy_widget(self) -> tuple:
        
        lbl_1 = ttk.Label(self.content, text="Bokningar utan resa i Navis", font=("Calibri Light", 11, "bold", "underline"), padding=(0, 15, 0, 0), justify=tk.CENTER)
        lbl_2 = ttk.Label(self.content, text="(saknas resa)", font=("Calibri Light", 8), padding=(0, 0, 0, 0), justify=tk.CENTER)
        lbl_3 = ttk.Label(self.content, text="Markera de bokningar du vill köra", font=("Calibri Light", 8), padding=(0, 5, 0, 5), justify=tk.CENTER)
        btn = ttk.Button(self.content, text="Hantera markerade bokningar", width=30, style="Accent.TButton", command=self.run_no_voy_navis_program)
        tree = ttk.Treeview(self.content, columns=("Bokning", "Voyage"), show="headings", height=14)

        return [lbl_1, lbl_2, lbl_3, btn, tree]

    def no_terminal_treeview(self) -> tuple:
        
        lbl_1 = ttk.Label(self.content, text="Bokningar utan terminal", font=("Calibri Light", 11, "bold", "underline"), padding=(0, 15, 0, 0), justify=tk.CENTER)
        lbl_2 = ttk.Label(self.content, text="(kan kopieras)", font=("Calibri Light", 8), padding=(0, 0, 0, 5), justify=tk.CENTER)
        tree = ttk.Treeview(self.content, columns=("Bokning"), show="headings", height=3)

        return [lbl_1, lbl_2, tree]

    def _run_main_program(self) -> None:
        pass

    
    def _run_no_voy_navis_program(self) -> None:
        pass


    def _get_values_from_no_navis_bookings(self) -> None:
        pass


    def _copy_terminal_treeview(self) -> None:
        pass


    def redirect_print(text_widget: tk.Text) -> None:
        pass


    def check_if_ready(self) -> None:
        pass


    def packing_widgets(self) -> None:

        loop_through = self.content, self.bookings_widget(), self.no_voy_widget(), self.no_terminal_treeview()
        for widget in loop_through:
            if isinstance(widget, list):
                for w in widget:
                    w.pack()
            else:
                widget.pack()
        
        self.adjust_columns_widths()

    def adjust_columns_widths(self) -> None:
        



