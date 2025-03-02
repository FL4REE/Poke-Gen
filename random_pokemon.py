import tkinter as tk
from tkinter import ttk, messagebox
import requests
from PIL import Image, ImageTk
from io import BytesIO
import random
import json
import os
import concurrent.futures
from typing import List, Dict, Optional, Set, Tuple
import threading
import time

# Cache directories
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')
SPRITE_CACHE_DIR = os.path.join(CACHE_DIR, 'sprites')
DATA_CACHE_FILE = os.path.join(CACHE_DIR, 'pokemon_data.json')
SPECIES_CACHE_FILE = os.path.join(CACHE_DIR, 'species_data.json')

# Ensure cache directories exist
os.makedirs(SPRITE_CACHE_DIR, exist_ok=True)

# Initialize caches
pokemon_cache: Dict[int, Dict] = {}
species_cache: Dict[int, Dict] = {}
evolution_cache: Dict[int, List[int]] = {}
sprite_cache: Dict[str, ImageTk.PhotoImage] = {}

class DraculaTheme:
    """Dracula color theme constants"""
    BACKGROUND = "#282a36"
    CURRENT_LINE = "#44475a"
    SELECTION = "#44475a"
    FOREGROUND = "#f8f8f2"
    COMMENT = "#6272a4"
    CYAN = "#8be9fd"
    GREEN = "#50fa7b"
    ORANGE = "#ffb86c"
    PINK = "#ff79c6"
    PURPLE = "#bd93f9"
    RED = "#ff5555"
    YELLOW = "#f1fa8c"

def load_cache():
    """Load cached data from files."""
    global pokemon_cache, species_cache
    try:
        if os.path.exists(DATA_CACHE_FILE):
            with open(DATA_CACHE_FILE, 'r') as f:
                pokemon_cache = json.load(f)
        if os.path.exists(SPECIES_CACHE_FILE):
            with open(SPECIES_CACHE_FILE, 'r') as f:
                species_cache = json.load(f)
    except Exception as e:
        print(f"Error loading cache: {e}")

def save_cache():
    """Save cached data to files."""
    try:
        with open(DATA_CACHE_FILE, 'w') as f:
            json.dump(pokemon_cache, f)
        with open(SPECIES_CACHE_FILE, 'w') as f:
            json.dump(species_cache, f)
    except Exception as e:
        print(f"Error saving cache: {e}")

def get_sprite_path(url: str) -> str:
    """Get the local path for a sprite URL."""
    return os.path.join(SPRITE_CACHE_DIR, url.split('/')[-1])

def load_sprite(url: str, size: Tuple[int, int] = (150, 150)) -> Optional[ImageTk.PhotoImage]:
    """Load a sprite from cache or download it."""
    if url in sprite_cache:
        return sprite_cache[url]
    
    sprite_path = get_sprite_path(url)
    try:
        if os.path.exists(sprite_path):
            image = Image.open(sprite_path)
        else:
            response = requests.get(url)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
            image.save(sprite_path)
        
        image = image.resize(size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        sprite_cache[url] = photo
        return photo
    except Exception as e:
        print(f"Error loading sprite: {e}")
        return None

def prefetch_pokemon_data(pokemon_ids: List[int]):
    """Prefetch Pokemon data in parallel."""
    def fetch_single_pokemon(pokemon_id: int):
        if pokemon_id not in pokemon_cache:
            try:
                response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}")
                response.raise_for_status()
                pokemon_cache[pokemon_id] = response.json()
            except Exception:
                pass
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(fetch_single_pokemon, pokemon_ids)

def prefetch_species_data(pokemon_ids: List[int]):
    """Prefetch species data in parallel."""
    def fetch_single_species(pokemon_id: int):
        if pokemon_id not in species_cache:
            try:
                response = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_id}")
                response.raise_for_status()
                species_cache[pokemon_id] = response.json()
            except Exception:
                pass
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(fetch_single_species, pokemon_ids)

