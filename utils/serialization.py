# utils/serialization.py
import pickle
import sys
from engine import Engine

def save_game(engine: Engine, filename: str):
    """
    Sauvegarde l'état complet du moteur de jeu dans un fichier binaire (.sav).
    Utilise pickle (Req 12).
    """
    print(f"Sauvegarde de la partie dans '{filename}'...")
    try:
        # 'wb' signifie Write Binary (indispensable pour pickle)
        with open(filename, 'wb') as f:
            pickle.dump(engine, f)
        print("Sauvegarde réussie !")
    except IOError as e:
        print(f"Erreur lors de la sauvegarde : {e}", file=sys.stderr)

def load_game(filename: str) -> Engine:
    """
    Charge un moteur de jeu complet depuis un fichier binaire (.sav).
    """
    print(f"Chargement de la partie depuis '{filename}'...")
    try:
        # 'rb' signifie Read Binary
        with open(filename, 'rb') as f:
            engine = pickle.load(f)
        
        print(f"Chargement réussi ! Tour actuel : {engine.turn_count}")
        return engine
    except FileNotFoundError:
        print(f"Erreur : Fichier de sauvegarde '{filename}' introuvable.", file=sys.stderr)
        sys.exit(1)
    except (pickle.UnpicklingError, EOFError) as e:
        print(f"Erreur : Le fichier '{filename}' est corrompu ou invalide.", file=sys.stderr)
        sys.exit(1)