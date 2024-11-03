from tkinter import *
from datetime import date
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from tkinter.ttk import Combobox
import sqlite3
import re
from datetime import datetime
import psycopg2

background = "#06283D"
framebg = "#EDEDED"
framefg = "#06283D"
background2 = "#FFFFFF"

db_config = {
    'database': 'registro estudantes',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': '5432'
}

def connect_db():
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS students
                      (id SERIAL PRIMARY KEY,
                       registration_no TEXT,
                       name TEXT,
                       birthdate TEXT,
                       cpf TEXT,
                       class TEXT,
                       father_name TEXT,
                       mother_name TEXT,
                       photo_path TEXT)''')
    conn.commit()
    cursor.close()
    conn.close()


def save_to_db():
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute('''INSERT INTO students 
                          (registration_no, name, birthdate, cpf, class, father_name, mother_name, photo_path) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
                       (Registration.get(), Name.get(), Nasc.get(), Cpf.get(), Turma.get(), F_Name.get(), M_Name.get(), filename))
        conn.commit()
        messagebox.showinfo("Salvo", "Dados salvos com sucesso!")

    except psycopg2.IntegrityError:
        conn.rollback()
        messagebox.showerror("Erro", "Registro já existe!")

    cursor.close()
    conn.close()


def search_student():
    search_term = Search.get()
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE registration_no = %s OR name = %s", (search_term, search_term))
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    results_window = Toplevel(root)
    results_window.title("Resultados da Pesquisa")
    results_window.geometry("600x400")
    results_window.config(bg=background)

    if results:
        for student in results:
            student_frame = Frame(results_window, bg=framebg)
            student_frame.pack(pady=5, fill=X)

            Label(student_frame, text=f"Registro Nº: {student[1]}, Nome: {student[2]}", bg=framebg, fg=framefg).pack(
                side=LEFT)

            select_button = Button(student_frame, text="Selecionar", bg="blue", fg="white",
                                   command=lambda s=student: (preencher_dados(s), results_window.destroy()))
            select_button.pack(side=RIGHT)

            delete_button = Button(student_frame, text="Excluir", bg="red",
                                   command=lambda reg_no=student[1]: delete_student(reg_no))
            delete_button.pack(side=RIGHT)
    else:
        Label(results_window, text="Nenhum aluno encontrado", bg=framebg, fg=framefg).pack(pady=2)


def preencher_dados(student):
    default_img = PhotoImage(file="./assets/user.png")

    Registration.set(student[1])
    Name.set(student[2])
    Nasc.set(student[3])
    Cpf.set(student[4])
    Turma.set(student[5])
    F_Name.set(student[6])
    M_Name.set(student[7])

    if student[8]:
        img = Image.open(student[8])
        resized_image = img.resize((256, 256))
        photo2 = ImageTk.PhotoImage(resized_image)
        lbl.config(image=photo2)
        lbl.image = photo2
    else:
        lbl.config(image=default_img)


def delete_student(reg_no):
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE registration_no = %s", (reg_no,))
    conn.commit()
    cursor.close()
    conn.close()
    messagebox.showinfo("Sucesso", "Aluno excluído com sucesso!")


def Exit():
    root.destroy()


def showimage():
    global filename
    global img
    filename = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select image file", filetypes=(
    ("JPG File", ".jpg"), ("PNG File", ".png"), ("All Files", "*.txt")))
    img = Image.open(filename)
    resized_image = img.resize((256, 256))
    photo2 = ImageTk.PhotoImage(resized_image)
    lbl.config(image=photo2)
    lbl.image = photo2


def Clear():
    Name.set('')
    Nasc.set('')
    Cpf.set('')
    F_Name.set('')
    M_Name.set('')
    Turma.set("Selecione a turma")
    botaosalvar.config(state='normal')
    img1 = PhotoImage(file="./assets/user.png")
    lbl.config(image=img1)
    lbl.image = img1
    img = ""

def update_student():
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        if 'filename' not in globals() or not filename:
            cursor.execute("SELECT photo_path FROM students WHERE registration_no = %s", (Registration.get(),))
            current_photo_path = cursor.fetchone()[0]
        else:
            current_photo_path = filename

        cursor.execute('''UPDATE students SET 
                          name = %s, birthdate = %s, cpf = %s, class = %s, 
                          father_name = %s, mother_name = %s, photo_path = %s 
                          WHERE registration_no = %s''',
                       (Name.get(), Nasc.get(), Cpf.get(), Turma.get(), F_Name.get(), M_Name.get(), current_photo_path, Registration.get()))

        conn.commit()
        messagebox.showinfo("Atualizado", "Dados do aluno atualizados com sucesso!")

    except Exception as e:
        conn.rollback()
        messagebox.showerror("Erro", f"Não foi possível atualizar os dados: {e}")

    finally:
        cursor.close()
        conn.close()


