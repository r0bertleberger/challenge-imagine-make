import numpy as np
import pandas as pd
from biosppy.signals import ecg
import time

fs = 500 # Fréquence d'échantillonnage

# Chargement des métadonnées
print("📂 Chargement du fichier meta...")
df_meta = pd.read_pickle("df_meta.pkl")
print("✅ Fichier meta chargé avec succès !")

def is_rythm_regular(rpeaks, threshold=55, log=False):
    gap = np.diff(rpeaks)
    std_deviation = np.std(gap)
    if log:
        print(f"📊 Écart-type des intervalles RR : {std_deviation:.2f}")
    return std_deviation <= threshold

def analyse_heart_rate(rpeaks, brad_threshold=59.4, tachy_threshold=100, log=False):
    heart_rate = 60 * fs / np.diff(rpeaks)
    mean_hr = np.mean(heart_rate)
    if log:
        print(f"💓 Fréquence cardiaque moyenne : {mean_hr:.2f} bpm")
    if mean_hr > tachy_threshold:
        return 1, "Tachycardie"
    elif mean_hr < brad_threshold:
        return -1, "Bradycardie"
    else:
        return 0, ""

def analyse_segment_pr(rpeaks, P_pos, distance_threshold=110, repetition_threshold=0.5):
    # On se base sur un signal de 9,5s avec 5000 échantillons soit un signal échantilloné à environ 526Hz
    segment_pr = rpeaks - P_pos["P_positions"]
    if(segment_pr > distance_threshold).mean() >= repetition_threshold: # On vérifie le caractère prolongé de l'anomalie
        return -2, "Bloc auriculo-ventriculaire I"
    return 0, ""

def analyse_complexe_qrs(Q_pos, S_pos, threshold=63):
    return -3, "Tachycardie ventriculaire" if (S_pos["S_positions"] - Q_pos["Q_positions"] > threshold).any() else 0, ""
    
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
    print("Diagnostic du chirurgien :" + str(df_meta.iloc[ecg_id].diagnosis))
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
    
    regular_rythm = is_rythm_regular(rpeaks, log=True)

    if regular_rythm:
        print(f"🔄 Rythme régulier pour ECG #{ecg_id}.")

        heart_rate_diagnosis, heart_rate_reason = analyse_heart_rate(rpeaks, log=True)

        if heart_rate_diagnosis == -1:
            return heart_rate_diagnosis, heart_rate_reason
        
        if heart_rate_diagnosis == 0 :
            segment_pr_diagnosis, segment_pr_reason = analyse_segment_pr(rpeaks, P_pos)

            if segment_pr_diagnosis == -2:
                return segment_pr_diagnosis, segment_pr_reason
            else: 
                return 0, "Rythme sinusal normal"
        
        if heart_rate_diagnosis == 1:
            qrs_diagnosis, qrs_reason = analyse_complexe_qrs(Q_pos, S_pos)

            if qrs_diagnosis == -3:
                return qrs_diagnosis, qrs_reason
            else:
                return heart_rate_diagnosis, heart_rate_reason
    
    else:
        print(f"🔴 Rythme irrégulier pour ECG #{ecg_id}.")

        # COMPLETER ICI AUSSI

        if is_normal_p_wave_present(rpeaks, P_pos):
            return -4, "Hypertrophie ou ischémie ou infarctus"
        else:
            return -5, "Fibrillation"


# Appel de la fonction d'analyse
# print(analyse_ecg(0))
# print(analyse_ecg(75))

for i in range(30):
    print("="*20)
    print(analyse_ecg(i, log=True))
