import contextlib
import os
import shelve
import tkinter as tk
from tkinter import BOTTOM, END, LEFT, TOP, Frame, Label, Message, Text, messagebox
from tkinter.ttk import Button

import requests
import ttkbootstrap as ttk
from ttkbootstrap.constants import DANGER, INFO, OUTLINE, PRIMARY, SUCCESS

with contextlib.suppress(ImportError):
    from ctypes import windll  # Only exists on Windows.

    MY_APP_ID = "christianhofmann.quoter.gui.0.0.1"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(MY_APP_ID)


class APIFunctions:
    @staticmethod
    def get_response(url: str, proxy: str) -> requests.Response | None:
        proxy_dict = {"http": proxy, "https": proxy}
        try:
            response = requests.get(url, proxies=proxy_dict, timeout=5)
            return None if response.status_code != 200 else response
        except requests.exceptions.InvalidURL:
            return None
        except requests.exceptions.ConnectionError:
            return None


class MainWindow(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        self.__create_widgets()

    def __create_widgets(self) -> None:

        self.top_frame = Frame(self)
        self.middle_frame = Frame(self)
        self.bottom_frame = Frame(self)

        self.quote_msg = Message(
            self.top_frame,
            font=("Helvetica 12 italic"),
            justify="center",
            bg="#2b3e50",
            fg="#ffffff",
            aspect="500",
            width=300,
        )
        self.author_lbl = Label(self.top_frame, font=("Helvetica 10"))
        self.get_button = Button(
            self.bottom_frame,
            text="Get random Quote",
            bootstyle=SUCCESS,
            command=self.new_quote,
        )
        self.get_today_button = Button(
            self.bottom_frame,
            text="Get Quote of the day",
            bootstyle=(INFO, OUTLINE),
            command=self.today_quote,
        )

        self.settings_button = Button(
            self.bottom_frame, text="⚙️", bootstyle=PRIMARY, command=self.open_settings
        )

        self.top_frame.pack(
            side=TOP,
            fill="both",
            expand=True,
            ipadx=10,
            ipady=10,
        )
        self.middle_frame.pack(side=TOP, fill="both", expand=True, ipadx=10, ipady=10)
        self.bottom_frame.pack(side=BOTTOM, fill="both", expand=True, ipady=10)

        self.quote_msg.pack(side=TOP, pady=20)
        self.author_lbl.pack(side=TOP)

        self.get_button.pack(side=LEFT, padx=5, pady=10)
        self.get_today_button.pack(side=LEFT, padx=5, pady=10)
        self.settings_button.pack(side=LEFT, padx=5, pady=10)

        self.pack()

    def open_settings(self) -> None:
        window = SettingsWindow(self)
        window.grab_set()

    def get_quote(self, quote: list) -> str:
        return quote[0]["q"]

    def get_author(self, quote: list) -> str:
        return quote[0]["a"]

    def delete_text(self) -> None:
        self.quote_msg.config(text="")
        self.author_lbl.config(text="")

    def set_text(self, quote, author) -> None:
        self.quote_msg.config(text=f"'{quote}'")
        self.author_lbl.config(text=author)

    def new_quote(self) -> None:
        response = APIFunctions.get_response(
            "https://zenquotes.io/api/random", SettingsWindow.get_settings(self)
        )
        self.display_content(response, "normal")

    def today_quote(self) -> None:
        response = APIFunctions.get_response(
            "https://zenquotes.io/api/today", SettingsWindow.get_settings(self)
        )
        self.display_content(response, "disabled")

    def display_content(
        self, response: requests.Response, today_btn_state: str
    ) -> None:
        if response is not None:
            self.get_today_button.config(state=today_btn_state)
            quote = self.get_quote(response.json())
            author = self.get_author(response.json())
            self.delete_text()
            self.set_text(quote, author)
        else:
            messagebox.showerror(title="Error!", message="Invalid proxy settings!")


class SettingsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Quoter - Settings")
        self.iconbitmap(bitmap=ICON_PATH, default=ICON_PATH)
        self.geometry("520x90")
        self.resizable(False, False)

        self.__create_widgets()

    def __create_widgets(self) -> None:

        self.proxy_lbl = Label(self, text="Proxy:")
        self.settings_txt = Text(self, height=1, width=50, wrap="none")
        self.settings_txt.insert(END, self.get_settings())

        self.cancel_button = Button(
            self,
            text="Cancel",
            bootstyle=(DANGER, OUTLINE),
            command=self.close_settings,
        )
        self.save_button = Button(
            self,
            text="Save",
            bootstyle=SUCCESS,
            command=self.save_settings,
        )
        self.proxy_lbl.pack(side=LEFT, padx=5, pady=10)
        self.settings_txt.pack(side=LEFT, padx=5, pady=10)
        self.cancel_button.pack(side=LEFT, padx=5, pady=10)
        self.save_button.pack(side=LEFT, padx=5, pady=10)

    def get_settings(self) -> str:
        try:
            return SETTINGS["proxy"]
        except KeyError:
            return ""

    def save_settings(self) -> None:
        SETTINGS["proxy"] = self.settings_txt.get(1.0, "end-1c")
        self.destroy()

    def close_settings(self) -> None:
        self.destroy()


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        ttk.Style("superhero")
        self.title("Quoter")
        self.iconbitmap(
            bitmap=ICON_PATH,
            default=ICON_PATH,
        )
        self.geometry("500x300")
        self.resizable(False, False)


if __name__ == "__main__":
    SETTINGS = shelve.open("mySettings")
    BASE_DIR = os.path.dirname(__file__)
    OLDER_ICON_PATH = r"icon/quoter.ico"
    OLD_ICON_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/quoter.ico"
    ICON_PATH = os.path.join(BASE_DIR, "icon", "quoter.ico")
    app = App()
    frame = MainWindow(app)
    app.mainloop()
