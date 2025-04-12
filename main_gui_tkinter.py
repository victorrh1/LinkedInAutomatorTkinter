import customtkinter as ctk
from threading import Thread
import json
import os
from cryptography.fernet import Fernet
import base64
import hashlib
import uuid
from app import iniciar_automacao

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Linked Automator")
        self.geometry("500x600")
        
        self.credentials_file = os.path.join(os.path.expanduser("~"), ".linked_automator_credentials")
        self.key_file = os.path.join(os.path.expanduser("~"), ".linked_automator_key")
        
        self.setup_ui()
        self.center_window()
        self.load_credentials()

    def setup_ui(self):
        self.credentials_frame = ctk.CTkFrame(self)
        self.credentials_frame.pack(pady=10, fill="x", padx=20)
        
        self.login_label = ctk.CTkLabel(self.credentials_frame, text="E-mail LinkedIn:")
        self.login_label.pack(pady=(10, 0), anchor="w")
        
        self.login_entry = ctk.CTkEntry(self.credentials_frame, width=400)
        self.login_entry.pack(pady=5)
        
        self.senha_label = ctk.CTkLabel(self.credentials_frame, text="Senha LinkedIn:")
        self.senha_label.pack(pady=(10, 0), anchor="w")
        
        self.senha_entry = ctk.CTkEntry(self.credentials_frame, width=400, show="•")
        self.senha_entry.pack(pady=5)
        
        self.save_credentials = ctk.CTkCheckBox(self.credentials_frame, text="Salvar credenciais")
        self.save_credentials.pack(pady=10)

        self.label = ctk.CTkLabel(self, text="Qual profissão deseja buscar")
        self.label.pack(pady=(20, 10))
        
        self.palavra_chave = ctk.CTkEntry(self, width=400)
        self.palavra_chave.pack(pady=10)
        
        self.start_button = ctk.CTkButton(self, text="Iniciar Automação", command=self.start_automation)
        self.start_button.pack(pady=10)
        
        self.output_text = ctk.CTkTextbox(self, width=400, height=200)
        self.output_text.pack(pady=10, fill="both", expand=True, padx=20)

    def center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        width = 500
        height = 600
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.geometry(f"{width}x{height}+{x}+{y}")

    def get_device_id(self):
        return str(uuid.getnode())

    def get_encryption_key(self):
        try:
            if os.path.exists(self.key_file):
                with open(self.key_file, 'rb') as f:
                    key = f.read()
                    if not key:
                        raise ValueError("Empty key file")
                    return key
            
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            return key
        except Exception as e:
            self.write_output(f"Erro ao gerar chave de criptografia: {str(e)}\n")
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            return key

    def save_credentials_to_file(self):
        if not self.save_credentials.get():
            return
        
        email = self.login_entry.get()
        password = self.senha_entry.get()

        if not email or not password:
            return
        
        try:
            key = self.get_encryption_key()
            cipher_suite = Fernet(key)

            credentials = {
                'email': cipher_suite.encrypt(email.encode()).decode(),
                'password': cipher_suite.encrypt(password.encode()).decode()
            }

            with open(self.credentials_file, 'w') as f:
                json.dump(credentials, f)
        except Exception as e:
            self.write_output(f"Erro ao salvar credenciais: {str(e)}\n")

    def load_credentials(self):
        if not os.path.exists(self.credentials_file) or not os.path.exists(self.key_file):
            return

        try:
            key = self.get_encryption_key()
            cipher_suite = Fernet(key)
            
            with open(self.credentials_file, 'r') as f:
                credentials = json.load(f)

            email = cipher_suite.decrypt(credentials['email'].encode()).decode()
            password = cipher_suite.decrypt(credentials['password'].encode()).decode()

            self.login_entry.delete(0, 'end')
            self.login_entry.insert(0, email)

            self.senha_entry.delete(0, 'end')
            self.senha_entry.insert(0, password)

            self.save_credentials.select()
        except Exception as e:
            self.write_output(f"Erro ao carregar credenciais salvas: {str(e)}\n")

    def start_automation(self):
        self.start_button.configure(state="disabled")
        self.save_credentials_to_file()

        email = self.login_entry.get()
        senha = self.senha_entry.get()
        palavra_chave = self.palavra_chave.get()

        if not email or not senha:
            self.write_output("Por favor, insira seu e-mail e senha do LinkedIn.\n")
            self.start_button.configure(state="normal")
            return

        if not palavra_chave:
            self.write_output("Por favor, insira uma profissão para buscar.\n")
            self.start_button.configure(state="normal")
            return

        self.write_output(f"Iremos buscar por: {palavra_chave}\n")

        thread = Thread(
            target=iniciar_automacao,
            daemon=True,
            args=(palavra_chave, self, email, senha)
        )
        thread.start()

    def write_output(self, text):
        self.output_text.insert("end", text)
        self.output_text.see("end")

if __name__ == "__main__":
    app = App()
    app.mainloop()