class GenerationSelector(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=DraculaTheme.BACKGROUND)
        self.checkboxes = []
        self.vars = []
        
        # Create title
        title = tk.Label(self,
                        text="Generationen-Auswahl",
                        font=('Arial', 14, 'bold'),
                        bg=DraculaTheme.BACKGROUND,
                        fg=DraculaTheme.ORANGE)
        title.pack(anchor='w', pady=(0, 10))
        
        # Create checkbox container
        checkbox_container = tk.Frame(self, bg=DraculaTheme.BACKGROUND)
        checkbox_container.pack(fill=tk.X)
        
        # Create checkboxes for each generation
        for i in range(9):
            var = tk.BooleanVar(value=True)
            self.vars.append(var)
            cb = tk.Checkbutton(checkbox_container, 
                              text=f"Gen {i+1}", 
                              variable=var,
                              font=('Arial', 10),
                              bg=DraculaTheme.BACKGROUND,
                              fg=DraculaTheme.FOREGROUND,
                              selectcolor=DraculaTheme.CURRENT_LINE,
                              activebackground=DraculaTheme.BACKGROUND,
                              activeforeground=DraculaTheme.YELLOW)
            cb.pack(side=tk.LEFT, padx=5)
            self.checkboxes.append(cb)
    
    def get_selected_generations(self) -> List[int]:
        return [i+1 for i, var in enumerate(self.vars) if var.get()]

class PokemonSelector(ttk.Combobox):
    def __init__(self, master, pokemon_list):
        super().__init__(master, width=15)
        self['values'] = [''] + pokemon_list
        self.set('')

def get_pokemon_data(pokemon_id: int) -> Dict:
    """Fetch Pokemon data from cache or PokeAPI."""
    if pokemon_id in pokemon_cache:
        return pokemon_cache[pokemon_id]
    
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        pokemon_cache[pokemon_id] = data
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Pokemon data: {e}")
        return None

def get_pokemon_species_data(pokemon_id: int) -> Dict:
    """Fetch Pokemon species data from cache or PokeAPI."""
    if pokemon_id in species_cache:
        return species_cache[pokemon_id]
    
    url = f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        species_cache[pokemon_id] = data
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Pokemon species data: {e}")
        return None

def get_evolution_chain(pokemon_id: int) -> List[int]:
    """Get the evolution chain for a Pokemon."""
    if pokemon_id in evolution_cache:
        return evolution_cache[pokemon_id]
    
    species_data = get_pokemon_species_data(pokemon_id)
    if not species_data:
        return []
    
    try:
        evolution_url = species_data['evolution_chain']['url']
        response = requests.get(evolution_url)
        response.raise_for_status()
        evolution_data = response.json()
        
        evolution_chain = []
        def extract_chain(chain_data):
            species_url = chain_data['species']['url']
            pokemon_id = int(species_url.split('/')[-2])
            evolution_chain.append(pokemon_id)
            
            for evolved in chain_data.get('evolves_to', []):
                extract_chain(evolved)
        
        extract_chain(evolution_data['chain'])
        evolution_cache[pokemon_id] = evolution_chain
        return evolution_chain
    except (requests.exceptions.RequestException, KeyError, ValueError) as e:
        print(f"Error getting evolution chain: {e}")
        return []

def is_fully_evolved(pokemon_id: int) -> bool:
    """Check if a Pokemon is fully evolved."""
    evolution_chain = get_evolution_chain(pokemon_id)
    if not evolution_chain:
        return True
    return pokemon_id == evolution_chain[-1]

def is_legendary(pokemon_id: int) -> bool:
    """Check if a Pokemon is legendary or mythical."""
    species_data = get_pokemon_species_data(pokemon_id)
    if not species_data:
        return False
    return species_data.get('is_legendary', False) or species_data.get('is_mythical', False)

def get_all_pokemon() -> List[str]:
    """Get a list of all Pokemon names."""
    try:
        response = requests.get("https://pokeapi.co/api/v2/pokemon?limit=1025")
        response.raise_for_status()
        data = response.json()
        return [p['name'].capitalize() for p in data['results']]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Pokemon list: {e}")
        return []

