import numpy as np
import pandas as pd
from biosppy.signals import ecg
import time

fs = 500 # Fréquence d'échantillonnage

# Chargement des métadonnées
print("📂 Chargement du fichier meta...")
df_meta = pd.read_pickle("df_meta.pkl")
print("✅ Fichier meta chargé avec succès !")

def is_rythm_regular(rpeaks, threshold=100, log=False):
    gap = np.diff(rpeaks)
    std_deviation = np.std(gap)
    if log:
        print(f"📊 Écart-type des intervalles RR : {std_deviation:.2f}")
    return std_deviation <= threshold

def analyse_heart_rate(rpeaks, brad_threshold=60, tachy_threshold=100, log=False):
    heart_rate = 60 * fs / np.diff(rpeaks)
    mean_hr = np.mean(heart_rate)
    if log:
        print(f"💓 Fréquence cardiaque moyenne : {mean_hr:.2f} bpm")
    if mean_hr > tachy_threshold:
        return 1
    elif mean_hr < brad_threshold:
        return -1
    else:
        return 0
    
def heart_rate_diagnosis(heart_rate_analysis):
    if heart_rate_analysis == 1:
        return "Tachycardie"
    elif heart_rate_analysis == -1:
        return "Bradycardie"
    else:
        return "Rythme cardiaque normal"
    
def is_normal_p_wave_present(rpeaks, P_pos, threshold=10, log=False):
    diff = rpeaks - P_pos["P_positions"]
    std_deviation = np.std(diff)
    if log:
        print(f"📊 Écart-type des intervalles PR : {std_deviation:.2f}")

    return std_deviation <= threshold

def analyse_ecg(ecg_id, log=True):
    """
    Analyse un ECG à partir de son ID.
    Renvoie un couple. Le premier élément est 0 si l'ECV est normal, et un autre code en cas de pathologie.
    Le deuxième élément est le diagnostic associé.
    """

    # Lecture des données ECG
    start_time = time.time()

    ecg_file_path = df_meta.iloc[ecg_id].ecg_file_path
    if log: 
        print(f"📖 Lecture des données à partir de : {ecg_file_path}")
    ecg_data = pd.read_csv(ecg_file_path)

    # Extraction des données (~ 0.03s par dérivation)
    try:
        II = ecg.ecg(signal=ecg_data[" II"].values, sampling_rate=500, show=False)
        V1 = ecg.ecg(signal=ecg_data[" V1"].values, sampling_rate=500, show=False)
        V4 = ecg.ecg(signal=ecg_data[" V4"].values, sampling_rate=500, show=False)
    except Exception as e:
        return -2, "Erreur lors de la lecture de l'ECG"


    rpeaks = II["rpeaks"]

    if log:
        print(f"\n✨ Rpeaks détectés : {np.array2string(rpeaks)}")

    Q_pos = ecg.getQPositions(ecg_proc=II, show=False)
    S_pos = ecg.getSPositions(ecg_proc=V1, show=False)
    P_pos = ecg.getPPositions(ecg_proc=II, show=False)
    T_pos = ecg.getTPositions(ecg_proc=V4, show=False)

    if log:
        print(f"🔵 Q pos détectées : {np.array2string(np.array(Q_pos['Q_positions']))}")
        print(f"🔴 S pos détectées : {np.array2string(np.array(S_pos['S_positions']))}")
        print(f"🟢 P pos détectées : {np.array2string(np.array(P_pos['P_positions']))}")
        print(f"🟣 T pos détectées : {np.array2string(np.array(T_pos['T_positions']))}")

    elapsed_time = time.time() - start_time

    if log:
        print(f"\n⏱️ Chargement ECG #{ecg_id} terminé en {elapsed_time:.2f} secondes.")

    # Classification
    
    regular_rythm = is_rythm_regular(rpeaks)

    if regular_rythm:
        print(f"🔄 Rythme régulier pour ECG #{ecg_id}.")
        diagnosis = analyse_heart_rate(rpeaks, log=True)
        
        if diagnosis != 0:
            return diagnosis, heart_rate_diagnosis(diagnosis)
        
        # COMPLETER ICI

    else:
        print(f"🔴 Rythme irrégulier pour ECG #{ecg_id}.")

        # COMPLETER ICI AUSSI

        # is_normal_p_wave_present(rpeaks, P_pos)


# Appel de la fonction d'analyse
analyse_ecg(0)
analyse_ecg(1)
