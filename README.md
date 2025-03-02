# Pokémon Team Generator

Ein fortgeschrittener Pokémon Team Generator mit umfangreichen Filtermöglichkeiten, entwickelt in Python mit Tkinter.

## Features

### 1. Pokémon Auswahl
- Zufällige Generierung von bis zu 6 Pokémon
- Unterstützung aller 9 Generationen (Pokémon #1-1025)
- Manuelle Auswahl über Dropdown-Menüs
- Vermeidung von Duplikaten
- 10% Chance auf Shiny Pokémon (✨)

### 2. Filter Optionen

#### Generations-Filter
- Individuelle Auswahl der Generationen 1-9
- Mehrfachauswahl möglich
- Standardmäßig alle Generationen aktiviert

#### Typ-Filter
- Option zur Vermeidung doppelter Typen im Team
- Berücksichtigt beide Typen eines Pokémon
- Wird auch bei manueller Auswahl beachtet

#### Entwicklungs-Filter
- Zeigt nur voll entwickelte oder nicht entwickelbare Pokémon
- Prüft die komplette Entwicklungskette
- Warnung bei manueller Auswahl nicht entwickelter Pokémon

#### Legendär-Filter
- Schließt legendäre und mystische Pokémon aus
- Basiert auf offiziellen PokeAPI-Daten
- Warnung bei manueller Auswahl legendärer Pokémon

### 3. Benutzeroberfläche
- Moderne, benutzerfreundliche GUI
- Responsive Design (1000x1350 Pixel)
- Automatische Zentrierung auf dem Bildschirm
- Animierter Pokeball-Ladeindikator
- Detaillierte Pokémon-Informationen:
  - Name (Deutsch)
  - Pokédex-Nummer
  - Typen
  - Größe (in Metern)
  - Gewicht (in Kilogramm)
  - Shiny-Status

### 4. Performance Optimierungen
- Lokales Caching von:
  - Pokémon-Daten
  - Spezies-Informationen
  - Sprites (Bilder)
- Parallele API-Aufrufe
- Hintergrund-Prefetching
- Thread-basierte UI-Updates

## Technische Details

### Abhängigkeiten
```python
tkinter      # GUI-Framework
requests     # API-Aufrufe
Pillow       # Bildverarbeitung
```

### Wichtige Klassen

#### LoadingIndicator
```python
class LoadingIndicator(tk.Canvas):
    """
    Animierter Pokeball-Ladeindikator
    - Größe anpassbar
    - Authentische Pokémon-Farben
    - Flüssige 360°-Rotation
    """
```

#### GenerationSelector
```python
class GenerationSelector(tk.Frame):
    """
    Generations-Auswahlfeld
    - Checkbox für jede Generation
    - Mehrfachauswahl möglich
    - Automatische Layout-Anpassung
    """
```

#### PokemonSelector
```python
class PokemonSelector(ttk.Combobox):
    """
    Dropdown-Menü für manuelle Pokémon-Auswahl
    - Alle verfügbaren Pokémon
    - Alphabetische Sortierung
    - Leere Auswahl möglich
    """
```

### Wichtige Funktionen

#### get_pokemon_data
```python
def get_pokemon_data(pokemon_id: int) -> Dict:
    """
    Lädt Basis-Pokémon-Daten
    - Cached Ergebnisse
    - Fehlerbehandlung
    - Thread-sicher
    """
```

#### get_pokemon_species_data
```python
def get_pokemon_species_data(pokemon_id: int) -> Dict:
    """
    Lädt erweiterte Pokémon-Informationen
    - Deutsche Namen
    - Legendär-Status
    - Entwicklungsketten
    """
```

#### get_random_pokemon
```python
def get_random_pokemon(
    selected_generations: List[int],
    existing_types: Set[str] = None,
    evolution_filter: bool = False,
    exclude_legendary: bool = False
) -> Optional[Dict]:
    """
    Hauptfunktion für Pokémon-Generierung
    - Berücksichtigt alle Filter
    - Zufällige Auswahl
    - Cached Zugriffe
    """
```

## Cache-System

### Struktur
```
cache/
├── pokemon_data.json    # Basis-Pokémon-Daten
├── species_data.json    # Spezies-Informationen
└── sprites/            # Pokémon-Bilder
    ├── normal/
    └── shiny/
```

### Features
- Persistentes Caching
- Automatische Cache-Verwaltung
- Threadsichere Zugriffe
- Automatische Wiederherstellung

## API-Nutzung

Das Programm verwendet die [PokeAPI](https://pokeapi.co/):
- RESTful API
- Umfangreiche Pokémon-Daten
- Kostenlos und ohne API-Key
- Rate-Limiting beachtet

## Threading-Modell

### Hauptthread
- UI-Rendering
- Event-Handling
- Animation

### Arbeitsthreads
- API-Aufrufe
- Daten-Verarbeitung
- Cache-Management

## Fehlerbehandlung
- Informative Warnmeldungen
- Graceful Degradation
- Automatische Wiederherstellung
- Logging wichtiger Ereignisse

## Installation

1. Python 3.13.2 oder höher installieren
2. Repository klonen
3. Abhängigkeiten installieren:
```bash
pip install pillow requests
```
4. Programm starten:
```bash
python random_pokemon.py
```

## Lizenz
MIT License - Siehe LICENSE Datei