def get_random_pokemon(selected_generations: List[int], 
                      existing_types: Set[str] = None,
                      evolution_filter: bool = False,
                      exclude_legendary: bool = False) -> Optional[Dict]:
    """Get a random Pokemon that meets the filter criteria."""
    # Define generation ranges
    gen_ranges = {
        1: (1, 151),
        2: (152, 251),
        3: (252, 386),
        4: (387, 493),
        5: (494, 649),
        6: (650, 721),
        7: (722, 809),
        8: (810, 905),
        9: (906, 1025)
    }
    
    # Get all valid Pokemon IDs based on selected generations
    valid_ids = []
    for gen in selected_generations:
        start, end = gen_ranges[gen]
        valid_ids.extend(range(start, end + 1))
    
    if not valid_ids:
        return None
    
    # Shuffle the valid IDs
    random.shuffle(valid_ids)
    
    # Try Pokemon until we find one that meets all criteria
    for pokemon_id in valid_ids:
        pokemon_data = get_pokemon_data(pokemon_id)
        if not pokemon_data:
            continue
        
        # Check evolution filter
        if evolution_filter and not is_fully_evolved(pokemon_id):
            continue
        
        # Check legendary filter
        if exclude_legendary and is_legendary(pokemon_id):
            continue
        
        # Check type filter
        if existing_types is not None:
            pokemon_types = {t['type']['name'] for t in pokemon_data['types']}
            if pokemon_types & existing_types:
                continue
        
        return pokemon_data
    
    return None

class LoadingIndicator(tk.Canvas):
    def __init__(self, master, size=30, **kwargs):
        super().__init__(master, width=size*2, height=size, **kwargs)
        self.size = size
        self.angle = 0
        self.is_running = False
        
        # Pokeball colors with Dracula theme
        self.red = DraculaTheme.RED
        self.white = DraculaTheme.FOREGROUND
        self.black = DraculaTheme.BACKGROUND
        
        self.configure(bg=DraculaTheme.BACKGROUND)
        self.draw_pokeball()
    
    def draw_pokeball(self):
        self.delete("all")  # Clear canvas
        
        # Calculate center and radius
        cx = self.size
        cy = self.size/2
        r = self.size/2 - 2
        
        # Draw rotating arc (animation effect)
        start_angle = self.angle
        extent = 30
        self.create_arc(cx-r, cy-r, cx+r, cy+r, 
                       start=start_angle, extent=extent,
                       fill=self.red, width=0)
        
        # Draw Pokeball outline
        self.create_oval(cx-r, cy-r, cx+r, cy+r, 
                        outline=self.black, width=2)
        
        # Draw middle line
        line_y = cy
        self.create_line(cx-r, line_y, cx+r, line_y, 
                        fill=self.black, width=2)
        
        # Draw center button
        button_r = r/4
        self.create_oval(cx-button_r, cy-button_r, cx+button_r, cy+button_r, 
                        fill=self.white, outline=self.black, width=2)
    
    def start(self):
        self.is_running = True
        self.animate()
    
    def stop(self):
        self.is_running = False
    
    def animate(self):
        if not self.is_running:
            return
        
        self.angle = (self.angle + 10) % 360
        self.draw_pokeball()
        self.after(50, self.animate)  # Update every 50ms

class LoadingFrame(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg=DraculaTheme.BACKGROUND, **kwargs)
        
        # Create and pack loading indicator
        self.indicator = LoadingIndicator(self)
        self.indicator.pack(side=tk.LEFT, padx=5)
        
        # Create and pack loading text
        self.text = tk.Label(self,
                           text="Lade Pokemon...",
                           font=('Arial', 12),
                           bg=DraculaTheme.BACKGROUND,
                           fg=DraculaTheme.CYAN)
        self.text.pack(side=tk.LEFT, padx=5)
    
    def start(self):
        self.indicator.start()
    
    def stop(self):
        self.indicator.stop()
        self.destroy()

