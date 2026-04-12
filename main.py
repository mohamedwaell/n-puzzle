import tkinter as tk
from tkinter import messagebox
import puzzle_logic as logic
import solver
import time
import winsound
import os

class NPuzzleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle AI Solver")
        self.root.configure(bg="#2c3e50")
        
        self.board = [1, 2, 3, 4, 5, 6, 7, 8, 0] # Goal state
        self.buttons = []
        self.is_solving = False
        self.moves = 0
        
        self.setup_ui()
        self.shuffle_board() # Start shuffled

    def play_sound(self, sound_file):
        if os.path.exists(sound_file):
            winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)

    def setup_ui(self):
        # Header
        self.header = tk.Label(self.root, text="8-Puzzle Game", font=("Helvetica", 24, "bold"), 
                              bg="#2c3e50", fg="#ecf0f1", pady=20)
        self.header.pack()

        # Game Board Frame
        self.board_frame = tk.Frame(self.root, bg="#34495e", bd=5, relief="ridge")
        self.board_frame.pack(padx=20, pady=10)

        for i in range(9):
            btn = tk.Button(self.board_frame, text="", font=("Helvetica", 24, "bold"), 
                           width=4, height=2, bd=2, relief="flat",
                           command=lambda idx=i: self.on_tile_click(idx))
            btn.grid(row=i//3, column=i%3, padx=5, pady=5)
            self.buttons.append(btn)

        # Controls Frame
        self.control_frame = tk.Frame(self.root, bg="#2c3e50", pady=20)
        self.control_frame.pack()

        self.btn_reset = tk.Button(self.control_frame, text="Reset", font=("Helvetica", 12, "bold"),
                                   bg="#e67e22", fg="white", width=15, command=self.shuffle_board)
        self.btn_reset.grid(row=0, column=0, padx=10, columnspan=2)

        self.btn_solve = tk.Button(self.control_frame, text="AI Solve", font=("Helvetica", 12, "bold"),
                                  bg="#2ecc71", fg="white", width=15, command=self.ai_solve)
        self.btn_solve.grid(row=0, column=2, padx=10, columnspan=2)

        # Status and Moves Frame
        self.info_frame = tk.Frame(self.root, bg="#2c3e50")
        self.info_frame.pack(pady=5)

        self.moves_var = tk.StringVar(value="Moves: 0")
        self.moves_label = tk.Label(self.info_frame, textvariable=self.moves_var, font=("Helvetica", 14, "bold"),
                                   bg="#2c3e50", fg="#f1c40f")
        self.moves_label.pack(side="left", padx=20)

        self.status_var = tk.StringVar(value="Click Shuffle to Start!")
        self.status_label = tk.Label(self.info_frame, textvariable=self.status_var, font=("Helvetica", 12),
                                    bg="#2c3e50", fg="#bdc3c7")
        self.status_label.pack(side="left", padx=20)

    def update_board(self):
        for i in range(9):
            val = self.board[i]
            if val == 0:
                self.buttons[i].config(text="", bg="#34495e", state="disabled")
            else:
                self.buttons[i].config(text=str(val), bg="#ecf0f1", state="normal" if not self.is_solving else "disabled")
        
        if self.board == [1, 2, 3, 4, 5, 6, 7, 8, 0] and not self.is_solving:
            self.status_var.set("Solved! 🎉")
            self.play_sound('audio/win.wav')
            self.show_win_popup()
            for btn in self.buttons:
                btn.config(state="disabled")
        
        self.moves_var.set(f"Moves: {self.moves}")

    def on_tile_click(self, idx):
        if self.is_solving: return
        
        blank_idx = self.board.index(0)
        r1, c1 = divmod(idx, 3)
        r2, c2 = divmod(blank_idx, 3)
        
        # Check if adjacent
        if abs(r1-r2) + abs(c1-c2) == 1:
            self.board[idx], self.board[blank_idx] = self.board[blank_idx], self.board[idx]
            self.moves += 1
            self.play_sound('audio/move.wav')
            self.update_board()

    def shuffle_board(self):
        self.play_sound('audio/shuffle.wav')
        self.board = logic.generate_solvable_puzzle()
        self.is_solving = False
        self.moves = 0
        self.update_board()
        self.status_var.set("Try to solve it!")


    def ai_solve(self):
        if self.board == [1, 2, 3, 4, 5, 6, 7, 8, 0]:
            messagebox.showinfo("Info", "The puzzle is already solved!")
            return

        self.is_solving = True
        self.btn_solve.config(state="disabled")
        self.btn_reset.config(state="disabled")
        self.status_var.set("AI is thinking...")
        self.root.update()

        path = solver.solve_puzzle(self.board)
        if path:
            self.moves = 0 # Reset moves for AI session? Or keep?
            # User usually wants to see the total moves from start if they solve it.
            # But AI path has its own length. Let's reset it to show AI steps.
            self.animate_solution(path)
        else:
            self.is_solving = False
            self.update_board()
            messagebox.showerror("Error", "No solution found!")

    def show_win_popup(self):
        # Create a custom popup window
        win_dialog = tk.Toplevel(self.root)
        win_dialog.title("Victory!")
        win_dialog.geometry("300x250")
        win_dialog.configure(bg="#2c3e50")
        win_dialog.resizable(False, False)
        
        # Center the popup relative to the main window
        win_dialog.transient(self.root)
        win_dialog.grab_set()
        
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        win_dialog.geometry(f"+{main_x + 50}+{main_y + 100}")

        # Content
        tk.Label(win_dialog, text="You Won! 🎉", font=("Helvetica", 24, "bold"),
                 bg="#2c3e50", fg="#f1c40f", pady=20).pack()
        
        tk.Label(win_dialog, text=f"Total Moves: {self.moves}", font=("Helvetica", 14),
                 bg="#2c3e50", fg="#ecf0f1", pady=10).pack()

        def play_again():
            win_dialog.destroy()
            self.shuffle_board()

        tk.Button(win_dialog, text="Play Again", font=("Helvetica", 12, "bold"),
                  bg="#2ecc71", fg="white", width=12, pady=10, relief="flat",
                  command=play_again).pack(pady=20)

    def animate_solution(self, path):
        if not path:
            self.is_solving = False
            self.btn_solve.config(state="normal")
            self.btn_reset.config(state="normal")
            self.update_board()
            return
        
        self.board = path.pop(0)
        self.moves += 1
        self.play_sound('audio/move.wav')
        self.update_board()
        self.status_var.set(f"AI Solving... {len(path)} steps left")
        
        # Delay for animation
        self.root.after(300, lambda: self.animate_solution(path))

if __name__ == "__main__":
    root = tk.Tk()
    app = NPuzzleGUI(root)
    root.mainloop()
