import os
import numpy as np
import pandas as pd
import re
import json

def get_info(general_config: dict, root_dir: str):

    # Compositions to compare
    compositions = general_config["llm"]["compositions"]

    # Abstractability grouping
    abstractability_path = os.path.join("outputs", "maps", "map_abstractability.csv")
    abstractability_df = pd.read_csv(abstractability_path).set_index("map_name")

    rows = []
    json_pattern = re.compile(r'^(?P<prompt_id>\d+)_(?P<model>.+?)_out\.json$')
    csv_pattern = re.compile(r'^(?P<prompt_id>\d+)_(?P<model>.+?)_raw_results\.csv$')
    map_id_pattern = m = re.compile(r'^map_(?P<size>\d+)x\d+_')

    for map_id in os.listdir(root_dir):
        map_dir = os.path.join(root_dir, map_id)
        if not os.path.isdir(map_dir):
            raise KeyError(f"{map_dir} is not a directory")
        
        if map_id in abstractability_df.index:
            abstr = abstractability_df.at[map_id, "abstractability"]
        else:
            raise KeyError(f"map_id {map_id} does not exist in map_abstractability.csv. Please run `preview-maps` to generate classification")
        
        map_m = map_id_pattern.match(map_id)
        map_size = int(map_m.group("size"))
        
        json_paths = [os.path.join(map_dir, f) for f in os.listdir(map_dir) if f.endswith('.json')]
        csv_paths = [os.path.join(map_dir, f) for f in os.listdir(map_dir) if f.endswith('.csv')]

        for json_file_path in json_paths:
            file_name = os.path.basename(json_file_path)

            json_m = json_pattern.match(file_name)
            prompt_id = int(json_m.group("prompt_id"))
            model_name = json_m.group("model")
            composition = compositions[prompt_id]

            records = json.load(open(json_file_path))

            rows.append({
                "map_id": map_id,
                "map_size": map_size,
                "abstractability": abstr,
                "model": model_name,
                "prompt_id": prompt_id,
                "instruction": composition["instruction"],
                "necessary_context": composition["necessary_context"],
                "background_contexts": composition["background_contexts"],
                "representation_key": composition["representation_key"],
                "output": composition["output"],
                "scores": records["scores"],
                "avg_score": np.mean(records["scores"]),
                "best_score": np.max(records["scores"])
            })
    
    df = pd.DataFrame(rows)

    df_exploded = df.explode('scores').rename(columns={'scores':'score'})

    df_exploded = df_exploded.explode('background_contexts').rename(columns={'background_contexts':'background_context'})

    df_exploded['score'] = pd.to_numeric(df_exploded['score'], errors='raise')

    # All of these are categorical:
    for col in [
        'model',
        'instruction',
        'necessary_context',
        'background_context',
        'representation_key',
        'output',
        'abstractability'
    ]:
        df_exploded[col] = df_exploded[col].astype('category')

    return df, df_exploded

def get_planning_info(root_dir: str) -> pd.DataFrame:
    """
    Load MCTS planning results and compute gain and relative gain.
    Expects per-map folders with CSVs named {prompt_id}_{model}_raw_results.csv.
    Returns a DataFrame pivoted on agent_type with gain & rel_gain computed.
    """
    rows = []
    plan_pattern = re.compile(r'^(?P<prompt_id>\d+)_(?P<model>.+?)_raw_results\.csv$')
    map_pattern  = re.compile(r'^map_(?P<size>\d+)x\d+_')

    for map_id in os.listdir(root_dir):
        map_dir = os.path.join(root_dir, map_id)
        if not os.path.isdir(map_dir):
            continue

        # parse out the size
        m_map = map_pattern.match(map_id)
        if not m_map:
            print(f"[WARN] skipping directory with unexpected name: {map_id}")
            continue
        map_size = int(m_map.group('size'))

        # find all raw-results CSVs
        for fname in os.listdir(map_dir):
            m = plan_pattern.match(fname)
            if not m:
                continue
            prompt_id = int(m.group('prompt_id'))
            model     = m.group('model')
            csv_path  = os.path.join(map_dir, fname)

            df_csv = pd.read_csv(csv_path)
            if 'agent_type' not in df_csv or 'average_score' not in df_csv:
                print(f"[WARN] skipping {fname} because missing required columns")
                continue

            # attach metadata -- use the folder name, not m_map
            df_csv['map_id']       = map_id
            df_csv['map_size']     = map_size
            df_csv['model']        = model
            df_csv['prompt_id']    = prompt_id

            rows.append(df_csv)

    if not rows:
        return pd.DataFrame()

    df_all = pd.concat(rows, ignore_index=True)

    # pivot so each agent_type becomes its own column of average_score
    df_grp = df_all.pivot_table(
        index=['map_id','map_size','model','prompt_id','simulation_depth','simulation_limit'],
        columns='agent_type',
        values='average_score',
        aggfunc='mean'  # make explicit
    ).reset_index()

    # compute gains
    df_grp['gain']      = df_grp['LLM']   - df_grp['Ground']
    df_grp['ideal_gain'] = df_grp['Abstract'] - df_grp['Ground']
    df_grp['rel_gain']  = df_grp['gain']  / df_grp['ideal_gain']
    df_grp['gain_diff'] = df_grp['ideal_gain'] - df_grp['gain']

    return df_grp
