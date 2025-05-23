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
    ancova_mod = ols('I(score) ~ C(model)*C(prompt_id) + map_size', data=df_exploded).fit()
    ancova_table = anova_lm(ancova_mod, typ=2)
    ancova_table.to_csv(os.path.join(out_dir, "ancova_model_prompt_mapSize.csv"))


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
    for mid, grp in df_exploded.groupby('map_id'):
        tuk = pairwise_tukeyhsd(endog=grp['score'], groups=grp['model'], alpha=sig)
        tbl = pd.DataFrame(tuk._results_table.data[1:], columns=tuk._results_table.data[0])
        tbl.to_csv(os.path.join(out_dir, f"tukey_map_{mid}.csv"), index=False)

    # 4) ANOVA on abstractability: score ~ model * abstractability + map_size
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
    plt.gca().invert_yaxis()
    plt.title('Interaction: Model × Abstractability')
    plt.xlabel('Abstractability')
    plt.ylabel('Mean Score')
    plt.savefig(os.path.join(out_dir, 'interaction_model_abstractability.png'))
    plt.close()