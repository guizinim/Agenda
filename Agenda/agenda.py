import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, colorchooser
from datetime import datetime, timedelta

class StyledAddTaskDialog(simpledialog.Dialog):
    def __init__(self, parent, title):
        self.task_name = ""
        self.deadline_str = ""
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text="Nome da Tarefa:").grid(row=0, column=0, sticky="w", padx=10, pady=(10, 0))
        tk.Label(master, text="Prazo (opcional, formato: DD-MM-YYYY HH:MM):").grid(row=1, column=0, sticky="w", padx=10)

        self.task_name_entry = tk.Entry(master)
        self.task_name_entry.grid(row=0, column=1, padx=10, pady=(10, 0))

        self.deadline_entry = tk.Entry(master)
        self.deadline_entry.grid(row=1, column=1, padx=10)

        return self.task_name_entry  # Focar no campo de nome da tarefa

    def apply(self):
        self.task_name = self.task_name_entry.get()
        self.deadline_str = self.deadline_entry.get()

class Task:
    def __init__(self, name, deadline=None):
        self.name = name
        self.deadline = deadline
        self.reminder_id = None

    def __str__(self):
        if self.deadline:
            return f"{self.name} (Prazo: {self.deadline.strftime('%d-%m-%Y %H:%M')})"
        else:
            return self.name

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Organizador de Tarefas")

        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", font=('Helvetica', 12), background='#D3D3D3', foreground='black')
        self.style.configure("TLabel", padding=6, font=('Helvetica', 12))
        self.style.configure("TListbox", font=('Helvetica', 12), background='#D3D3D3', foreground='black')

        # Adição da barra de status
        self.statusbar = tk.Label(root, text="Bem-vindo ao Organizador de Tarefas!", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.tasks = []

        self.task_listbox = tk.Listbox(root, selectmode=tk.SINGLE, height=15, width=50, font=('Helvetica', 12), bg='#D3D3D3', fg='black')
        self.task_listbox.pack(pady=10)

        self.add_button = ttk.Button(root, text="Adicionar Tarefa", command=self.add_task)
        self.add_button.pack(pady=5)

        self.edit_button = ttk.Button(root, text="Editar Tarefa", command=self.edit_task)
        self.edit_button.pack(pady=5)

        self.delete_button = ttk.Button(root, text="Excluir Tarefa", command=self.delete_task)
        self.delete_button.pack(pady=5)

        self.reminder_button = ttk.Button(root, text="Definir Lembrete", command=self.set_reminder)
        self.reminder_button.pack(pady=5)

        # Adição de um botão para personalizar cores
        # self.customize_colors_button = ttk.Button(root, text="Personalizar Cores", command=self.customize_colors)
        # self.customize_colors_button.pack(pady=5)

        self.schedule_reminders()

    def schedule_reminders(self):
        self.root.after(60000, self.check_reminders)  # Agendar verificação de lembretes a cada 1 minuto

    def check_reminders(self):
        now = datetime.now().time()
        for task in self.tasks:
            if task.deadline and now >= task.deadline.time():
                messagebox.showinfo("Lembrete", f"{task.name}: Lembrete programado para {task.deadline.strftime('%H:%M')}.")
        self.schedule_reminders()  # Agendar a próxima verificação

    def add_task(self):
        add_task_dialog = StyledAddTaskDialog(self.root, "Adicionar Tarefa")
        if add_task_dialog.task_name:
            deadline = self.parse_deadline(add_task_dialog.deadline_str)
            task = Task(add_task_dialog.task_name, deadline)
            self.tasks.append(task)
            self.update_task_listbox()
            self.set_status_message(f"Tarefa '{task.name}' adicionada com sucesso!")

    def edit_task(self):
        selected_task_index = self.get_selected_task_index()
        if selected_task_index is not None:
            selected_task = self.tasks[selected_task_index]
            new_task_name = simpledialog.askstring("Editar Tarefa", "Digite o novo nome da tarefa:",
                                                   initialvalue=selected_task.name)
            if new_task_name:
                selected_task.name = new_task_name
                self.update_task_listbox()
                self.set_status_message(f"Tarefa '{new_task_name}' editada com sucesso!")

    def delete_task(self):
        selected_task_index = self.get_selected_task_index()
        if selected_task_index is not None:
            deleted_task_name = self.tasks[selected_task_index].name
            del self.tasks[selected_task_index]
            self.update_task_listbox()
            self.set_status_message(f"Tarefa '{deleted_task_name}' excluída com sucesso!")

    def set_reminder(self):
        selected_task_index = self.get_selected_task_index()
        if selected_task_index is not None:
            selected_task = self.tasks[selected_task_index]
            reminder_time_str = simpledialog.askstring("Definir Lembrete",
                                                      f"Digite o lembrete para '{selected_task.name}' (formato: HH:MM):")
            if reminder_time_str:
                try:
                    reminder_time = datetime.strptime(reminder_time_str, "%H:%M").time()
                    selected_task.deadline = datetime.combine(datetime.today(), reminder_time)
                    messagebox.showinfo("Lembrete definido", f"Lembrete para '{selected_task.name}' às {reminder_time_str}.")
                    self.update_task_listbox()
                    self.set_status_message(f"Lembrete para '{selected_task.name}' definido com sucesso!")
                except ValueError:
                    messagebox.showerror("Erro", "Formato de hora inválido. Use HH:MM.")

    def customize_colors(self):
        color_bg, _ = colorchooser.askcolor(title="Escolha a cor de fundo")
        color_fg, _ = colorchooser.askcolor(title="Escolha a cor do texto")

        if color_bg and color_fg:
            self.style.configure("TButton", background=color_bg)
            self.style.configure("TLabel", background=color_bg)
            self.style.configure("TListbox", background=color_bg, foreground=color_fg)
            self.task_listbox.config(bg=color_bg, fg=color_fg)
            self.customize_colors_button.configure(bg=color_bg)
            self.statusbar.configure(bg=color_bg)
            self.root.configure(bg=color_bg)
            self.set_status_message("Cores personalizadas aplicadas com sucesso!")

    def update_task_listbox(self):
        self.task_listbox.delete(0, tk.END)
        for task in self.tasks:
            self.task_listbox.insert(tk.END, str(task))

    def get_selected_task_index(self):
        selected_task_index = self.task_listbox.curselection()
        if selected_task_index:
            return selected_task_index[0]
        return None

    @staticmethod
    def parse_deadline(deadline_str):
        if deadline_str:
            try:
                return datetime.strptime(deadline_str, "%d-%m-%Y %H:%M")
            except ValueError:
                messagebox.showerror("Erro", "Formato de prazo inválido. Use DD-MM-YYYY HH:MM.")
        return None

    def set_status_message(self, message):
        self.statusbar.config(text=message)

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()
