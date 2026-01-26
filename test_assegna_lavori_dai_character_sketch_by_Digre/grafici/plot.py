import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

file_path = 'job_divergence_multiagent.csv' 

try:
    df = pd.read_csv(file_path)
except FileNotFoundError:
    print(f"Errore: Il file '{file_path}' non trovato.")
    sys.exit()

dialetti = ['SIC', 'PAR', 'NAP']
colori = {'SIC': '#3498db', 'PAR': '#e67e22', 'NAP': '#2ecc71'}

for d in dialetti:
    df[f'{d}_div'] = df[d] - df['ITA']

df['abs_sum'] = df[[f'{d}_div' for d in dialetti]].abs().sum(axis=1)
df_filtered = df[df['abs_sum'] > 10].copy().sort_values('ITA', ascending=True)


fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(18, 12), sharey=True)
y_pos = np.arange(len(df_filtered))

for i, d in enumerate(dialetti):
    ax = axes[i]
    

    ax.hlines(y=y_pos, xmin=df_filtered['ITA'], xmax=df_filtered[d], 
              color='grey', alpha=0.4, linewidth=2, zorder=1)
    

    ax.scatter(df_filtered['ITA'], y_pos, color='#95a5a6', s=120, 
               label='ITA' if i == 0 else "", zorder=2, edgecolors='white')
    

    ax.scatter(df_filtered[d], y_pos, color=colori[d], s=120, 
               label=d, zorder=3, edgecolors='white')
    
    for y, ita, dial in zip(y_pos, df_filtered['ITA'], df_filtered[d]):
        ax.annotate('', xy=(dial, y), xytext=(ita, y),
                    arrowprops=dict(arrowstyle='->', color=colori[d], lw=1, alpha=0.6))


    ax.set_title(f'ITA vs {d}', fontweight='bold', fontsize=14, pad=15)
    ax.set_xlabel('Score')
    ax.grid(axis='x', linestyle='--', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

axes[0].set_yticks(y_pos)
axes[0].set_yticklabels(df_filtered['LAVORO'], fontweight='bold')

plt.suptitle('Analisi Divergenze Occupazionali: Dialetti vs Italiano Centrale', 
             fontsize=20, y=1.05, fontweight='bold')

fig.legend(loc='upper center', bbox_to_anchor=(0.5, 1.01), ncol=4, frameon=False, fontsize=12)

plt.tight_layout()
plt.savefig('divergence_multiagent_values_dumbbell.png', dpi=300, bbox_inches='tight')
plt.show()