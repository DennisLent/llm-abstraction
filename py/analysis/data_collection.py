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
