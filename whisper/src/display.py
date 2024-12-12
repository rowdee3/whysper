import customtkinter

class splashscreen(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("800x400")
        self.title("whisper v0.0.3")

        self.button = customtkinter.CTkButton(self, text="My button", command=self.button_callback)
        self.button.pack(pady=20, padx=20)

    def button_callback(self):
        print("Hello, World!")

app = splashscreen()
app.mainloop()