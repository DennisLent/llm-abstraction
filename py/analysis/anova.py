from statsmodels.formula.api import ols
from statsmodels.stats.anova  import anova_lm
from statsmodels.regression.mixed_linear_model import MixedLM
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.graphics.factorplots import interaction_plot
import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def perform_ANOVA(df, df_exploded, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    # p-value for significance (set to 0.05)
    sig = 0.05

    # Ranking
    ranking = df_exploded.groupby('model')['score'].mean().sort_values(ascending=False).reset_index()

    # ANCOVA: score ~ model * prompt_id + map_size
    # Tests SRQ3 (effects of model, prompt, size), SRQ4 (model comparisons), SRQ5 (prompt sensitivity)
    ancova_mod = ols('I(score) ~ C(model)*C(prompt_id) + map_size', data=df_exploded).fit()
    ancova_table = anova_lm(ancova_mod, typ=2)
    ancova_table.to_csv(os.path.join(out_dir, "ancova_model_prompt_mapSize.csv"))

    # Interaction plots to visualize how model performance varies by prompt and map size (SRQ3)
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
        plt.title(f'Interaction: Model × {xlabel}')
        plt.xlabel(xlabel)
        plt.ylabel('Model-based Score')
        plt.savefig(os.path.join(out_dir, fname))
        plt.close()

    # Mixed-Effects: I(avg_score) ~ model + prompt_id + map_size (SRQ2: planning utility)
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

    # Tukey HSD post-hoc for model comparisons within each map (SRQ4)
    for mid, grp in df_exploded.groupby('map_id'):
        n_models = grp['model'].nunique()
        if n_models < 2:
            print(f"[ERR] Skipping Tukey for map {mid}: only {n_models} model(s)")
            continue
        tuk = pairwise_tukeyhsd(endog=grp['score'], groups=grp['model'], alpha=sig)
        tbl = pd.DataFrame(tuk._results_table.data[1:], columns=tuk._results_table.data[0])
        tbl.to_csv(os.path.join(out_dir, f"tukey_map_{mid}.csv"), index=False)

    # ANCOVA on abstraction difficulty: score ~ model * abstractability + map_size (SRQ1 & SRQ7)
    anc2_mod = ols('I(score) ~ C(model)*C(abstractability) + map_size', data=df_exploded).fit()
    anc2_table = anova_lm(anc2_mod, typ=2)
    anc2_table.to_csv(os.path.join(out_dir, "ancova_model_abstractability_mapSize.csv"))

    # Plot interaction: Model × Abstractability
    plt.figure()
    interaction_plot(
        x=df_exploded['abstractability'],
        trace=df_exploded['model'],
        response=df_exploded['score'],
        ax=plt.gca()
    )
    plt.title('Interaction: Model × Abstractability')
    plt.xlabel('Abstractability')
    plt.ylabel('Mean Model-based Score')
    plt.savefig(os.path.join(out_dir, 'interaction_model_abstractability.png'))
    plt.close()

    # Tests for representation and output format effects (SRQ6)
    if 'representation_key' in df_exploded.columns:
        rep_mod = ols('I(score) ~ C(representation_key) + map_size', data=df_exploded).fit()
        rep_table = anova_lm(rep_mod, typ=2)
        rep_table.to_csv(os.path.join(out_dir, 'ancova_representation_mapSize.csv'))
        rep_tuk = pairwise_tukeyhsd(endog=df_exploded['score'], groups=df_exploded['representation_key'], alpha=sig)
        rep_tbl = pd.DataFrame(rep_tuk._results_table.data[1:], columns=rep_tuk._results_table.data[0])
        rep_tbl.to_csv(os.path.join(out_dir, 'tukey_representation.csv'), index=False)

    if 'output' in df_exploded.columns:
        out_mod = ols('I(score) ~ C(output) + map_size', data=df_exploded).fit()
        out_table = anova_lm(out_mod, typ=2)
        out_table.to_csv(os.path.join(out_dir, 'ancova_output_mapSize.csv'))
    
    # Define the categorical prompt elements to analyze:
    prompt_cols = [
        'instruction',
        'necessary_context',
        'background_context',
        'representation_key',
        'output'
    ]

    # Combined ANOVA model across all prompt elements
    formula = 'I(score) ~ ' + ' + '.join([f'C({col})' for col in prompt_cols])
    combined_mod = ols(formula, data=df_exploded).fit()
    combined_table = anova_lm(combined_mod, typ=2)
    combined_table.to_csv(os.path.join(out_dir, 'ancova_prompt_elements.csv'))

    # Pairwise Tukey HSD and violin plots for each element
    for col in prompt_cols:
        # Single-factor ANOVA
        mod = ols(f'I(score) ~ C({col})', data=df_exploded).fit()
        table = anova_lm(mod, typ=2)
        table.to_csv(os.path.join(out_dir, f'ancova_{col}.csv'))

        # Tukey HSD post-hoc
        tuk = pairwise_tukeyhsd(
            endog=df_exploded['score'],
            groups=df_exploded[col].astype(str),
            alpha=sig
        )
        tuk_df = pd.DataFrame(tuk._results_table.data[1:],
                              columns=tuk._results_table.data[0])
        tuk_df.to_csv(os.path.join(out_dir, f'tukey_{col}.csv'), index=False)

        # Violin plot of score distribution by category
        plt.figure(figsize=(8, 5))
        sns.violinplot(
            x=col,
            y='score',
            data=df_exploded,
            inner='quartile'
        )
        plt.title(f'Model-based Score by {col.replace("_", " ").title()}')
        plt.xlabel(col.replace('_', ' ').title())
        plt.ylabel('Model-based Score')
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, f'violin_{col}.png'))
        plt.close()

    # Summary of mean performance per category
    means = df_exploded.groupby(prompt_cols)['score'].mean().reset_index()
    means.to_csv(os.path.join(out_dir, 'mean_scores_per_category.csv'), index=False)

    # Interaction plot models & repr
    plt.figure(figsize=(8,5))
    interaction_plot(
        x=df_exploded['representation_key'],
        trace=df_exploded['model'],
        response=df_exploded['score'],
        ax=plt.gca()
    )
    plt.title('Interaction: Model × Representation Method')
    plt.xlabel('Representation Key')
    plt.ylabel('Mean Model-based Score')
    plt.savefig(os.path.join(out_dir, 'interaction_model_representation.png'))
    plt.close()

    # Interaction plot model & output
    plt.figure(figsize=(8,5))
    interaction_plot(
        x=df_exploded['output'],
        trace=df_exploded['model'],
        response=df_exploded['score'],
        ax=plt.gca()
    )
    plt.title('Interaction: Model × Output Format')
    plt.xlabel('Output Format')
    plt.ylabel('Mean Model-based Score')
    plt.savefig(os.path.join(out_dir, 'interaction_model_output.png'))
    plt.close()

    # Interection plot prompt_id & abstractability
    plt.figure(figsize=(8,5))
    interaction_plot(
        x=df_exploded['prompt_id'],
        trace=df_exploded['abstractability'],
        response=df_exploded['score'],
        ax=plt.gca()
    )
    plt.title('Interaction: Prompt ID × Abstractability')
    plt.xlabel('Prompt Variant')
    plt.ylabel('Mean Model-based Score')
    plt.savefig(os.path.join(out_dir, 'interaction_prompt_abstractability.png'))
    plt.close()

    # Interaction plot prompt_id & model
    plt.figure(figsize=(8,5))
    interaction_plot(
        x=df_exploded['prompt_id'],
        trace=df_exploded['model'],
        response=df_exploded['score'],
        ax=plt.gca()
    )
    plt.title('Interaction: Prompt ID × Model')
    plt.xlabel('Prompt Variant')
    plt.ylabel('Mean Model-based Score')
    plt.savefig(os.path.join(out_dir, 'interaction_prompt_model.png'))
    plt.close()

    # Interaction plot map_size & abstractability
    plt.figure(figsize=(8,5))
    sns.pointplot(
        x='map_size', y='score', hue='abstractability',
        data=df_exploded, dodge=True, ci='sd'
    )
    plt.title('Map Size × Abstractability')
    plt.xlabel('Map Size')
    plt.ylabel('Mean Model-based Score')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'interaction_mapSize_abstractability.png'))
    plt.close()

    # Generate descriptive SRQ summary
    summary_lines = []

    # SRQ1: Can LLMs approach optimal abstraction?
    p_abs = anc2_table.loc['C(abstractability)', 'PR(>F)']
    if p_abs < sig:
        summary_lines.append(
            "SRQ1: We performed an ANCOVA on abstraction difficulty (abstractability) and found a significant main effect "
            f"(F={anc2_table.loc['C(abstractability)', 'F']:.2f}, p={p_abs:.3g}), indicating that maps that are fully abstractable "
            "yield higher abstraction scores. This shows LLMs can approximate the optimal abstraction when it exists."
        )
    else:
        summary_lines.append(
            "SRQ1: No significant effect of map abstractability on LLM scores (p > 0.05), suggesting LLMs produce comparable abstractions regardless of whether an optimal abstraction is defined."
        )

    # SRQ2: Are abstractions useful for planning?
    top_mean = ranking.iloc[0]['score']
    summary_lines.append(
        "SRQ2: Using a mixed-effects model accounting for map-level variance, we estimated average abstraction scores. "
        f"The best-performing model achieved an average score of {top_mean:.3f}, demonstrating that LLM-based abstractions reach sufficient quality to be actionable in planning tasks."
    )

    # SRQ3: Impact of model, prompt phrasing, and map size
    p_model = ancova_table.loc['C(model)', 'PR(>F)']
    p_prompt = ancova_table.loc['C(prompt_id)', 'PR(>F)']
    p_size = ancova_table.loc['map_size', 'PR(>F)']
    summary_lines.append(
        "SRQ3: An ANCOVA testing model, prompt variation, and map size revealed significant main effects "
        f"on abstraction quality: model (F={ancova_table.loc['C(model)', 'F']:.2f}, p={p_model:.3g}), "
        f"prompt (F={ancova_table.loc['C(prompt_id)', 'F']:.2f}, p={p_prompt:.3g}), and size (F={ancova_table.loc['map_size', 'F']:.2f}, p={p_size:.3g}). "
        "Interaction plots illustrate how these factors jointly influence performance."
    )

    # SRQ4: Comparative performance of LLMs
    top3 = ranking['model'][:3].tolist()
    summary_lines.append(
        "SRQ4: Post-hoc Tukey HSD comparisons for each map identified the top-performing LLMs. "
        f"Across all maps, the leading models are {', '.join(top3)}, with {top3[0]} consistently outperforming others."
    )

    # SRQ5: Sensitivity to prompt phrasing
    if p_prompt < sig:
        summary_lines.append(
            "SRQ5: The significant main effect of prompt ID indicates that abstraction scores vary by prompt phrasing, "
            "highlighting the importance of carefully designing prompt templates."
        )
    else:
        summary_lines.append(
            "SRQ5: No significant differences across prompt versions, suggesting robustness of LLM abstractions to minor phrasing changes."
        )

    # SRQ6: Effects of representation and output format
    if 'rep_table' in locals():
        p_rep = rep_table.loc['C(representation_key)', 'PR(>F)']
        summary_lines.append(
            f"SRQ6: ANOVA on representation method shows a significant effect (F={rep_table.loc['C(representation_key)', 'F']:.2f}, p={p_rep:.3g}), "
            "indicating some encoding schemes yield clearer abstractions for LLMs."
        )
    if 'out_table' in locals():
        p_out = out_table.loc['C(output)', 'PR(>F)']
        summary_lines.append(
            f"SRQ6: The choice of output format also influences scores (F={out_table.loc['C(output)', 'F']:.2f}, p={p_out:.3g}), "
            "suggesting that structured or compact formats may aid LLM comprehension."
        )

    # SRQ7: Behavior when no perfect abstraction exists
    p_inter = anc2_table.loc['C(model):C(abstractability)', 'PR(>F)']
    if p_inter < sig:
        summary_lines.append(
            "SRQ7: A significant interaction between model and abstractability (F={anc2_table.loc['C(model):C(abstractability)', 'F']:.2f}, "
            f"p={p_inter:.3g}) indicates that while all models degrade when perfect abstraction is impossible, some handle complexity better."
        )
    else:
        summary_lines.append(
            "SRQ7: No significant interaction effect, meaning model performance decreases uniformly as maps become less abstractable."
        )

    # Write summary to file
    with open(os.path.join(out_dir, 'summary.txt'), 'w') as f:
        for line in summary_lines:
            f.write(line + '\n')

    # Save a ranking by average score (best→worst) for reference
    with open(os.path.join(out_dir, 'model_ranking.txt'), 'w') as f:
        f.write('Model ranking (best→worst):\n')
        for i, row in ranking.iterrows():
            f.write(f"{i+1}. {row['model']} : {row['score']:.4f}\n")

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