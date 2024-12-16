import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df_meta = pd.read_pickle("df_meta.pkl")

def compute_fft(signal, sampling_rate=500):
    """
    Calcule la transformée de Fourier d'un signal.

    Args:
        signal (pd.Series): Le signal à analyser.
        sampling_rate (int): Fréquence d'échantillonnage du signal (en Hz).

    Returns:
        tuple: (frequences, amplitudes)
    """
    fft_values = np.fft.fft(signal)
    fft_freqs = np.fft.fftfreq(len(signal), d=1/sampling_rate)  # Corrige les fréquences
    return fft_freqs[:len(fft_freqs)//2], np.abs(fft_values)[:len(fft_values)//2]

def plot_ecg(n: int):
    """
    Affiche les subplots pour les dérivations ECG I, II, et III à partir de l'entrée n du dataframe df_meta.
    """
    # Chargement des données ECG pour la ligne n
    ecg = pd.read_csv(df_meta.iloc[n].ecg_file_path)

    # Création des subplots pour les signaux temporels
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

    # Liste des dérivations et couleurs
    derivations = ["I", " II", " III"]
    colors = ["blue", "green", "red"]

    for i, (derivation, color) in enumerate(zip(derivations, colors)):
        signal = ecg[derivation]
        axes[i].plot(signal, color=color)
        axes[i].set_title(f"Dérivation {derivation.strip()}")
        axes[i].set_ylabel("Amplitude")

    # Label commun pour l'axe x
    axes[-1].set_xlabel("Temps")

    # Ajuster les espaces entre les subplots
    plt.tight_layout()

    # Affichage
    plt.show()

def plot_fft(n: int):
    """
    Affiche les transformées de Fourier pour les dérivations ECG I, II, et III à partir de l'entrée n du dataframe df_meta.
    """
    # Chargement des données ECG pour la ligne n
    ecg = pd.read_csv(df_meta.iloc[n].ecg_file_path)

    # Création des subplots pour les FFT
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

    # Liste des dérivations et couleurs
    derivations = ["I", " II", " III"]
    colors = ["blue", "green", "red"]

    for i, (derivation, color) in enumerate(zip(derivations, colors)):
        signal = ecg[derivation]
        freqs, amplitudes = compute_fft(signal)
        axes[i].plot(freqs, amplitudes, color=color)
        axes[i].set_title(f"Transformée de Fourier {derivation.strip()}")
        axes[i].set_ylabel("Amplitude")

    # Label commun pour l'axe x
    axes[-1].set_xlabel("Fréquence")

    # Ajuster les espaces entre les subplots
    plt.tight_layout()

    # Affichage
    plt.show()

# Exemple d'utilisation
#plot_ecg(69)
#plot_fft(69)