def show_pokemon():
    """Display the selected Pokemon team."""
    # Show loading indicator
    loading_frame = LoadingFrame(pokemon_frame)
    loading_frame.pack(pady=20)
    loading_frame.start()
    window.update()
    
    # Clear previous Pokemon display
    for widget in pokemon_frame.winfo_children():
        if widget != loading_frame:
            widget.destroy()
    
    # Get selected generations
    selected_generations = generation_selector.get_selected_generations()
    if not selected_generations:
        loading_frame.stop()
        messagebox.showwarning("Warnung", "Bitte wähle mindestens eine Generation aus!")
        return
    
    def generate_pokemon_team():
        """Generate Pokemon team in background thread."""
        # Prefetch Pokemon data for selected generations
        gen_ranges = {
            1: (1, 151),
            2: (152, 251),
            3: (252, 386),
            4: (387, 493),
            5: (494, 649),
            6: (650, 721),
            7: (722, 809),
            8: (810, 905),
            9: (906, 1025)
        }
        
        pokemon_ids = []
        for gen in selected_generations:
            start, end = gen_ranges[gen]
            pokemon_ids.extend(range(start, end + 1))
        
        # Prefetch data in background
        prefetch_pokemon_data(pokemon_ids)
        prefetch_species_data(pokemon_ids)
        
        # Get manually selected Pokemon
        selected_pokemon = []
        selected_types = set()
        
        for selector in pokemon_selectors:
            pokemon_name = selector.get()
            if pokemon_name:
                try:
                    pokemon_id = get_all_pokemon().index(pokemon_name) + 1
                    pokemon_data = get_pokemon_data(pokemon_id)
                    if pokemon_data:
                        # Check legendary filter for manually selected Pokemon
                        if legendary_filter_var.get() and is_legendary(pokemon_id):
                            window.after(0, lambda: messagebox.showwarning(
                                "Warnung",
                                f"Das Pokemon {pokemon_name} ist legendär/mystisch und wird bei aktiviertem Legendär-Filter übersprungen!"
                            ))
                            continue
                        selected_pokemon.append(pokemon_data)
                        if type_filter_var.get():
                            selected_types.update(t['type']['name'] for t in pokemon_data['types'])
                except ValueError:
                    continue
        
        # Fill remaining slots with random Pokemon
        while len(selected_pokemon) < 6:
            pokemon_data = get_random_pokemon(
                selected_generations,
                selected_types if type_filter_var.get() else None,
                evolution_filter_var.get(),
                legendary_filter_var.get()
            )
            
            if not pokemon_data:
                window.after(0, lambda: messagebox.showwarning(
                    "Warnung",
                    "Es konnten keine weiteren Pokemon gefunden werden, die den Filterkriterien entsprechen!"
                ))
                break
            
            selected_pokemon.append(pokemon_data)
            if type_filter_var.get():
                selected_types.update(t['type']['name'] for t in pokemon_data['types'])
        
        # Update UI in main thread
        def update_ui():
            nonlocal loading_frame
            
            # Create frame for each row (3 Pokemon per row)
            for row in range(2):
                row_frame = tk.Frame(pokemon_frame, bg=DraculaTheme.BACKGROUND)
                row_frame.pack(pady=10)
                
                for col in range(3):
                    idx = row * 3 + col
                    if idx >= len(selected_pokemon):
                        break
                    
                    pokemon_data = selected_pokemon[idx]
                    
                    # Create frame for this Pokemon
                    pokemon_display = tk.Frame(row_frame, 
                                            bg=DraculaTheme.CURRENT_LINE,
                                            padx=10, pady=10,
                                            relief=tk.RAISED,
                                            borderwidth=1)
                    pokemon_display.pack(side=tk.LEFT, padx=10)
                    
                    # Determine if Pokemon should be shiny (10% chance)
                    is_shiny = random.random() < 0.1
                    
                    # Get sprite URL
                    sprite_url = (pokemon_data['sprites']['front_shiny'] if is_shiny and pokemon_data['sprites']['front_shiny']
                                else pokemon_data['sprites']['front_default'])
                    
                    # Load sprite
                    photo = load_sprite(sprite_url)
                    if photo:
                        image_label = tk.Label(pokemon_display,
                                             image=photo,
                                             bg=DraculaTheme.CURRENT_LINE)
                        image_label.image = photo
                        image_label.pack()
                    
                    try:
                        # Get German name
                        species_data = get_pokemon_species_data(pokemon_data['id'])
                        german_name = next((name['name'] for name in species_data['names'] 
                                        if name['language']['name'] == 'de'), 
                                        pokemon_data['name'].capitalize())
                        
                        # Create text with Pokemon info
                        name_text = f"{german_name} {'✨' if is_shiny else ''}"
                        number_text = f"#{pokemon_data['id']}"
                        type_text = f"Typ: {' / '.join(t['type']['name'].capitalize() for t in pokemon_data['types'])}"
                        size_text = f"Größe: {pokemon_data['height']/10:.1f}m"
                        weight_text = f"Gewicht: {pokemon_data['weight']/10:.1f}kg"
                        
                        # Create and pack info labels with different colors
                        name_label = tk.Label(pokemon_display,
                                           text=name_text,
                                           font=('Arial', 12, 'bold'),
                                           bg=DraculaTheme.CURRENT_LINE,
                                           fg=DraculaTheme.GREEN if is_shiny else DraculaTheme.PINK)
                        name_label.pack()
                        
                        number_label = tk.Label(pokemon_display,
                                             text=number_text,
                                             font=('Arial', 10),
                                             bg=DraculaTheme.CURRENT_LINE,
                                             fg=DraculaTheme.COMMENT)
                        number_label.pack()
                        
                        type_label = tk.Label(pokemon_display,
                                           text=type_text,
                                           font=('Arial', 10),
                                           bg=DraculaTheme.CURRENT_LINE,
                                           fg=DraculaTheme.ORANGE)
                        type_label.pack()
                        
                        size_label = tk.Label(pokemon_display,
                                           text=size_text,
                                           font=('Arial', 10),
                                           bg=DraculaTheme.CURRENT_LINE,
                                           fg=DraculaTheme.CYAN)
                        size_label.pack()
                        
                        weight_label = tk.Label(pokemon_display,
                                             text=weight_text,
                                             font=('Arial', 10),
                                             bg=DraculaTheme.CURRENT_LINE,
                                             fg=DraculaTheme.CYAN)
                        weight_label.pack()
                        
                    except Exception as e:
                        print(f"Error displaying Pokemon: {e}")
                        error_label = tk.Label(pokemon_display, 
                                             text=f"Error displaying\n{pokemon_data['name']}", 
                                             font=('Arial', 10),
                                             bg=DraculaTheme.CURRENT_LINE,
                                             fg=DraculaTheme.RED)
                        error_label.pack()
            
            # Stop and remove loading indicator
            loading_frame.stop()
            
            # Save cache after successful operation
            save_cache()
        
        # Schedule UI update in main thread
        window.after(0, update_ui)
    
    # Start generation in background thread
    thread = threading.Thread(target=generate_pokemon_team)
    thread.daemon = True
    thread.start()

