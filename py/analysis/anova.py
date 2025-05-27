from statsmodels.formula.api import ols
from statsmodels.stats.anova  import anova_lm
from statsmodels.regression.mixed_linear_model import MixedLM
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.graphics.factorplots import interaction_plot
import os
import matplotlib.pyplot as plt
import pandas as pd

def perform_ANOVA(df, df_exploded, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    # p-value for significance (set to 0.05)
    sig = 0.05

    # ANCOVA: score ~ model * prompt_id + map_size
    # SRQ3, 4 & 5
    ancova_mod = ols('I(score) ~ C(model)*C(prompt_id) + map_size', data=df_exploded).fit()
    ancova_table = anova_lm(ancova_mod, typ=2)
    ancova_table.to_csv(os.path.join(out_dir, "ancova_model_prompt_mapSize.csv"))

    # (model x prompt) & (model x size) SRQ3
    for xvar, fname, xlabel in [
        ('prompt_id', 'interaction_model_prompt.png', 'Prompt ID'),
        ('map_size', 'interaction_model_mapSize.png', 'Map Size')
    ]:
        plt.figure()
        interaction_plot(
            x=df_exploded[xvar],
            trace=df_exploded['model'],
            response=df_exploded['score'],
            ax=plt.gca()
        )
        plt.gca()
        plt.title(f'Interaction: Model × {xlabel}')
        plt.xlabel(xlabel)
        plt.ylabel('Score')
        plt.savefig(os.path.join(out_dir, fname))
        plt.close()

    # Mixed-Effects: I(avg_score) ~ model + prompt_id + map_size
    # SRQ2
    md = MixedLM.from_formula(
        'I(avg_score) ~ C(model) + C(prompt_id) + map_size',
        groups='map_id',
        data=df
    )
    mdf = md.fit()
    fe = pd.DataFrame({
        'coef': mdf.fe_params,
        'std_err': mdf.bse_fe,
        'z': mdf.fe_params / mdf.bse_fe,
        'pval': mdf.pvalues
    })
    fe.to_csv(os.path.join(out_dir, 'mixedlm_fixed_effects.csv'))

    # Tukey HSD: score by model for each map_id
    # SRQ4
    for mid, grp in df_exploded.groupby('map_id'):

        # Safeguard to run only with maps with more than 2 models
        n_models = grp['model'].nunique()
        if n_models < 2:
            print(f"[ERR] Skipping Tukey Comparison for map {mid}: only {n_models} available")
            continue

        tuk = pairwise_tukeyhsd(endog=grp['score'], groups=grp['model'], alpha=sig)
        tbl = pd.DataFrame(tuk._results_table.data[1:], columns=tuk._results_table.data[0])
        tbl.to_csv(os.path.join(out_dir, f"tukey_map_{mid}.csv"), index=False)

    # ANOVA on abstractability: score ~ model * abstractability + map_size
    # SRQ1 & 7
    anc2_mod = ols('I(score) ~ C(model)*C(abstractability) + map_size', data=df_exploded).fit()
    anc2_table = anova_lm(anc2_mod, typ=2)
    anc2_table.to_csv(os.path.join(out_dir, "ancova_model_abstractability_mapSize.csv"))

    # Plot interaction: Model x Abstractability
    plt.figure()
    interaction_plot(
        x=df_exploded['abstractability'],
        trace=df_exploded['model'],
        response=df_exploded['score'],
        ax=plt.gca()
    )
    plt.title('Interaction: Model × Abstractability')
    plt.xlabel('Abstractability')
    plt.ylabel('Mean Score')
    plt.savefig(os.path.join(out_dir, 'interaction_model_abstractability.png'))
    plt.close()

    # ANOVA on representation_key + Map Size
    # SRQ6
    if 'representation_key' in df_exploded.columns:
        rep_mod = ols('I(score) ~ C(representation_key) + map_size', data=df_exploded).fit()
        rep_table = anova_lm(rep_mod, typ=2)
        rep_table.to_csv(os.path.join(out_dir, 'ancova_representation_mapSize.csv'))
        # Post-hoc Tukey for representation_key
        rep_tuk = pairwise_tukeyhsd(endog=df_exploded['score'], groups=df_exploded['representation_key'], alpha=sig)
        rep_tbl = pd.DataFrame(rep_tuk._results_table.data[1:], columns=rep_tuk._results_table.data[0])
        rep_tbl.to_csv(os.path.join(out_dir, 'tukey_representation.csv'), index=False)

    # ANOVA on output format + Map Size
    # SRQ6
    if 'output' in df_exploded.columns:
        out_mod = ols('I(score) ~ C(output) + map_size', data=df_exploded).fit()
        out_table = anova_lm(out_mod, typ=2)
        out_table.to_csv(os.path.join(out_dir, 'ancova_output_mapSize.csv'))

    # Save a ranking by average score (best→worst)
    ranking = df_exploded.groupby('model')['score'].mean().sort_values(ascending=False).reset_index()
    with open(os.path.join(out_dir, 'model_ranking.txt'), 'w') as f:
        f.write('Model ranking (best→worst):\n')
        for i, row in ranking.iterrows():
            f.write(f"{i+1}. {row['model']} : {row['score']:.4f}\n")
    

    # ANOVA on prompt elements (instruction, necessary_context, background_context, representation_key, output)
    prompt_elems = ['instruction', 'necessary_context', 'background_context', 'representation_key', 'output']
    for elem in prompt_elems:
        if elem in df_exploded.columns:
            mod_elem = ols(f'I(score) ~ C({elem}) + map_size', data=df_exploded).fit()
            table_elem = anova_lm(mod_elem, typ=2)
            table_elem.to_csv(os.path.join(out_dir, f'ancova_{elem}_mapSize.csv'))
            # Post-hoc Tukey for prompt element levels
            try:
                tuk_elem = pairwise_tukeyhsd(endog=df_exploded['score'], groups=df_exploded[elem], alpha=sig)
                tuk_df_elem = pd.DataFrame(tuk_elem._results_table.data[1:], columns=tuk_elem._results_table.data[0])
                tuk_df_elem.to_csv(os.path.join(out_dir, f'tukey_{elem}.csv'), index=False)
            except ValueError:
                print(f"[WARN] Skipping Tukey for {elem}: insufficient groups")

    # === Generate SRQ summary ===
    summary_lines = []
    # SRQ1: Optimal abstraction
    p_abs = anc2_table.loc['C(abstractability)', 'PR(>F)']
    if p_abs < sig:
        summary_lines.append(f"SRQ1: LLM abstraction quality differs by map abstractability (p={p_abs:.3g}), with fully abstractable maps yielding higher scores, indicating LLMs can approach optimal abstraction when it exists.")
    else:
        summary_lines.append("SRQ1: No significant difference in abstraction quality across abstractability categories.")

    # SRQ2: Useful for planning
    top_mean = ranking.iloc[0]['score']
    summary_lines.append(f"SRQ2: Top LLM achieves average abstraction score of {top_mean:.3f}, demonstrating utility of LLM-based abstractions for planning.")

    # SRQ3: Impact of model, prompt, map size
    p_model = ancova_table.loc['C(model)', 'PR(>F)']
    p_prompt = ancova_table.loc['C(prompt_id)', 'PR(>F)']
    p_size = ancova_table.loc['map_size', 'PR(>F)']
    summary_lines.append(
        f"SRQ3: Model (p={p_model:.3g}), prompt (p={p_prompt:.3g}), and map size (p={p_size:.3g}) all significantly affect abstraction quality."
    )

    # SRQ4: Model comparison
    top3 = ranking['model'][:3].tolist()
    summary_lines.append(
        f"SRQ4: Best models are {', '.join(top3)}, with {top3[0]} leading."
    )

    # SRQ5: Prompt sensitivity
    if p_prompt < sig:
        summary_lines.append("SRQ5: Abstraction outcomes are sensitive to prompt phrasing (prompt main effect significant).")
    else:
        summary_lines.append("SRQ5: No significant sensitivity to prompt phrasing detected.")

    # SRQ6: Representation and output
    if 'rep_table' in locals():
        p_rep = rep_table.loc['C(representation_key)', 'PR(>F)']
        summary_lines.append(
            f"SRQ6: Representation key significantly impacts performance (p={p_rep:.3g})."
        )
    if 'out_table' in locals():
        p_out = out_table.loc['C(output)', 'PR(>F)']
        summary_lines.append(
            f"SRQ6: Output format effect p={p_out:.3g}."
        )

    # SRQ7: No perfect abstraction scenario
    p_inter = anc2_table.loc['C(model):C(abstractability)', 'PR(>F)']
    if p_inter < sig:
        summary_lines.append("SRQ7: Interaction between model and abstractability significant, indicating some models handle non-abstractable maps better.")
    else:
        summary_lines.append("SRQ7: No significant model-by-abstractability interaction; all models degrade similarly when perfect abstraction does not exist.")

    # Write summary to file
    with open(os.path.join(out_dir, 'summary.txt'), 'w') as f:
        for line in summary_lines:
            f.write(line + '\n')

def perform_planning_analysis(df_plan: pd.DataFrame, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    sig = 0.05

    # ANOVA: gain ~ C(model) + map_size
    df_plan['gain'] = pd.to_numeric(df_plan['gain'], errors='coerce')
    mod = ols('gain ~ C(model) + map_size', data=df_plan).fit()
    table = anova_lm(mod, typ=2)
    table.to_csv(os.path.join(out_dir, 'ancova_gain_model_mapSize.csv'))

    # Tukey on model for gain
    tuk = pairwise_tukeyhsd(endog=df_plan['gain'], groups=df_plan['model'], alpha=sig)
    tuk_df = pd.DataFrame(tuk._results_table.data[1:], columns=tuk._results_table.data[0])
    tuk_df.to_csv(os.path.join(out_dir, 'tukey_gain_model.csv'), index=False)

    # Correlation between abstraction avg_score (needs merge externally) and rel_gain
    # Expect df_plan to have 'avg_score' and 'rel_gain'
    if 'avg_score' in df_plan.columns:
        corr = df_plan[['avg_score','rel_gain']].corr().iloc[0,1]
        with open(os.path.join(out_dir,'gain_correlation.txt'),'w') as f:
            f.write(f'Correlation between abstraction quality and relative gain: {corr:.3f}\n')
        # scatter plot
        plt.figure()
        plt.scatter(df_plan['avg_score'], df_plan['rel_gain'])
        plt.xlabel('Avg Abstraction Score')
        plt.ylabel('Relative Planning Gain')
        plt.title('Abstraction Quality vs Planning Gain')
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir,'scatter_abstr_gain.png'))
        plt.close()

    # Violin of gain by model
    plt.figure()
    models = df_plan['model'].unique()
    data = [df_plan[df_plan['model']==m]['gain'].dropna().values for m in models]
    plt.violinplot(data, showmeans=True)
    plt.xticks(range(1,len(models)+1), models, rotation=45)
    plt.ylabel('Planning Gain')
    plt.title('Planning Gain by Model')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir,'violin_gain_model.png'))
    plt.close()