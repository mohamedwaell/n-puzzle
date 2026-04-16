import tkinter as tk
from tkinter import messagebox
import puzzle_logic as logic
import solver
import time
import winsound
import os
from PIL import Image, ImageTk

class NPuzzleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("N-Puzzle")
        # Modern Slate Theme
        self.bg_color = "#0f172a"
        self.card_color = "#1e293b"
        self.accent_color = "#10b981"
        self.text_primary = "#f8fafc"
        self.text_secondary = "#94a3b8"
        
        self.root.configure(bg=self.bg_color)
        self.root.geometry("400x700")
        self.root.resizable(False, False)
        
        self.size = 3
        self.board = []
        self.buttons = []
        self.is_solving = False
        self.moves = 0
        self.start_time = None
        
        self.main_container = tk.Frame(self.root, bg=self.bg_color)
        self.main_container.pack(expand=True, fill="both")
        
        # Load Win Image (Animated WebP support)
        self.win_image_path = os.path.join("images", "5d52c915-ea5b-40c7-8f44-4a8f3879e7f1.webp")
        self.win_frames = []
        self.current_win_frame = 0
        self.win_animation_id = None
        
        if os.path.exists(self.win_image_path):
            try:
                img = Image.open(self.win_image_path)
                n_frames = getattr(img, "n_frames", 1)
                for i in range(n_frames):
                    img.seek(i)
                    frame = img.convert("RGBA").resize((200, 200), Image.Resampling.LANCZOS)
                    self.win_frames.append(ImageTk.PhotoImage(frame))
            except Exception as e:
                print(f"Error loading win image: {e}")

        # Load Splash Image
        self.splash_image_path = os.path.join("images", "splash.png")
        self.splash_photo = None
        if os.path.exists(self.splash_image_path):
            try:
                img = Image.open(self.splash_image_path)
                img = img.resize((240, 240), Image.Resampling.LANCZOS)
                self.splash_photo = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Error loading splash image: {e}")

        self.show_menu()

    def play_sound(self, sound_file):
        if os.path.exists(sound_file):
            try:
                winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except:
                pass

    def stop_sound(self):
        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
        except:
            pass

    def clear_container(self):
        if self.win_animation_id:
            self.root.after_cancel(self.win_animation_id)
            self.win_animation_id = None
            
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def format_time(self, seconds):
        mins, secs = divmod(int(seconds), 60)
        return f"{mins:02d}:{secs:02d}"

    def show_menu(self):
        self.stop_sound()
        self.clear_container()
        self.root.geometry("400x700")
        
        menu_content = tk.Frame(self.main_container, bg=self.bg_color)
        menu_content.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(menu_content, text="N-Puzzle", font=("Helvetica", 36, "bold"), 
                 bg=self.bg_color, fg=self.text_primary, pady=10).pack()

        if self.splash_photo:
            tk.Label(menu_content, image=self.splash_photo, bg=self.bg_color).pack(pady=10)

        tk.Button(menu_content, text="Start Game", font=("Helvetica", 16, "bold"),
                  bg=self.accent_color, fg="white", width=20, pady=10, relief="flat",
                  cursor="hand2", command=self.show_size_selection).pack(pady=30)

        tk.Label(menu_content, text="Made by Mohamed Wael", font=("Helvetica", 12),
                 bg=self.bg_color, fg=self.text_secondary).pack(pady=20)

    def show_size_selection(self):
        self.stop_sound()
        self.clear_container()
        
        selection_content = tk.Frame(self.main_container, bg=self.bg_color)
        selection_content.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(selection_content, text="Choose Grid Size", font=("Helvetica", 24, "bold"), 
                 bg=self.bg_color, fg=self.text_primary, pady=20).pack()

        tk.Button(selection_content, text="3 x 3", font=("Helvetica", 14, "bold"),
                  bg="#334155", fg="white", width=20, pady=10, relief="flat",
                  cursor="hand2", command=lambda: self.initialize_game(3)).pack(pady=10)

        tk.Button(selection_content, text="4 x 4", font=("Helvetica", 14, "bold"),
                  bg="#334155", fg="white", width=20, pady=10, relief="flat",
                  cursor="hand2", command=lambda: self.initialize_game(4)).pack(pady=10)
        
        tk.Button(selection_content, text="← Back", font=("Helvetica", 11),
                  bg=self.bg_color, fg=self.text_secondary, bd=0, command=self.show_menu).pack(pady=20)

    def initialize_game(self, size):
        self.size = size
        self.moves = 0
        self.start_time = time.time()
        self.setup_ui()
        self.shuffle_board()

    def setup_ui(self):
        self.clear_container()
        self.buttons = []
        
        if self.size == 4:
            self.root.geometry("500x820")
            btn_font = ("Helvetica", 22, "bold")
            btn_width = 4
            btn_height = 2
            title_font = ("Helvetica", 28, "bold")
        else:
            self.root.geometry("400x700")
            btn_font = ("Helvetica", 26, "bold")
            btn_width = 4
            btn_height = 2
            title_font = ("Helvetica", 24, "bold")
            
        # Header
        title_text = f"{self.size*self.size - 1}-Puzzle Game"
        self.header = tk.Label(self.main_container, text=title_text, font=title_font, 
                              bg=self.bg_color, fg=self.text_primary, pady=30)
        self.header.pack()

        # Game Board Frame
        self.board_frame = tk.Frame(self.main_container, bg=self.card_color, padx=12, pady=12)
        self.board_frame.pack(padx=20, pady=10)

        for i in range(self.size * self.size):
            btn = tk.Button(self.board_frame, text="", font=btn_font, 
                           width=btn_width, height=btn_height, bd=0, relief="flat", highlightthickness=0,
                           command=lambda idx=i: self.on_tile_click(idx))
            btn.grid(row=i//self.size, column=i%self.size, padx=6, pady=6)
            self.buttons.append(btn)

        # Controls Frame
        self.control_frame = tk.Frame(self.main_container, bg=self.bg_color, pady=20)
        self.control_frame.pack()

        self.btn_reset = tk.Button(self.control_frame, text="Shuffle", font=("Helvetica", 11, "bold"),
                                   bg="#334155", fg="white", width=12, pady=5, relief="flat", command=self.shuffle_board)
        self.btn_reset.grid(row=0, column=0, padx=10)

        self.btn_solve = tk.Button(self.control_frame, text="AI Solve", font=("Helvetica", 11, "bold"),
                                  bg=self.accent_color, fg="white", width=12, pady=5, relief="flat", command=self.ai_solve)
        self.btn_solve.grid(row=0, column=1, padx=10)

        # Status and Moves Frame
        self.info_frame = tk.Frame(self.main_container, bg=self.bg_color)
        self.info_frame.pack(pady=10)

        self.moves_var = tk.StringVar(value="Moves: 0")
        tk.Label(self.info_frame, textvariable=self.moves_var, font=("Helvetica", 16, "bold"),
                 bg=self.bg_color, fg=self.accent_color).pack(side="left", padx=20)

        self.status_var = tk.StringVar(value="Solve it!")
        tk.Label(self.info_frame, textvariable=self.status_var, font=("Helvetica", 14),
                 bg=self.bg_color, fg=self.text_secondary).pack(side="left", padx=20)

        # Home Button at the bottom
        home_btn = tk.Button(self.main_container, text="🏠", font=("Helvetica", 24),
                            bg=self.bg_color, fg=self.text_secondary, bd=0, 
                            activebackground=self.bg_color, activeforeground=self.text_primary,
                            cursor="hand2", command=self.show_menu)
        home_btn.pack(side="bottom", pady=20)

    def update_board(self):
        goal = list(range(1, self.size * self.size)) + [0]
        for i in range(self.size * self.size):
            val = self.board[i]
            if val == 0:
                self.buttons[i].config(text="", bg=self.card_color, state="disabled")
            else:
                self.buttons[i].config(text=str(val), bg="#f1f5f9", fg="#1e293b", 
                                      state="normal" if not self.is_solving else "disabled")
        
        if self.board == goal and not self.is_solving:
            elapsed = time.time() - self.start_time
            self.play_sound('audio/win.wav')
            self.root.after(500, lambda: self.show_win_screen(elapsed))
        
        self.moves_var.set(f"Moves: {self.moves}")

    def on_tile_click(self, idx):
        if self.is_solving: return
        
        blank_idx = self.board.index(0)
        r1, c1 = divmod(idx, self.size)
        r2, c2 = divmod(blank_idx, self.size)
        
        if abs(r1-r2) + abs(c1-c2) == 1:
            self.board[idx], self.board[blank_idx] = self.board[blank_idx], self.board[idx]
            self.moves += 1
            self.play_sound('audio/move.wav')
            self.update_board()

    def shuffle_board(self):
        self.play_sound('audio/shuffle.wav')
        self.board = logic.generate_solvable_puzzle(self.size)
        self.is_solving = False
        self.btn_solve.config(state="normal")
        self.btn_reset.config(state="normal")
        self.moves = 0
        self.start_time = time.time()
        self.update_board()
        self.status_var.set("Solve it!")

    def ai_solve(self):
        goal = list(range(1, self.size * self.size)) + [0]
        if self.board == goal:
            return

        self.is_solving = True
        self.btn_solve.config(state="disabled")
        self.btn_reset.config(state="disabled")
        self.status_var.set("AI thinking...")
        self.root.update()

        # Run solver in background would be better, but for now we'll just wait
        path = solver.solve_puzzle(self.board, self.size)
        if path:
            self.animate_solution(path)
        else:
            self.is_solving = False
            self.status_var.set("No solution found")
            self.btn_solve.config(state="normal")
            self.btn_reset.config(state="normal")

    def show_win_screen(self, elapsed_time):
        self.clear_container()
        self.root.geometry("400x700")
        
        win_container = tk.Frame(self.main_container, bg=self.bg_color)
        win_container.place(relx=0.5, rely=0.5, anchor="center")

        if self.win_frames:
            self.win_image_label = tk.Label(win_container, image=self.win_frames[0], bg=self.bg_color)
            self.win_image_label.pack(pady=20)
            self.current_win_frame = 0
            if len(self.win_frames) > 1:
                self.play_win_animation()
        else:
            trophy_frame = tk.Frame(win_container, bg="#16213e", width=100, height=100)
            trophy_frame.pack_propagate(False)
            trophy_frame.pack(pady=20)
            tk.Label(trophy_frame, text="🏆", font=("Helvetica", 40), bg="#16213e", fg=self.accent_color).place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(win_container, text="You Won! 🥳", font=("Helvetica", 32, "bold"),
                 bg=self.bg_color, fg=self.accent_color).pack(pady=(10, 5))
        
        tk.Label(win_container, text=f"Masterful execution. The {self.size*self.size-1}-puzzle\nis complete.", 
                 font=("Helvetica", 12), bg=self.bg_color, fg=self.text_secondary, justify="center").pack(pady=5)

        stats_frame = tk.Frame(win_container, bg=self.bg_color)
        stats_frame.pack(pady=20)

        moves_box = tk.Frame(stats_frame, bg=self.card_color, padx=15, pady=15, width=100, height=100)
        moves_box.pack_propagate(False)
        moves_box.pack(side="left", padx=10)
        tk.Label(moves_box, text="TOTAL\nMOVES", font=("Helvetica", 8, "bold"), bg=self.card_color, fg=self.text_secondary).pack()
        tk.Label(moves_box, text=str(self.moves), font=("Helvetica", 24, "bold"), bg=self.card_color, fg="#f1f5f9").pack()

        time_box = tk.Frame(stats_frame, bg=self.card_color, padx=15, pady=15, width=100, height=100)
        time_box.pack_propagate(False)
        time_box.pack(side="left", padx=10)
        tk.Label(time_box, text="TIME\nELAPSED", font=("Helvetica", 8, "bold"), bg=self.card_color, fg=self.text_secondary).pack()
        tk.Label(time_box, text=self.format_time(elapsed_time), font=("Helvetica", 20, "bold"), bg=self.card_color, fg=self.accent_color).pack()

        tk.Button(win_container, text="Play Again  →", font=("Helvetica", 14, "bold"),
                  bg=self.accent_color, fg="white", width=18, pady=12, relief="flat",
                  cursor="hand2", command=self.show_size_selection).pack(pady=20)

        tk.Button(win_container, text="Back to Menu", font=("Helvetica", 11, "bold"),
                  bg=self.bg_color, fg=self.text_secondary, bd=0, activebackground=self.bg_color,
                  activeforeground=self.text_primary, cursor="hand2", command=self.show_menu).pack()

    def play_win_animation(self):
        if not hasattr(self, 'win_image_label') or not self.win_image_label.winfo_exists():
            return
            
        self.current_win_frame = (self.current_win_frame + 1) % len(self.win_frames)
        self.win_image_label.config(image=self.win_frames[self.current_win_frame])
        self.win_animation_id = self.root.after(80, self.play_win_animation)

    def animate_solution(self, path):
        if not path:
            self.is_solving = False
            self.btn_solve.config(state="normal")
            self.btn_reset.config(state="normal")
            self.update_board()
            return
        
        self.board = path.pop(0)
        self.moves += 1
        self.update_board()
        self.status_var.set(f"Solving... {len(path)}")
        # Check if still in game (didn't go back to menu)
        if hasattr(self, 'board_frame') and self.board_frame.winfo_exists():
            self.root.after(200, lambda: self.animate_solution(path))

if __name__ == "__main__":
    root = tk.Tk()
    app = NPuzzleGUI(root)
    root.mainloop()