def main():
    global pokemon_frame, pokemon_selectors, generation_selector, type_filter_var, evolution_filter_var, legendary_filter_var, window
    
    # Load cached data
    load_cache()
    
    window = tk.Tk()
    window.title("Pokémon Team Generator")
    
    # Configure Dracula theme styles
    style = ttk.Style()
    style.configure("Dracula.TCheckbutton",
                   background=DraculaTheme.BACKGROUND,
                   foreground=DraculaTheme.FOREGROUND)
    style.configure("Dracula.TCombobox",
                   background=DraculaTheme.BACKGROUND,
                   foreground=DraculaTheme.FOREGROUND,
                   fieldbackground=DraculaTheme.CURRENT_LINE,
                   selectbackground=DraculaTheme.SELECTION)
    
    # Set window size and position
    window_width = 1000
    window_height = 1350
    window.geometry(f"{window_width}x{window_height}")
    window.minsize(800, 700)
    
    # Configure window colors
    window.configure(bg=DraculaTheme.BACKGROUND)
    
    # Center window
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    # Create main container
    main_container = tk.Frame(window, padx=20, pady=20, bg=DraculaTheme.BACKGROUND)
    main_container.pack(fill=tk.BOTH, expand=True)
    
    # Create title
    title_label = tk.Label(main_container, 
                          text="Pokémon Team Generator",
                          font=('Arial', 24, 'bold'),
                          bg=DraculaTheme.BACKGROUND,
                          fg=DraculaTheme.PURPLE)
    title_label.pack(pady=(0, 20))
    
    # Create generation selector
    generation_selector = GenerationSelector(main_container)
    generation_selector.pack(fill=tk.X, pady=(0, 20))
    
    # Create filter frame
    filter_frame = tk.Frame(main_container, bg=DraculaTheme.BACKGROUND)
    filter_frame.pack(fill=tk.X, pady=(0, 20))
    
    # Create filter section title
    filter_title = tk.Label(filter_frame,
                           text="Filter Optionen",
                           font=('Arial', 14, 'bold'),
                           bg=DraculaTheme.BACKGROUND,
                           fg=DraculaTheme.CYAN)
    filter_title.pack(anchor='w', pady=(0, 10))
    
    # Create type filter checkbox
    type_filter_var = tk.BooleanVar(value=False)
    type_filter = tk.Checkbutton(filter_frame, 
                                text="Typ-Filter: Jeder Typ soll nur einmal vorkommen", 
                                variable=type_filter_var,
                                font=('Arial', 10),
                                bg=DraculaTheme.BACKGROUND,
                                fg=DraculaTheme.FOREGROUND,
                                selectcolor=DraculaTheme.CURRENT_LINE,
                                activebackground=DraculaTheme.BACKGROUND,
                                activeforeground=DraculaTheme.GREEN)
    type_filter.pack(anchor='w')
    
    # Create evolution filter checkbox
    evolution_filter_var = tk.BooleanVar(value=False)
    evolution_filter = tk.Checkbutton(filter_frame, 
                                    text="Entwicklungs-Filter: Nur voll entwickelte Pokemon oder Pokemon ohne Entwicklung", 
                                    variable=evolution_filter_var,
                                    font=('Arial', 10),
                                    bg=DraculaTheme.BACKGROUND,
                                    fg=DraculaTheme.FOREGROUND,
                                    selectcolor=DraculaTheme.CURRENT_LINE,
                                    activebackground=DraculaTheme.BACKGROUND,
                                    activeforeground=DraculaTheme.GREEN)
    evolution_filter.pack(anchor='w')

    # Create legendary filter checkbox
    legendary_filter_var = tk.BooleanVar(value=False)
    legendary_filter = tk.Checkbutton(filter_frame,
                                    text="Legendär-Filter: Keine legendären oder mystischen Pokemon",
                                    variable=legendary_filter_var,
                                    font=('Arial', 10),
                                    bg=DraculaTheme.BACKGROUND,
                                    fg=DraculaTheme.FOREGROUND,
                                    selectcolor=DraculaTheme.CURRENT_LINE,
                                    activebackground=DraculaTheme.BACKGROUND,
                                    activeforeground=DraculaTheme.GREEN)
    legendary_filter.pack(anchor='w')

    # Create selector container
    selector_container = tk.Frame(main_container, bg=DraculaTheme.BACKGROUND)
    selector_container.pack(fill=tk.X, pady=(0, 20))
    
    # Add label above selectors
    selector_title = tk.Label(selector_container,
                            text="Manuelle Pokémon-Auswahl",
                            font=('Arial', 14, 'bold'),
                            bg=DraculaTheme.BACKGROUND,
                            fg=DraculaTheme.PINK)
    selector_title.pack(pady=(0, 10))
    
    selector_subtitle = tk.Label(selector_container, 
                               text="Wähle deine Pokemon (leere Plätze werden zufällig aufgefüllt):", 
                               font=('Arial', 10),
                               bg=DraculaTheme.BACKGROUND,
                               fg=DraculaTheme.FOREGROUND)
    selector_subtitle.pack(pady=(0, 10))
    
    # Create container for selectors
    dropdown_container = tk.Frame(selector_container, bg=DraculaTheme.BACKGROUND)
    dropdown_container.pack()
    
    # Get Pokemon list for dropdowns
    pokemon_list = get_all_pokemon()
    
    # Create 6 Pokemon selectors
    pokemon_selectors = []
    for i in range(6):
        selector = PokemonSelector(dropdown_container, pokemon_list)
        selector.pack(side=tk.LEFT, padx=2)
        pokemon_selectors.append(selector)

    # Create frame for Pokemon display
    global pokemon_frame
    pokemon_frame = tk.Frame(main_container, bg=DraculaTheme.BACKGROUND)
    pokemon_frame.pack(fill=tk.BOTH, expand=True)

    # Create generate button
    generate_button = tk.Button(main_container, 
                              text="Generiere Pokémon Team", 
                              command=show_pokemon,
                              padx=20, pady=10,
                              font=('Arial', 12, 'bold'),
                              bg=DraculaTheme.PURPLE,
                              fg=DraculaTheme.FOREGROUND,
                              activebackground=DraculaTheme.SELECTION,
                              activeforeground=DraculaTheme.FOREGROUND,
                              relief=tk.FLAT)
    generate_button.pack(pady=(0, 20))

    window.mainloop()

if __name__ == "__main__":
    main()
