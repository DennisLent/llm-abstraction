import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
import seaborn as sns
from tqdm import tqdm

def plot_distributions(df_exploded, out_dir):
    """Plot distributional summaries of model-based scores.

    Parameters
    ----------
    df_exploded : pandas.DataFrame
        Long-form table with one row per score; must include ``model``,
        ``representation_key`` (optional), and ``prompt_id``.
    out_dir : str
        Directory where figures will be saved.

    Returns
    -------
    None
    """

    # Violin: models
    manual_order = ['llama3.1:8b', 'llama3.1:70b', 'llama3.3:70b', 'deepseek-r1:7b', 'deepseek-r1:8b', 'deepseek-r1:14b',
                    'deepseek-r1:32b', 'deepseek-r1:70b']
    df_exploded['model'] = df_exploded['model'].cat.reorder_categories(manual_order, ordered=True)
    models = list(df_exploded['model'].cat.categories)
    data = [df_exploded[df_exploded['model'] == m]['score'].values for m in models]
    plt.figure()
    plt.violinplot(data, showmeans=True)
    plt.xticks(range(1, len(models) + 1), models, rotation=45)
    plt.ylabel('Model-based Score')
    plt.title('Score distribution by model')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'violin_models.png'))
    plt.close()

    # Bar: representation_key
    if 'representation_key' in df_exploded.columns:
        rep_means = df_exploded.groupby('representation_key')['score'].mean().sort_values()
        plt.figure()
        plt.bar(rep_means.index.astype(str), rep_means.values)
        plt.xticks(rotation=45)
        plt.ylabel('Average Model-based Score')
        plt.title('Average score by representation_key')
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, 'representation_performance.png'))
        plt.close()

    # Violin: prompt_id
    prompts = sorted(df_exploded['prompt_id'].unique())
    data = [df_exploded[df_exploded['prompt_id'] == p]['score'].values for p in prompts]
    plt.figure()
    plt.violinplot(data, showmeans=True)
    plt.xticks(range(1, len(prompts) + 1), prompts)
    plt.ylabel('Model-based Score')
    plt.title('Score distribution by prompt_id')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'violin_prompts.png'))
    plt.close()

    # Size and score plots
    families = {
        'llama':    ['llama3.1:8b', 'llama3.1:70b', 'llama3.3:70b'],
        'deepseek': ['deepseek-r1:7b', 'deepseek-r1:8b', 'deepseek-r1:14b',
                    'deepseek-r1:32b', 'deepseek-r1:70b']
    }

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)

    for ax, (family, model_list) in zip(axes, families.items()):
        sizes = []
        means = []
        for m in model_list:
            s = int(m.split(':')[1].rstrip('b'))

            # bump llama3.3:70b to 71 so it doesn't overlap
            if m == 'llama3.3:70b':
                s = 71
            sizes.append(s)
            means.append(df_exploded.loc[df_exploded['model'] == m, 'score'].mean())

        # plot line + markers
        ax.plot(sizes, means, marker='o', linestyle='-')
        ax.set_title(family.capitalize() + ' family')
        ax.set_xlabel('Model size (B)')
        ax.set_xticks(sizes)

    axes[0].set_ylabel('Average model-based score')
    fig.suptitle('Average Score vs. Model Size by Family')
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.savefig(os.path.join(out_dir, 'avg_score_by_family_size.png'))
    plt.close(fig)

