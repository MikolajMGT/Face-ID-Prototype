import tkinter as tk
from pathlib import Path

# Colors

DARK = '#404A4F'
LIGHT = '#E0E0E2'
ACCENT = '#454ADE'


class View:

    def __init__(self, manager):
        print('View.init() performed')

        self.manager = manager
        self.app_root = tk.Tk()
        self.app_root.eval('tk::PlaceWindow . center')
        self.app_screen = tk.Frame(self.app_root)
        self.welcome_screen = tk.Frame(self.app_root)
        self.register_screen = tk.Frame(self.app_root)
        self.user_name = tk.StringVar()
        self.register_name = tk.StringVar()
        Path('data/features').mkdir(parents=True, exist_ok=True)

    def display_view(self):
        print('View.init_view() performed')

        self.app_root.title('Amazing Face ID')

        screen_list = [self.app_screen, self.welcome_screen, self.register_screen]

        for screen in screen_list:
            screen.grid(row=0, column=0, sticky='news')
            screen.configure(bg=DARK)

        self.prepare_app_screen()
        self.prepare_welcome_screen()
        self.prepare_register_screen()

        self.open_welcome_screen()
        self.app_root.mainloop()

    # prepare

    def prepare_app_screen(self):
        tk.Label(self.app_screen, text="Hello, ", font=("Helvetica", 50), fg=LIGHT, bg=DARK)\
            .grid(row=1, column=1, pady=(30, 30))
        tk.Label(self.app_screen, textvariable=self.user_name, font=("Helvetica", 50), bg=DARK, fg=ACCENT) \
            .grid(row=1, column=2)
        tk.Button(self.app_screen, text="Log Out", font=("Helvetica", 30), command=self.open_welcome_screen) \
            .grid(row=2, column=1)

    def prepare_welcome_screen(self):
        tk.Label(self.welcome_screen, text="Face ID Prototype", font=("Helvetica", 50), fg=LIGHT, bg=DARK) \
            .grid(row=1, column=1, columnspan=5, pady=(30, 30))

        login_button = tk.Button(self.welcome_screen, text="Sign In", font=("Helvetica", 30),
                                 command=self.__login_user)
        login_button.grid(row=2, column=3, padx=(30, 30), pady=(30, 30))

        register_button = tk.Button(self.welcome_screen, text="Sign Up", command=self.open_register_screen,
                                    font=("Helvetica", 30))
        register_button.grid(row=2, column=1, padx=(30, 30), pady=(30, 30))

        recognition_button = tk.Button(self.welcome_screen, text="Recognition", command=self.__recognition,
                                       font=("Helvetica", 30))
        recognition_button.grid(row=2, column=5, padx=(30, 30), pady=(30, 30))

    def __login_user(self):
        auth_user = self.manager.login()
        if auth_user is not None:
            self.user_name.set(auth_user)
            self.open_app_screen()

    def __recognition(self):
        self.manager.auth.recognition()

    def prepare_register_screen(self):
        tk.Label(self.register_screen, text="Sign Up", font=("Helvetica", 50), fg=LIGHT, bg=DARK) \
            .grid(row=1, column=1, columnspan=5, pady=(30, 30))
        tk.Label(self.register_screen, text="Name: ", font=("Helvetica", 20), fg=LIGHT, bg=DARK) \
            .grid(row=2, column=1)

        tk.Entry(self.register_screen, textvariable=self.register_name, font=("Helvetica", 30)) \
            .grid(row=2, column=2)

        register_confirm_button = tk.Button(self.register_screen, text="Sign Up", command=self.__register,
                                            font=("Helvetica", 30))
        register_confirm_button.grid(row=3, column=2)

    def __register(self):
        self.manager.register(self.register_name.get())
        self.open_welcome_screen()

    # open

    def open_app_screen(self):
        print('View.open_menu() performed')
        self.app_screen.tkraise()

    def open_welcome_screen(self):
        print('View.open_login() performed')
        self.welcome_screen.tkraise()

    def open_register_screen(self):
        print('View.open_register() performed')
        self.register_screen.tkraise()
