import builtins
import concurrent.futures
import tkinter as tk
from tkinter import ttk, messagebox

from eglhandler.src import main
from eglhandler.src.sqlite.sqlite_db import SqliteDB


class EGLApp:
    """
    """
    VERSION = "0.1.0"

    database: str
    forest_theme: str
    ms_delay: int
    style: ttk.Style
    content: ttk.Frame
    window: tk.Tk
    bookings: dict

    config = dict
    forest_theme: str
    email_count: int

    def __init__(self, config: dict, database: str) -> None:
        self.database = database
        self.forest_theme = config['widget'].get('forest_theme')
        self.ms_delay = config['widget'].get('ms_delay')
        self.config = config
        self.style = None
        self.content = None

        # Run functions to create the widgets.
        self.window = self.window()
        self.bookings = self._bookings_widget()
        self.no_voy = self._no_voy_widget()
        self.no_terminal = self._no_terminal_treeview()
        self._packing_widgets()
        self._redirect_print()
        self._write_out_missing_bookings()

        self.email_count = None
    
      
    def window(self) -> tk.Tk:
        """Create the main window. """

        self.window = tk.Tk()
        self.window.option_add("*tearOff", False)

        self.window.tk.call('source', self.forest_theme)

        self.style = ttk.Style(self.window)
        self.style.theme_use('forest-light')

        self.window.title("EVERGREEN")

        self.content = ttk.Frame(self.window)

        """ Set the window position. """

        # Geometry: width x height + x_offset + y_offset
        self.window.geometry("504x1009+-7+0")
        self.window.resizable(False, False)

        return self.window
    

    def _bookings_widget(self) -> dict:
        
        lbl = ttk.Label(
            self.content,
            text="Evergreen-bokningar",
            font=("Calibri Light", 20, "bold", "underline"),
            padding=(0, 5, 0, 5)
        )
        btn = ttk.Button(
            self.content,
            text="Hantera bokningar",
            width=30,
            style="Accent.TButton",
            command=self.run_main_program_with_threading
        )
        txt = tk.Text(
            self.content,
            width=60,
            height=22,
            font=("Calibri Light", 11),
            border=3
        )
        
        return {'label': lbl, 'button': btn, 'text': txt}
    

    def _no_voy_widget(self) -> dict:
        
        lbl_1 = ttk.Label(
            self.content,
            text="Bokningar utan resa i Navis",
            font=("Calibri Light", 14, "bold", "underline"),
            padding=(0, 7, 0, 0),
            justify=tk.CENTER
        )
        lbl_2 = ttk.Label(
            self.content,
            text="(kan kopieras)",
            font=("Calibri Light", 10),
            padding=(0, 0, 0, 0),
            justify=tk.CENTER
        )
        lbl_3 = ttk.Label(
            self.content,
            text="Markera de bokningar du vill köra",
            font=("Calibri Light", 10),
            padding=(0, 0, 0, 5),
            justify=tk.CENTER
        )
        btn = ttk.Button(
            self.content,
            text="Hantera markerade bokningar",
            width=30, style="Accent.TButton",
            command=self.run_no_voy_with_threading
        )
        tree = ttk.Treeview(
            self.content,
            columns=("Bokning", "Voyage"),
            show="headings",
            height=9
        )

        return {
            'label1': lbl_1,
            'label2': lbl_2,
            'label3': lbl_3,
            'button': btn,
            'tree': tree}
    

    def _no_terminal_treeview(self) -> dict:

        lbl_1 = ttk.Label(
            self.content,
            text="Bokningar utan terminal",
            font=("Calibri Light", 14, "bold", "underline"),
            padding=(0, 7, 0, 0),
            justify=tk.CENTER
        )
        
        lbl_2 = ttk.Label(
            self.content,
            text="(kan kopieras)",
            font=("Calibri Light", 10),
            padding=(0, 0, 0, 5),
            justify=tk.CENTER
        )
        
        tree = ttk.Treeview(
            self.content,
            columns=("Bokning"),
            show="headings",
            height=2
        )

        return {'label1': lbl_1, 'label2': lbl_2, 'tree': tree}
    
    def run_main_program_with_threading(self) -> None:
        executor = concurrent.futures.ThreadPoolExecutor()
        executor.submit(self._run_main_program)
        executor.shutdown(wait=False)

        
    def _run_main_program(self) -> None:
        """Run the main program that handles the bookings.

        It will:
            - Download PDFs from e-mails through Microsoft Graph API.
            - Extract the data from the PDFs and insert to Sqlite Database.
            - Based on the data create/update/delete bookings in Navis.
        """

        self.bookings.get('button').config(state=tk.DISABLED)
        self._delete_text()
        main.run_main_program()

        self.bookings.get('button').config(state=tk.NORMAL)
        print("Done!")


    def run_no_voy_with_threading(self) -> None:
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        executor.submit(self._run_no_voy_navis_program)
        executor.shutdown(wait=False)


    def _run_no_voy_navis_program(self) -> tuple:
        """Run the program that handles the bookings without voyages in Navis. """
        
        if self._get_values_from_no_navis_bookings() == '':
            messagebox.showinfo(
                "Ingen bokning vald",
                "Markera en eller flera bokningar i listan."
                )
            return

        self.no_voy.get('button').configure(state=tk.DISABLED)
        self._delete_text()

        bookings = self._get_values_from_no_navis_bookings()
        bookings_list = bookings.split(', ')
        main.run_missing_bookings_in_navis(bookings_list)
        self._write_out_missing_bookings()
        self.no_voy.get('button').config(state=tk.NORMAL)
        print("Done")


    def _get_values_from_no_navis_bookings(self) -> tuple:
        no_voy_tree = self.no_voy.get('tree')
        selected_items = no_voy_tree.selection()
        return ', '.join(
            [str(no_voy_tree.item(i)['values'][0]) for i in selected_items]
            )


    def _copy_treeview(self, treeview: ttk.Treeview) -> None:
        selected_items = treeview.selection()
        self.window.clipboard_clear()

        self.window.clipboard_append(
            '\n'.join([str(treeview.item(i)['values'][0]) for i in selected_items])
        )


    def _redirect_print(self) -> None:
        """ Redirects the print function to the text widget."""

        text = self.bookings.get('text')
        def write_to_text(*args, **kwargs):
            end = kwargs.get('end', 'end-1c')
            text.configure(state='normal')
            text.insert(end, ' '.join(map(str, args)) + '\n')
            text.configure(state='disabled')
            text.see(tk.END)  # Scroll to the end of the text

        # Replace the built-in print function with our custom function
        builtins.print = write_to_text


    def _check_if_ready(self) -> None:
        if self.executor.is_alive():
            print('Waiting for thread to finish...')
            #return
        else:
            self._write_out_missing_bookings()
            print('Done!')

            self.bookings.get('button').configure(state=tk.NORMAL)
            self.no_voy.get('button').configure(state=tk.NORMAL)


    def _delete_text(self) -> None:
        text = self.bookings.get('text')
        text.configure(state='normal')
        text.delete("1.0", tk.END)


    def _packing_widgets(self) -> None:
        loop_through = (
            self.content,
            list(self.bookings.values()),
            list(self.no_voy.values()),
            list(self.no_terminal.values())
        )
        for widget in loop_through:
            if isinstance(widget, list):
                for w in widget:
                    w.pack()
            else:
                widget.pack()
        
        self._adjust_columns_widths()


    def _adjust_columns_widths(self) -> None:
        voy_tree = self.no_voy.get('tree')
        voy_tree.column("Bokning", width=96, anchor=tk.W)
        voy_tree.heading("Bokning", text="Bokning")
        voy_tree.column("Voyage", width=96, anchor=tk.W)
        voy_tree.heading("Voyage", text="Navis-resa")

        terminal_tree = self.no_terminal.get('tree')
        terminal_tree.column("Bokning", width=115, anchor=tk.W)
        terminal_tree.heading("Bokning", text="Bokning")


    def _write_out_missing_bookings(self) -> None:
        sql = SqliteDB(self.database)
        bookings_not_in_navis = sql.get_bookings_where_navis_voy_not_in_database()
        bookings_with_no_terminal = sql.get_bookings_where_terminal_not_in_database()

        no_voy_tree: ttk.Treeview = self.no_voy.get('tree')
        no_terminal_tree: ttk.Treeview = self.no_terminal.get('tree')

        no_voy_tree.bind(
            "<Control-c>",
            lambda x: self._copy_treeview(no_voy_tree)
            )
            
        no_terminal_tree.bind(
            "<Control-c>",
            lambda x: self._copy_treeview(no_terminal_tree)
            )
        
        no_voy_tree.delete(*no_voy_tree.get_children())
        no_terminal_tree.delete(*no_terminal_tree.get_children())

        if bookings_not_in_navis:
            for booking in bookings_not_in_navis:
                no_voy_tree.insert("", tk.END, values=booking)
        
        if bookings_with_no_terminal:
            for booking in bookings_with_no_terminal:
                no_terminal_tree.insert("", tk.END, values=booking)


    def menu_bar(self) -> None:
        menu_bar = tk.Menu(self.window)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Refresh", command=self.refresh_window, accelerator="Ctrl+Q")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.window.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="Settings", command=self.settings)
        settings_menu.add_command(label="About...", command=self.about)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)

        self.window.bind_all("<Control-Q>", self.refresh_window)
        self.window.bind_all("<Control-q>", self.refresh_window)

        return menu_bar

    def write_out_booking_count(self, booking_count: int) -> None:
        print(f"{booking_count} e-mail(s) found in folder Evergreen.")
        self.email_count = booking_count
         

    def refresh_window(self, event=None) -> None:
        self.window.destroy()
        from eglhandler.src import main_app
        main_app.run_application()
    

    def about(self) -> None:
        """About the program."""

        about_window = tk.Toplevel(self.window)
        about_window.title("About")

        content = ttk.Frame(about_window)

        # Geometry: width x height + x_offset + y_offset
        about_window.geometry("250x66+100+300")
        about_window.resizable(False, False)
        about_window.focus_set()
        about_window.grab_set()
        about_window.transient(self.window)
  

        label_version = ttk.Label(
            content,
            text=f"Version: {self.VERSION}",
            font=("Calibri Light", 12),
            padding=(0, 5, 0, 5),
            justify=tk.CENTER,
        )
        
        label_author = ttk.Label(
            content,
            text="Author: Marcus Berggren (2023)",
            font=("Calibri Light", 12),
            padding=(0, 5, 0, 5),
            justify=tk.CENTER
        )

        content.pack()
        label_version.pack(anchor=tk.W)
        label_author.pack(anchor=tk.W)
        
        
    def settings(self) -> None:
        """TODO: Add settings for the program.
        Should configure config.yaml file."""

        settings_window = tk.Toplevel(self.window)
        settings_window.title("Settings")

        content = ttk.Frame(settings_window)

        # Geometry: width x height + x_offset + y_offset
        settings_window.geometry("1000x500+50+150")
        settings_window.resizable(False, False)
        settings_window.focus_set()
        settings_window.grab_set()
        settings_window.transient(self.window)
    
    def read_from_config_file(self) -> None:

        config = self.config
        login = config['navis']['login']
        user = login['user']
        password = login['password']



    def run_widget(self) -> None:
        self.window.config(menu=self.menu_bar())
        self.window.mainloop()