def plot_gain_heatmaps(df_merged, out_dir: str):
    """Create heatmaps of planning gain across depth/limit for each prompt.

    Parameters
    ----------
    df_merged : pandas.DataFrame
        Data joined with model-based scores; must include ``map_id``, ``model``,
        ``prompt_id``, ``simulation_depth``, ``simulation_limit``, and ``gain``.
    out_dir : str
        Directory where figures will be saved (grouped by map).

    Returns
    -------
    None
    """
    os.makedirs(out_dir, exist_ok=True)

    # Group by map and model only
    for (map_id, model), sub_model in tqdm(df_merged.groupby(['map_id','model'], observed=True), desc='Heatmaps'):
        prompts = sorted(sub_model['prompt_id'].unique())
        n = len(prompts)
        # determine grid size
        cols = min(4, n)
        rows = (n + cols - 1) // cols
        fig, axes = plt.subplots(rows, cols, figsize=(4*cols, 3*rows), squeeze=False)

        # compute global vmin/vmax for consistent color scaling
        pivot_all = sub_model.pivot_table(
            index='simulation_depth', columns='simulation_limit', values='gain', aggfunc='mean'
        )
        vmin, vmax = pivot_all.min().min(), pivot_all.max().max()

        for idx, pid in enumerate(prompts):
            r, c = divmod(idx, cols)
            ax = axes[r][c]
            sub = sub_model[sub_model['prompt_id']==pid]
            pivot = sub.pivot_table(
                index='simulation_depth', columns='simulation_limit', values='gain', aggfunc='mean'
            )
            if pivot.empty:
                ax.axis('off')
                continue

            # plot heatmap
            cax = ax.pcolor(pivot.values, vmin=vmin, vmax=vmax)
            ax.set_title(f'Prompt {pid} Model-based Score: {sub["model_based_score"].iloc[0]:.2f}')
            ax.set_xlabel('Limit')
            ax.set_ylabel('Depth')
            ax.set_xticks(np.arange(0.5, pivot.shape[1], 1))
            ax.set_yticks(np.arange(0.5, pivot.shape[0], 1))
            ax.set_xticklabels(pivot.columns.astype(str), rotation=45)
            ax.set_yticklabels(pivot.index.astype(str))

        # turn off unused axes
        for idx in range(n, rows*cols):
            r, c = divmod(idx, cols)
            axes[r][c].axis('off')

        # shared colorbar
        fig.tight_layout()
        fig.subplots_adjust(right=0.85)
        cb_ax = fig.add_axes([0.88, 0.15, 0.02, 0.7])
        fig.colorbar(cax, cax=cb_ax, label='Planning Gain')

        # save
        sub_dir = os.path.join(out_dir, map_id)
        os.makedirs(sub_dir, exist_ok=True)
        fname = f"heatmap_{model}.png"
        fig.savefig(os.path.join(sub_dir, fname))
        plt.close(fig)


def plot_gain_lines(df_merged, out_dir: str):
    """Plot planning gain difference curves per depth and prompt.

    Parameters
    ----------
    df_merged : pandas.DataFrame
        Data table including ``map_id``, ``model``, ``prompt_id``,
        ``simulation_depth``, ``simulation_limit``, and ``gain_diff``.
    out_dir : str
        Directory where figures will be saved (grouped by map).

    Returns
    -------
    None
    """

    os.makedirs(out_dir, exist_ok=True)

    # Group by map and model
    for (map_id, model), sub_model in tqdm(df_merged.groupby(['map_id','model'], observed=True), desc='Gain Plots'):
        prompts = sorted(sub_model['prompt_id'].unique())
        depths = sorted(sub_model['simulation_depth'].unique())
        n_p = len(prompts)
        n_d = len(depths)

        fig, axes = plt.subplots(n_d, n_p,
                                 figsize=(4*n_p, 3*n_d),
                                 squeeze=False)

        for i, depth in enumerate(depths):
            for j, pid in enumerate(prompts):
                ax = axes[i][j]
                sub = sub_model[
                    (sub_model['prompt_id'] == pid) &
                    (sub_model['simulation_depth'] == depth)
                ]
                if sub.empty:
                    ax.axis('off')
                    continue

                # plot gain vs limit
                sns.lineplot(
                    data=sub,
                    x='simulation_limit', y='gain_diff', marker='o', ax=ax
                )
                ax.set_title(f'Prompt {pid} | Depth {depth}')
                if i == n_d - 1:
                    ax.set_xlabel('Limit')
                else:
                    ax.set_xlabel('')
                if j == 0:
                    ax.set_ylabel('Gain Difference')
                else:
                    ax.set_ylabel('')

        fig.suptitle(f'Planning Gain Difference: {map_id} – {model}', fontsize=16)
        fig.tight_layout(rect=[0, 0, 1, 0.95])

        sub_dir = os.path.join(out_dir, map_id)
        os.makedirs(sub_dir, exist_ok=True)
        fname = f"gain_grid_{model}.png"
        fig.savefig(os.path.join(sub_dir, fname))
        plt.close(fig)