def Save():
    if Name.get() == "" or Cpf.get() == "" or Turma.get() == "Selecione a turma" or Nasc.get() == "" or M_Name.get() == "":
        messagebox.showerror("Tente novamente", "Algum campo está em branco!")
    else:
        save_to_db()
        Clear()

def formatar_cpf(event=None):
    cpf = Cpf.get()
    cpf = re.sub(r'\D', '', cpf)
    cpf_formatado = re.sub(r"(\d{3})(\d{3})(\d{3})(\d{2})", r"\1.\2.\3-\4", cpf[:11])
    Cpf.set(cpf_formatado)

def formatar_nascimento(event=None):
    nasc = Nasc.get()
    nasc = re.sub(r'\D', '', nasc)
    nasc_formatado = re.sub(r"(\d{2})(\d{2})(\d{4})", r"\1/\2/\3", nasc[:8])
    Nasc.set(nasc_formatado)


root = Tk()
root.title("Cadastro de Alunos")
root.geometry("1250x600")
root.config(bg="#06283D")

# Configurar as colunas e linhas para responsividade
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=30)
root.rowconfigure(3, weight=300)
root.rowconfigure(4, weight=1000)

Search = StringVar()

cabecalho = Frame(root, bg="#06283D")
cabecalho.grid(row=0, column=0, pady=10, padx=10, sticky="nswe")
titulo_cabecalho = Label(cabecalho, text="CADASTRO DE ALUNO", width=40, height=2, fg="black", font="arial 20")
titulo_cabecalho.grid(row=0, column=0, sticky="nswe")

cabecalho.columnconfigure(0, weight=1)

obj0 = Frame(root, bg="#06283D")
obj0.grid(row=1, column=0, pady=5, padx=5, sticky="we")

obj0.columnconfigure(0, weight=1)
obj0.columnconfigure(1, weight=1)

search_frame = Frame(obj0, bg="#06283D")
search_frame.grid(row=0, column=1, pady=5, padx=5, sticky="e")

search_frame.columnconfigure(0, weight=1)
search_frame.columnconfigure(1, weight=0)

Entry(search_frame, textvariable=Search, bd=2, font="arial 20").grid(row=0, column=0, padx=5, sticky="e")
Srch = Button(search_frame, text="Pesquisar", bg="#68ddfa", font="arial 13 bold", command=search_student)
Srch.grid(row=0, column=1, padx=10, sticky="e")

obj0_0 = Frame(obj0, bg="#06283D")
obj0_0.grid(row=0, column=0, pady=10, padx=10, sticky="w")

obj0_0.columnconfigure(0, weight=0)
obj0_0.columnconfigure(1, weight=2)
obj0_0.columnconfigure(2, weight=0)
obj0_0.columnconfigure(3, weight=2)


text_registro = Label(obj0_0, text="Registro Nº:", font="arial 13", fg="#EDEDED", bg="#06283D")
text_registro.grid(row=0, column=0, pady=(5), padx=(50,0), sticky="w")
text_data = Label(obj0_0, text="Data:", font="arial 13", fg="#EDEDED", bg="#06283D")
text_data.grid(row=0, column=2, pady=5, padx=(10,0), sticky="w")


Registration = StringVar()
Date = StringVar()

reg_entry = Entry(obj0_0, textvariable=Registration, width=15, font="arial 10")
reg_entry.grid(row=0, column=1, padx=5, sticky="w")

today = date.today()
d1 = today.strftime("%d/%m/%Y")
date_entry = Entry(obj0_0, textvariable=Date, width=15, font="arial 10")
date_entry.grid(row=0, column=3, pady=5, sticky="w")
Date.set(d1)

obj = LabelFrame(root, text="Detalhes do Aluno", font=20, bd=2, width=1000, bg=framebg, fg=framefg, height=250,
                 relief=GROOVE)
obj.grid(row=3, column=0, pady=10, padx=50, sticky="wnes")

obj.columnconfigure(0, weight=0)
obj.columnconfigure(1, weight=1)
obj.columnconfigure(2, weight=1)
obj.columnconfigure(3, weight=0)


