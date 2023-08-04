import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import youtube_search
import youtube_dl
import vlc

class YouTubePlayer(Gtk.Window):
    def __init__(self):
        super(YouTubePlayer, self).__init__(title="YouTube Player")
        self.set_default_size(600, 400)
        self.player = vlc.MediaPlayer()
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(True)
        self.activeId = None
        self.init_ui()

    def init_ui(self):
        # Create widgets
        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Enter search query")
        self.search_entry.set_hexpand(True)
        self.search_entry.connect("activate", self.on_search)
        self.search_button = Gtk.Button(label="Search")
        self.search_button.connect("clicked", self.on_search)
        self.play_button = Gtk.Button(label="Play")
        self.play_button.set_sensitive(False)
        self.play_button.connect("clicked", self.on_play)
        self.pause_button = Gtk.Button(label="Pause")
        self.pause_button.set_sensitive(False)
        self.pause_button.connect("clicked", self.on_pause)
        self.song_title = Gtk.Label(label="None")
        self.song_title.set_halign(Gtk.Align.START)
        self.song_title.set_valign(Gtk.Align.START)
        self.song_title.set_hexpand(True)

        # List to display search results
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.listbox.connect("row-activated", self.on_list_item_activated)

        # Store the video_id associated with each ListBoxRow
        self.video_ids = {}

        # Layout
        grid = Gtk.Grid()
        # Set padding
        grid.set_border_width(10)
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        grid.attach(self.search_entry, 0, 0, 2, 1)
        grid.attach(self.search_button, 2, 0, 1, 1)
        grid.attach(self.listbox, 0, 1, 3, 5)
        grid.attach(self.play_button, 0, 6, 1, 1)
        grid.attach(self.pause_button, 1, 6, 1, 1)
        # Attach song title to the bottom of the window
        grid.attach(self.song_title, 0, 7, 1, 1)

        # Add the grid to the window
        self.add(grid)

    def on_search(self, button):
        query = self.search_entry.get_text()
        search_results = youtube_search.YoutubeSearch(query, max_results=5).to_dict()

        # Clear previous search results
        self.listbox.foreach(lambda row: self.listbox.remove(row))
        self.video_ids.clear()

        # Display search results in the list
        index = 0
        for result in search_results:
            title = result['title']
            video_id = result['id']
            row = Gtk.Label(label=title, xalign=0)
            self.listbox.add(row)
            self.video_ids[index] = video_id  # Store the video ID associated with the row
            index += 1

        # Show the listbox and enable the Play button
        self.play_button.set_sensitive(True)
        self.pause_button.set_sensitive(True)
        self.listbox.show_all()

    def on_list_item_activated(self, listbox, row):
        index = row.get_index()
        # Get the selected video_id from the associated dictionary
        video_id = self.video_ids.get(index)
        if video_id:
            self.activeId = video_id

    def on_play(self, button):
        if self.activeId:
            self.play_video(self.activeId)

    def play_video(self, video_id):
        # Get audio stream URL using youtube_dl
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        #BEST AUDIO
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192'
            }],
            'postprocessor_args': [
                '-ar', '16000'
            ],
            'prefer_ffmpeg': True,
            'keepvideo': True
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            audio_url = info_dict['formats'][0]['url']

        # Initialize and play the audio using python-vlc
        self.player.set_media(vlc.Media(audio_url))
        self.player.play()
        self.song_title.set_text("Now playing: " + info_dict['title'])

    def on_pause(self, button):
        if self.player:
            self.player.pause()


if __name__ == "__main__":
    win = YouTubePlayer()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
