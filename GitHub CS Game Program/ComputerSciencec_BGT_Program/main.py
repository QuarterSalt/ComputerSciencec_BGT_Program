import tkinter as tk
from tkinter import ttk, messagebox
import math
import json


class LeaderboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Player Scoring System")
        self.root.geometry("1920x1080")
        self.root.state('zoomed')  # Start maximized

        # Load data
        self.players_points_info = self.load_data()
        self.player_dict_info = {
            "NumberOfPlayers": 0,
            "TotalGlobalPoints": 0
        }

        # Create main container
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Leaderboard Panel (Left 60%)
        self.lb_frame = tk.Frame(self.main_frame, width=1152)
        self.lb_frame.pack(side='left', fill='both', expand=True)

        # Create canvas and scrollbar for leaderboard
        self.canvas = tk.Canvas(self.lb_frame)
        self.scrollbar = ttk.Scrollbar(self.lb_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)

        self.entries_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.entries_frame, anchor='nw')

        # Control Panel (Right 40%)
        self.control_frame = tk.Frame(self.main_frame, width=768, padx=20)
        self.control_frame.pack(side='right', fill='both', expand=True)

        # Create input controls
        self.create_input_controls()
        self.create_management_controls()

        # Initial population
        self.update_leaderboard()

        # Configure bindings
        self.entries_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def create_input_controls(self):
        # Add Player Section
        input_frame = ttk.LabelFrame(self.control_frame, text="Add Player Points", padding=15)
        input_frame.pack(fill='x', pady=10)

        # Player Name
        ttk.Label(input_frame, text="Player Name:").grid(row=0, column=0, sticky='w')
        self.player_name = ttk.Entry(input_frame, width=25)
        self.player_name.grid(row=0, column=1, padx=5, pady=5)

        # Game Duration
        ttk.Label(input_frame, text="Game Duration (mins):").grid(row=1, column=0, sticky='w')
        self.game_duration = ttk.Entry(input_frame, width=25)
        self.game_duration.grid(row=1, column=1, padx=5, pady=5)

        # Number of Players
        ttk.Label(input_frame, text="Number of Players:").grid(row=2, column=0, sticky='w')
        self.num_players = ttk.Entry(input_frame, width=25)
        self.num_players.grid(row=2, column=1, padx=5, pady=5)

        # Position
        ttk.Label(input_frame, text="Position Finished:").grid(row=3, column=0, sticky='w')
        self.position = ttk.Entry(input_frame, width=25)
        self.position.grid(row=3, column=1, padx=5, pady=5)

        # Submit Button
        ttk.Button(input_frame, text="Calculate Points", command=self.calculate_points).grid(row=4, column=0,columnspan=2, pady=10)

    def create_management_controls(self):
        # Manage Players Section
        manage_frame = ttk.LabelFrame(self.control_frame, text="Manage Players", padding=15)
        manage_frame.pack(fill='x', pady=10)

        # Delete Player
        ttk.Label(manage_frame, text="Player to Manage:").grid(row=0, column=0, sticky='w')
        self.del_player = ttk.Entry(manage_frame, width=25)
        self.del_player.grid(row=0, column=1, padx=5, pady=5)

        # Action Selection
        self.action_var = tk.StringVar()
        ttk.Radiobutton(manage_frame, text="Delete Player", variable=self.action_var, value="delete").grid(row=1,column=0,sticky='w')
        ttk.Radiobutton(manage_frame, text="Remove Points", variable=self.action_var, value="remove").grid(row=1,column=1,sticky='w')

        # Points to Remove
        ttk.Label(manage_frame, text="Points to Remove:").grid(row=2, column=0, sticky='w')
        self.points_to_remove = ttk.Entry(manage_frame, width=25)
        self.points_to_remove.grid(row=2, column=1, padx=5, pady=5)

        # Submit Button
        ttk.Button(manage_frame, text="Perform Action", command=self.perform_action).grid(row=3, column=0, columnspan=2,pady=10)

        # Save and Exit
        ttk.Button(self.control_frame, text="Save & Exit", command=self.save_and_exit).pack(pady=20)

    def load_data(self):
        try:
            with open('players_points_info.json', 'r') as f:
                content = f.read().strip()
                if not content:
                    return {}  # Empty file, return default empty dictionary
                return json.loads(content)  # Load properly formatted JSON
        except (FileNotFoundError, json.JSONDecodeError):
            return {}  # If file doesn't exist or JSON is corrupted, return empty dict

    def save_data(self):
        with open('players_points_info.json', 'w') as f:
            json.dump(self.players_points_info, f)
        print("\nData saved successfully.")

    def update_leaderboard(self):
        # Clear previous entries
        for widget in self.entries_frame.winfo_children():
            widget.destroy()

        # Update global stats
        self.player_dict_info["TotalGlobalPoints"] = sum(self.players_points_info.values())
        self.player_dict_info["NumberOfPlayers"] = len(self.players_points_info)

        # Create header with column configuration
        header_frame = tk.Frame(self.entries_frame, bg="lightgray")
        header_frame.grid(row=0, column=0, columnspan=3, sticky="ew")

        # Configure header columns (must match row_frame columns)
        header_frame.columnconfigure(0, weight=1, uniform="col")
        header_frame.columnconfigure(1, weight=1, uniform="col")
        header_frame.columnconfigure(2, weight=1, uniform="col")

        # Header labels with fixed width and centered text
        tk.Label(header_frame, text="Rank", font=("Arial", 12, "bold"),
                 bg="lightgray", width=8, anchor='center').grid(row=0, column=0, sticky='nsew')
        tk.Label(header_frame, text="Name", font=("Arial", 12, "bold"),
                 bg="lightgray", width=25, anchor='center').grid(row=0, column=1, sticky='nsew')
        tk.Label(header_frame, text="Score", font=("Arial", 12, "bold"),
                 bg="lightgray", width=10, anchor='center').grid(row=0, column=2, sticky='nsew')

        # Create entries with aligned columns
        sorted_players = sorted(self.players_points_info.items(), key=lambda x: x[1], reverse=True)
        for idx, (name, score) in enumerate(sorted_players, start=1):
            bg_color = "#f0f0f0" if idx % 2 else "white"

            row_frame = tk.Frame(self.entries_frame, bg=bg_color)
            row_frame.grid(row=idx, column=0, columnspan=3, sticky="ew")

            # Match column configuration with header
            row_frame.columnconfigure(0, weight=1, uniform="col")
            row_frame.columnconfigure(1, weight=1, uniform="col")
            row_frame.columnconfigure(2, weight=1, uniform="col")

            # Data labels with same width/alignment as headers
            tk.Label(row_frame, text=str(idx), bg=bg_color, width=8, anchor='center'
                     ).grid(row=0, column=0, sticky='nsew')
            tk.Label(row_frame, text=name, bg=bg_color, width=25, anchor='center'
                     ).grid(row=0, column=1, sticky='nsew')
            tk.Label(row_frame, text=str(score), bg=bg_color, width=10, anchor='center'
                     ).grid(row=0, column=2, sticky='nsew')

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def calculate_points(self):
        try:
            # Get input values
            player_name = self.player_name.get().strip()
            game_duration = float(self.game_duration.get())
            num_players = int(self.num_players.get())
            position = int(self.position.get())

            if not player_name:
                messagebox.showerror("Error", "Please enter a player name")
                return

            # Calculate points
            if not self.players_points_info:
                average_points = 1
                current_points = 1
            else:
                average_points = sum(self.players_points_info.values()) / len(self.players_points_info)
                current_points = self.players_points_info.get(player_name, 1)

            base_points = (game_duration / 2) + (num_players * 3)
            position_bonus = num_players / position / 10
            relative_position = average_points / current_points / 25 + 1

            if relative_position > 1.2: # Makes sure the multiplier isn't too large
                relative_position = 1.2

            if relative_position < 0.8: # Makes sure the multiplier isn't too small
                relative_position = 0.8

            awarded_points = math.floor(base_points * position_bonus)
            awarded_points += math.floor(relative_position * awarded_points * relative_position)

            # Update points
            if player_name not in self.players_points_info:
                self.players_points_info[player_name] = 0
            self.players_points_info[player_name] += awarded_points

            # Clear input fields after successful submission
            self.player_name.delete(0, tk.END)
            self.game_duration.delete(0, tk.END)
            self.num_players.delete(0, tk.END)
            self.position.delete(0, tk.END)

            self.update_leaderboard()
            messagebox.showinfo("Success", f"{player_name} awarded {awarded_points} points!")

        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {str(e)}")

    def perform_action(self):
        player = self.del_player.get().strip()
        action = self.action_var.get()

        if not player or player not in self.players_points_info:
            messagebox.showerror("Error", "Player not found")
            return

        if action == "delete":
            del self.players_points_info[player]
            messagebox.showinfo("Success", f"{player} deleted")
        elif action == "remove":
            try:
                points = int(self.points_to_remove.get())
                self.players_points_info[player] = max(0, self.players_points_info[player] - points)
                messagebox.showinfo("Success", f"Removed {points} points from {player}")
            except ValueError:
                messagebox.showerror("Error", "Invalid points value")

        # Clear management fields after action
        self.del_player.delete(0, tk.END)
        self.points_to_remove.delete(0, tk.END)
        self.action_var.set("")

        self.update_leaderboard()

    def save_and_exit(self):
        self.save_data()
        self.root.destroy()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


if __name__ == "__main__":
    root = tk.Tk()
    app = LeaderboardApp(root)
    root.mainloop()