import pandas as pd

def build_full_ranking_table(df_exploded, df_plan):
    df_model_all = (
        df_exploded
        .groupby(['map_id','model','prompt_id'], observed=True, as_index=False)
        .agg(
            avg_model_score=('score','mean'),
            max_model_score=('score','max'),
            std_model_score=('score','std'),
            n_model_runs = ('score','count'),
        )
    )

    df_plan_avg = (
        df_plan
        .groupby(['map_id','model','prompt_id'], observed=True, as_index=False)
        .agg(
            avg_gain      =('gain','mean'),
            avg_rel_gain  =('rel_gain','mean'),
            avg_gain_diff =('gain_diff','mean'),
            n_plan_runs   =('gain','count'),
        )
    )

    df_full = pd.merge(
        df_model_all,
        df_plan_avg,
        on=['map_id','model','prompt_id'],
        how='inner'
    )

    return df_full

def rank_models(df_full):
    """
    df_full must contain columns:
      - 'model'
      - 'avg_model_score'   (mean abstraction score per map/model/prompt)
      - 'avg_gain_diff'     (mean gain_diff per map/model/prompt)
    """
    # 1. Aggregate to one row per model
    model_summary = (
        df_full
        .groupby('model', observed=True, as_index=False)
        .agg(
            mean_model_score = ('avg_model_score', 'mean'),
            mean_gain_diff   = ('avg_gain_diff',   'mean'),
        )
    )

    # 2. Compute z-scores
    model_summary['z_score']     = (
        model_summary['mean_model_score'] 
        - model_summary['mean_model_score'].mean()
    ) / model_summary['mean_model_score'].std(ddof=0)

    model_summary['z_gain_diff'] = (
        model_summary['mean_gain_diff'] 
        - model_summary['mean_gain_diff'].mean()
    ) / model_summary['mean_gain_diff'].std(ddof=0)

    # 3. Combine (lower gain_diff is better, so subtract its z-score)
    model_summary['composite_z'] = model_summary['z_score'] - model_summary['z_gain_diff']

    # 4. Sort descending (higher composite_z = better)
    model_summary = model_summary.sort_values('composite_z', ascending=False).reset_index(drop=True)

    # 5. Display or return
    print(model_summary[['model','mean_model_score','mean_gain_diff','composite_z']])
    return model_summary

def rank_models_prompts(df_full):
    """
    Given df_full with columns:
      - 'map_id','model','prompt_id',
      - 'avg_model_score','avg_gain_diff', ...
    Returns a DataFrame ranking each (model, prompt_id) pair by a z-score composite.
    """

    # 1. Aggregate to one row per model × prompt
    combo_summary = (
        df_full
        .groupby(['model','prompt_id'], observed=True, as_index=False)
        .agg(
            mean_model_score = ('avg_model_score', 'mean'),
            mean_gain_diff   = ('avg_gain_diff',   'mean'),
        )
    )

    # 2. Compute z-scores across all combos
    combo_summary['z_score'] = (
        combo_summary['mean_model_score'] 
        - combo_summary['mean_model_score'].mean()
    ) / combo_summary['mean_model_score'].std(ddof=0)

    combo_summary['z_gain_diff'] = (
        combo_summary['mean_gain_diff'] 
        - combo_summary['mean_gain_diff'].mean()
    ) / combo_summary['mean_gain_diff'].std(ddof=0)

    # 3. Fuse (higher score ↑ better; lower gain_diff ↑ better → subtract)
    combo_summary['composite_z'] = (
        combo_summary['z_score'] 
        - combo_summary['z_gain_diff']
    )

    # 4. Sort descending by composite_z
    combo_summary = combo_summary.sort_values('composite_z', ascending=False) \
                                 .reset_index(drop=True)

    # 5. Return the ranked table
    print(combo_summary[['model','prompt_id', 'mean_model_score','mean_gain_diff','composite_z']])
    return combo_summary[['model','prompt_id','mean_model_score','mean_gain_diff','composite_z']]

