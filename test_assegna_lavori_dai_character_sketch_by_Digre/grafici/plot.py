import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

file_path = 'test_assegna_lavori_dai_character_sketch_by_Digre\grafici\job_divergence_baseline.csv' 

try:
    df = pd.read_csv(file_path)
except FileNotFoundError:
    print(f"Errore: Il file '{file_path}' non trovato.")
    sys.exit()

dialetti = ['SIC', 'PAR', 'NAP']
for d in dialetti:
    df[f'{d}_div'] = df[d] - df['ITA']


df['abs_sum'] = df[[f'{d}_div' for d in dialetti]].abs().sum(axis=1)
df_filtered = df[df['abs_sum'] > 10].copy().sort_values('abs_sum', ascending=True)

df_filtered['LABELS_WITH_BASE'] = df_filtered.apply(
    lambda x: f"{x['LAVORO']} [ITA: {x['ITA']}]", axis=1
)

# 4. Plotting
fig, ax = plt.subplots(figsize=(13, 14))
ind = np.arange(len(df_filtered))
width = 0.25

ax.barh(ind + width, df_filtered['SIC_div'], width, label='SIC vs ITA', color='#3498db')
ax.barh(ind, df_filtered['PAR_div'], width, label='PAR vs ITA', color='#e67e22')
ax.barh(ind - width, df_filtered['NAP_div'], width, label='NAP vs ITA', color='#2ecc71')

# 5. Estetica
ax.axvline(0, color='black', linewidth=1.5)
ax.set_yticks(ind)
ax.set_yticklabels(df_filtered['LABELS_WITH_BASE'], fontsize=10) # Qui usiamo le nuove etichette

ax.set_xlabel('Divergenza (Differenza rispetto a ITA)', fontsize=12)
ax.set_title('Divergenze Occupazionali\nI valori tra parentesi quadre [ ] indicano la base ITA', fontsize=15, pad=20)

# Aggiungiamo una griglia leggera per seguire meglio le barre
ax.grid(axis='x', linestyle=':', alpha=0.6)
ax.legend(title="Dialetto vs Base", loc='lower right')

plt.tight_layout()
plt.savefig('divergence_baseline_values.png', dpi=300)
plt.show()