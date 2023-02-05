"""
MIT License

Copyright (c) 2023 Pebbles210200

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""
import sc2reader
import matplotlib.pyplot as plt
from tkinter import Tk
from tkinter.filedialog import askopenfilenames
import tkinter as tk
import datetime

def unix_to_formatted_date(unix_timestamp):
    return datetime.datetime.fromtimestamp(unix_timestamp).strftime('%d %b, %Y - %H:%M:%S')

def on_button_click(index):
    global result
    result = buttons[index]['text']
    root.quit()

def choose_button(title, choices):
    global buttons, result, root

    root = tk.Tk()
    root.title(title)
    root.geometry("600x100") # set the GUI size to 200x100 pixels
    root.configure(bg='#282828')

    buttons = []
    for i, choice in enumerate(choices):
        button = tk.Button(root, text=choice, bg='#3c3836', fg='#ebdbb2', command=lambda index=i: on_button_click(index))
        button.pack(side=tk.LEFT, padx=5, pady=5, expand=True, fill=tk.BOTH) # arrange buttons side by side, taking up half of the GUI each
        buttons.append(button)

    result = None
    root.mainloop()
    root.destroy()
    return result

def select_replays():
    Tk().withdraw()
    files = askopenfilenames(filetypes=[("Starcraft 2 Replay", "*.SC2Replay")])
    return files

def search_for_player_named(replay, player_name):
    player = None
    for p in replay.players:
        if player_name == p.name:
            return p
    return player

def collect_worker_count_over_time(replay, player):
    supply_count = []
    worker_count = []
    time_stamps = []
    current_worker_count = 0
    current_supply_count = 0
    for event in replay.tracker_events:
        if event.name == "UnitBornEvent":
            if event.unit.owner != None:
                if event.unit.owner.pid == player.pid:
                    if event.unit.is_worker:
                        current_worker_count += 1
                    current_supply_count += event.unit.supply
                    

        elif event.name == "UnitDiedEvent":
            if event.unit.owner != None:
                if event.unit.owner.pid == player.pid:
                    if event.unit.is_worker:
                        current_worker_count -= 1
                    current_supply_count -= event.unit.supply
        
        supply_count.append(current_supply_count)
        worker_count.append(current_worker_count)
        time_stamps.append(event.second)
    return supply_count, worker_count, time_stamps

def plot_worker_graph(supply_count_data, worker_count_data, time_stamps_data, legend_titles):
    for supply_count, worker_count, time_stamps, legend_title in zip(supply_count_data, worker_count_data, time_stamps_data, legend_titles):
        plt.plot(time_stamps, worker_count, label="Workers for " + legend_title)
        plt.plot(time_stamps, supply_count, label="Total for " + legend_title)
    plt.grid(True)
    plt.xlabel('Time (s)')
    plt.ylabel('Supply Count')
    plt.legend()
    plt.show()

def main():
    replay_files = select_replays()

    supply_count_data = []
    worker_count_data = []
    time_stamps_data = []
    legend_titles = []
    for replay_file in replay_files:
        replay = sc2reader.load_replay(replay_file)
        player_name_options = []
        for player in replay.players:
            player_name_options.append(player.name)
        
        title_str = ""
        
        for team in replay.teams:
            team_player_count = 0
            for player in team.players:
                if team_player_count != 0:
                    title_str += ", "
                title_str += player.name
            if team != replay.teams[-1]:
                title_str += " VS "

        title_str += " on " + unix_to_formatted_date(replay.unix_timestamp)

        player_name = choose_button("Choose Player for " + title_str, player_name_options)
               
        player = search_for_player_named(replay, player_name)
        
        legend_titles.append(player.name + " in " + title_str)
        supply_count, worker_count, time_stamps = collect_worker_count_over_time(replay, player)
        supply_count_data.append(supply_count)
        worker_count_data.append(worker_count)
        time_stamps_data.append(time_stamps)
    plot_worker_graph(supply_count_data, worker_count_data, time_stamps_data, legend_titles)

if __name__ == '__main__':
    main()

