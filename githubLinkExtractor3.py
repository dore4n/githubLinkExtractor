import os
import threading
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from tkinter import Tk, Label, Button, Entry, filedialog, Toplevel, Text, Scrollbar, Frame, IntVar, messagebox
from tkinter.ttk import Progressbar, Checkbutton

class GithubRepoLinkExtractor:
    def __init__(self, master):
        self.master = master
        master.title("Github Repo Link Extractor")
        
        frame1 = Frame(master)
        frame1.pack()

        self.label = Label(frame1, text="Diretório para salvar os links:")
        self.label.grid(row=0, column=0)

        self.entry = Entry(frame1)
        self.entry.grid(row=0, column=1)

        self.browse_button = Button(frame1, text="Navegar", command=self.browse)
        self.browse_button.grid(row=0, column=2)
        
        self.label_filename = Label(master, text="Nome do arquivo:")
        self.label_filename.pack()

        self.entry_filename = Entry(master)
        self.entry_filename.pack()

        self.label_count = Label(master, text="Número de links para extrair:")
        self.label_count.pack()

        self.entry_count = Entry(master)
        self.entry_count.pack()

        self.extract_all_var = IntVar()
        self.extract_all_checkbox = Checkbutton(master, text="Extrair de todos os repositórios", variable=self.extract_all_var)
        self.extract_all_checkbox.pack()

        self.extract_button = Button(master, text="Iniciar Extração", command=self.extract_links)
        self.extract_button.pack()

        self.status_label = Label(master, text="")
        self.status_label.pack()

        self.progress = Progressbar(master, orient="horizontal", length=200, mode="determinate")
        self.progress.pack()

        self.cancel_button = Button(master, text="Cancelar", command=self.cancel_extraction)
        self.cancel_button.pack()

        self.cancelled = False
        self.driver = None

    def browse(self):
        folder_selected = filedialog.askdirectory()
        self.entry.delete(0, "end")
        self.entry.insert(0, folder_selected)

    def save_links_to_file(self, links, directory, filename):
        file_path = os.path.join(directory, filename + ".txt")
        with open(file_path, "w") as file:
            for link in links:
                file.write(link + "\n")

    def show_error(self, error_message):
        top = Toplevel()
        top.title("Erro")
        
        text = Text(top, height=10, width=50, wrap="word")
        text.insert("end", error_message)
        text.pack()

    def cancel_extraction(self):
        self.cancelled = True
        if self.driver:
            self.driver.quit()
        self.status_label.config(text="Extração cancelada.")
        self.extract_button.config(text="Iniciar Extração", command=self.extract_links)

    def extract_links(self):
        self.cancelled = False
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("executable_path=C:\temp\chromedriver.exe")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.get('Insira aqui o link do repositório')

            # Aguardar até que o usuário faça login manualmente
            messagebox.showinfo("Aviso", "Por favor, faça login manualmente na sua conta do GitHub e pressione OK quando estiver pronto para continuar.")
            
            repo_links = []

            if self.extract_all_var.get() == 1:
                max_links = float('inf')
            else:
                max_links = int(self.entry_count.get())

            while len(repo_links) < max_links and not self.cancelled:
                try:
                    repo_elements = self.driver.find_elements(By.CSS_SELECTOR, 'h3 a')
                    for el in repo_elements:
                        link = el.get_attribute('href')
                        if link not in repo_links:
                            repo_links.append(link)

                    next_page_button = self.driver.find_element(By.CSS_SELECTOR, '.pagination .next_page')
                    if next_page_button.get_attribute('class') == 'next_page':
                        next_page_button.click()
                        wait = WebDriverWait(self.driver, 10)
                        wait.until(lambda browser: browser.find_element(By.CSS_SELECTOR, 'h3 a'))
                    else:
                        break

                    self.status_label.config(text=f"Coletados {len(repo_links)} links")
                except Exception as e:
                    self.show_error(str(e))

                time.sleep(2)

            if not self.cancelled:
                self.driver.quit()
                filename = self.entry_filename.get()
                self.save_links_to_file(repo_links, self.entry.get(), filename)
                self.status_label.config(text=f"Extração concluída. Coletados {len(repo_links)} links e salvos em '{filename}.txt'")
            
        except Exception as e:
            self.show_error(str(e))
            self.driver.quit()
        finally:
            if self.cancelled:
                self.status_label.config(text="Extração cancelada.")
            self.extract_button.config(text="Iniciar Extração", command=self.extract_links)

if __name__ == "__main__":
    root = Tk()
    extractor = GithubRepoLinkExtractor(root)
    root.mainloop()
