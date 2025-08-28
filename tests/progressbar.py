import tkinter as tk
from tkinter import ttk
import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor

def worker(task_id, progress_queue):
    """Simule un travail et informe la prog bar."""
    for i in range(5):
        time.sleep(2)  # travail simulé
    print(str(task_id) + " done")
    progress_queue.put(1)  # informe qu'un thread est terminé

class App(tk.Tk):
    def __init__(self, num_threads):
        super().__init__()
        self.title("Progression multithread")
        self.progress = ttk.Progressbar(self, orient="horizontal",
                                        length=300, mode="indeterminate",
                                        maximum=num_threads)
        self.progress.pack(pady=20)

        self.start_button = ttk.Button(self, text="Démarrer", command=self.start)
        self.start_button.pack()

        self.num_threads = num_threads
        self.progress_queue = queue.Queue()

    def start(self):
        self.start_button.config(state=tk.DISABLED)
        self.progress["value"] = 0

        # Lancement du pool de threads
        self.pool = ThreadPoolExecutor(max_workers=self.num_threads)
        for task_id in range(self.num_threads):
            self.pool.submit(worker, task_id, self.progress_queue)

        # Démarre la boucle d'update de la progressbar
        self.after(100, self.check_queue)

    def check_queue(self):
        try:
            while True:
                self.progress.step(1)
                self.progress_queue.get_nowait()
        except queue.Empty:
            pass

        if self.progress["value"] < self.num_threads:
            self.after(100, self.check_queue)
        else:
            self.pool.shutdown(wait=False)
            self.start_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    app = App(num_threads=10)
    app.mainloop()