text_nome = Label(obj, text="Nome:", font="arial 13", bg=framebg, fg=framefg)
text_nome.grid(row=0, column=0, pady=10, padx=10, sticky="wn")
text_data2 = Label(obj, text="Data de Nascimento:", font="arial 13", bg=framebg, fg=framefg)
text_data2.grid(row=1, column=0, pady=10, padx=10, sticky="wn")
text_cpf = Label(obj, text="CPF:", font="arial 13", bg=framebg, fg=framefg)
text_cpf.grid(row=2, column=0, pady=10, padx=10, sticky="wn")
text_turma = Label(obj, text="Turma:", font="arial 13", bg=framebg, fg=framefg)
text_turma.grid(row=3, column=0, pady=10, padx=10, sticky="wn")

Name = StringVar()
name_entry = Entry(obj, textvariable=Name, width=50, font="arial 10")
name_entry.grid(row=0, column=1, pady=10, padx=10, sticky="wn")

Nasc = StringVar()
nasc_entry = Entry(obj, textvariable=Nasc, width=50, font="arial 10")
nasc_entry.grid(row=1, column=1, pady=10, padx=10, sticky="wn")
nasc_entry.bind("<KeyRelease>", formatar_nascimento)

nasc_info = Label(obj, text="Apenas Números", font="arial 10", bg=framebg, fg="gray")
nasc_info.grid(row=1, column=1, sticky="w", padx=10)

Cpf = StringVar()
cpf_entry = Entry(obj, textvariable=Cpf, width=50, font="arial 10")
cpf_entry.grid(row=2, column=1, pady=10, padx=10, sticky="wn")
cpf_entry.bind("<KeyRelease>", formatar_cpf)

cpf_info = Label(obj, text="Apenas Números", font="arial 10", bg=framebg, fg="gray")
cpf_info.grid(row=2, column=1, sticky="w", padx=10)

Turma = Combobox(obj, values=["Selecione a turma", "1A", "1B", "2A", "2B"], font="Roboto 10", width=17, state="r")
Turma.grid(row=3, column=1, pady=10, padx=10, sticky="wn")
Turma.set("Selecione a turma")


obj2 = LabelFrame(root, text="Detalhes do Responsável", font=20, bd=2, width=900, bg=framebg, fg=framefg, height=220,
                  relief=GROOVE)
obj2.grid(row=4, column=0, pady=10, padx=50, sticky="wnes")

obj2.columnconfigure(0, weight=0)
obj2.columnconfigure(1, weight=1)
obj2.columnconfigure(2, weight=0)
obj2.columnconfigure(3, weight=1)

Label(obj2, text="Nome do pai:", font="arial 13", bg=framebg, fg=framefg).grid(row=0, column=0, pady=10, padx=10, sticky="wn")
F_Name = StringVar()
f_entry = Entry(obj2, textvariable=F_Name, width=50, font="arial 10")
f_entry.grid(row=0, column=1, pady=10, padx=10, sticky="wn")

Label(obj2, text="Nome da mãe:", font="arial 13", bg=framebg, fg=framefg).grid(row=0, column=2, pady=10, padx=10, sticky="wn")
M_Name = StringVar()
M_entry = Entry(obj2, textvariable=M_Name, width=50, font="arial 10")
M_entry.grid(row=0, column=3, pady=10, padx=10, sticky="wn")

img = PhotoImage(file="./assets/user.png")
lbl = Label(obj, image=img, bg="white", width=256, height=256, relief=GROOVE)
lbl.grid(row=0, column=2, rowspan= 4, pady=10, padx=50, sticky="wn")

obj3 = Frame(obj, bd=2, bg=framebg)
obj3.grid(row=0, column=3, rowspan=4, pady=1, padx=1, sticky="wn")

botaoupload = Button(obj3, text="Upload", width=19, height=2, font="arial 12 bold", bg="lightblue", command=showimage)
botaoupload.grid(row=0, column=0, pady=5, padx= 1, sticky="wn")
botaosalvar = Button(obj3, text="Salvar", width=19, height=2, font="arial 12 bold", bg="lightgreen", command=Save)
botaosalvar.grid(row=1, column=0, pady=5, padx=1, sticky="wn")
botaoreset = Button(obj3, text="Reset", width=19, height=2, font="arial 12 bold", bg="lightpink", command=Clear)
botaoreset.grid(row=2, column=0, pady=5, padx= 1, sticky="wn")
botaoupdate = Button(obj3, text="Atualizar", width=19, height=2, font="arial 12 bold", bg="yellow", command=update_student)
botaoupdate.grid(row=3, column=0, pady=5, padx=1, sticky="wn")
botaosair = Button(obj3, text="Sair", width=19, height=2, font="arial 12 bold", bg="grey", command=Exit)
botaosair.grid(row=4, column=0, pady=5, padx= 1, sticky="wn")

connect_db()

root.mainloop()