from .utils import parse_maps, classify_abstraction
from .llm import generate_prompts, query_llm, bisimulation_similarity
from .evaluation import map_to_filename, mcts_evaluation, mcts_llm_evaluation
from core_rust import get_number_of_states, generate_mdp, visualize_abstraction, visualize_world_map
import numpy as np
import os
import json
from .analysis import get_info, perform_ANOVA, plot_distributions, get_planning_info, perform_planning_analysis, plot_gain_heatmaps, plot_gain_lines, \
    rank_models, rank_models_prompts, build_full_ranking_table
import pandas as pd
import time

def preview_prompts(general_config: dict, prompt_config: dict):
    """
    This is a main callable function that just previews all the prompts to the user in the CLI.
    It takes the prompts specified in `config.yml` and generates them using the content in `config_prompts.yml` and the rust_core.
    """

    parsed_maps = parse_maps(general_config["game"])
    compositions = general_config["llm"]["compositions"]

    for parsed_map in parsed_maps:
        map_name = map_to_filename(parsed_map)
        print(f"----- Using map with hash {map_name} -----")

        prompts = generate_prompts(compositions=compositions, prompts=prompt_config, world=parsed_map)

        for idx, prompt in enumerate(prompts):
            print(f"PROMPT: {idx}")
            print(f"{prompt}")
            print(f"--------------------\n")

def preview_maps(general_config: dict):
    """
    Preview each map and save its abstraction plus a metadata CSV
    with abstractability labels for later consumption.
    Uses pandas to append only new map entries.
    """
    parsed_maps = parse_maps(general_config["game"])

    # prepare output folders
    maps_out = os.path.join('outputs', 'maps')
    os.makedirs(maps_out, exist_ok=True)
    csv_path = os.path.join(maps_out, "map_abstractability.csv")

    # load existing metadata or create empty DataFrame
    if os.path.exists(csv_path):
        df_meta = pd.read_csv(csv_path)
    else:
        df_meta = pd.DataFrame(columns=["map_name", "abstractability"])

    new_records = []

    for parsed_map in parsed_maps:
        t1 = time.time()
        map_name = map_to_filename(parsed_map)
        print(f"[PREVIEW] {map_name}", flush=True)

        map_dir  = os.path.join(maps_out, map_name)
        os.makedirs(map_dir, exist_ok=True)

        # visualize
        print(f"visualizing world...")
        visualize_world_map(parsed_map, map_dir)
        print(f"calculating abstraction...")
        visualize_abstraction(parsed_map, map_dir)

        # classify
        print(f"determining abstractability...")
        abstr = classify_abstraction(parsed_map)
        print(f"Abstractability: {abstr}")
        new_records.append({"map_name": map_name, "abstractability": abstr})

        t2 = time.time()
        print(f"Time taken for map {map_name}: {t2 - t1} seconds")

    # build DataFrame of just-new maps
    df_new = pd.DataFrame(new_records)

    # find which map_names are missing already
    missing = df_new[~df_new["map_name"].isin(df_meta["map_name"])]

    if not missing.empty:
        
        df_meta = pd.concat([df_meta, missing], ignore_index=True)
        df_meta.to_csv(csv_path, index=False)
        print(f"Appended {len(missing)} new entries to {csv_path}")
    else:
        print("No new maps to append.")

    return df_meta

def mcts(general_config: dict, show_mcts: bool = False):
    """
    This function runs baseline experiments for MCTS.
    It uses the configurations from the `config.yml` to initialize different maps and MCTS experiments.
    It will always run a ground agent (no abstraction) and an abstract agent (perfect abstraction).
    The results are saved in outputs.
    """
    
    # Maps
    parsed_maps = parse_maps(general_config["game"])


    # MCTS variables from config file
    mcts_variables = general_config["mcts_variables"]
    simulation_limtits = mcts_variables["simulation_limit"]
    simulation_depths = mcts_variables["simulation_depth"]
    runs = mcts_variables["runs"]
    c = mcts_variables["c"]
    gamma = mcts_variables["gamma"]
    debug_flag = mcts_variables["debug"]

    # Agent config
    # 1 ground agent, 1 perfect abstraction
    runner_configs = [
        (False, None, "Ground"),
        (True, None, "Abstract")]


    for parsed_map in parsed_maps:
        mcts_evaluation(simulation_limits=simulation_limtits,
                        simulation_depths=simulation_depths,
                        world=parsed_map,
                        runner_configs=runner_configs,
                        folder_name="mcts",
                        runs=runs,
                        c=c,
                        gamma=gamma,
                        debug=debug_flag,
                        show_mcts=show_mcts)

def evaluate_prompt(general_config: dict, prompt_config: dict, model: str, prompt_index: int, map_hashes: list[str] = None, debug: bool = False):
    
    # Iterate over all maps or specified map hashes
    if map_hashes is not None:
        # Find hash names and run only over these
        config_maps = parse_maps(general_config["game"])
        hashed_map_names = [map_to_filename(chosen_map) for chosen_map in config_maps]
        parsed_maps = []
        for map_hash in map_hashes:
            map_index = hashed_map_names.index(map_hash)
            parsed_maps.append(config_maps[map_index])
    else:
        # Just use all the maps in the config
        parsed_maps = parse_maps(general_config["game"])
    
    compositions = general_config["llm"]["compositions"]
    llm_runs = general_config["llm"]["tries"]

    cleaned_and_scored = {}

    for parsed_map in parsed_maps:
        map_name = map_to_filename(parsed_map)
        print(f"----- Using map with hash {map_name} -----")

        prompts = generate_prompts(compositions=compositions, prompts=prompt_config, world=parsed_map)
        print(f"----- Using prompt index {prompt_index} -----")
        prompt = prompts[prompt_index]

        num_states = get_number_of_states(parsed_map)

        # Get the dictionary containing the raw and cleaned responses
        cleaned_responses = query_llm(prompt=prompt, runs=llm_runs, model=model, num_states=num_states, debug=debug)

        # Evaluate and score all the responses
        map_specific_results = {
            "raw_responses": [],
            "cleaned_responses": [],
            "scores": []
        }

        mdp_dictionary = generate_mdp(parsed_map)
        transition_matrix = np.array(mdp_dictionary["T"])
        reward_matrix = np.array(mdp_dictionary["R"])
        ideal_abstraction = mdp_dictionary["abstraction"]

        for raw_response, extracted_abstraction in zip(*cleaned_responses.values()):
            score = bisimulation_similarity(candidate_clustering=extracted_abstraction, 
                                            ideal_clustering=ideal_abstraction,
                                            transitions=transition_matrix,
                                            rewards=reward_matrix)
            map_specific_results["raw_responses"].append(raw_response)
            map_specific_results["cleaned_responses"].append(extracted_abstraction)
            map_specific_results["scores"].append(score)
        
        cleaned_and_scored[map_name] = map_specific_results
    
    return cleaned_and_scored

def llm_abstraction(general_config: dict, prompt_config: dict, model: str, prompt_index: int, map_hashes: list[str] = None, debug: bool = False):
    folder_name = 'llm_scoring'

    cleaned_and_scored = evaluate_prompt(general_config=general_config,
                                         prompt_config=prompt_config,
                                         model=model,
                                         prompt_index=prompt_index,
                                         map_hashes=map_hashes,
                                         debug=debug)
    
    print(f"Successfully generated all prompts for all maps")
    
    # Iterate over all maps or specified map hashes
    if map_hashes is not None:
        # Find hash names and run only over these
        config_maps = parse_maps(general_config["game"])
        hashed_map_names = [map_to_filename(chosen_map) for chosen_map in config_maps]
        parsed_maps = []
        for map_hash in map_hashes:
            map_index = hashed_map_names.index(map_hash)
            parsed_maps.append(config_maps[map_index])
    else:
        # Just use all the maps in the config
        parsed_maps = parse_maps(general_config["game"])

    for parsed_map in parsed_maps:
        map_name = map_to_filename(parsed_map)

        print(f"Benchmarking map: {map_name}")

        # Save map results
        map_responses = cleaned_and_scored[map_name]

        json_save_path = os.path.join('outputs',folder_name, map_name)
        if not os.path.isdir(json_save_path):
            os.mkdir(json_save_path)
        file_name = f"{prompt_index}_{model}_out.json"
        file_path = os.path.join(json_save_path, file_name)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(map_responses, f, ensure_ascii=False, indent=2)

        # Find lowest scoring abstraction
        raw_responses   = map_responses["raw_responses"]
        cleaned_responses = map_responses["cleaned_responses"]
        scores  = map_responses["scores"]

        best_score, _, best_abstraction = max(zip(scores, raw_responses, cleaned_responses), key=lambda trio: trio[0])

        print(f"Model: {model} @ prompt index: {prompt_index}")
        print(f"Best scoring abstraction: {best_abstraction}")
        print(f"Score: {best_score}")

        # Agent config
        # 1 ground agent, 1 perfect abstraction, 1 LLM abstraction
        runner_configs = [
            (False, None, "Ground"),
            (True, None, "Abstract"),
            (True, best_abstraction, "LLM")
        ]
        
        # MCTS variables from config file
        mcts_variables = general_config["mcts_variables"]
        simulation_limits = mcts_variables["simulation_limit"]
        simulation_depths = mcts_variables["simulation_depth"]
        runs = mcts_variables["runs"]
        c = mcts_variables["c"]
        gamma = mcts_variables["gamma"]
        debug_flag = mcts_variables["debug"]

        
        # Run MCTS and save
        mcts_llm_evaluation(simulation_limits=simulation_limits,
                            simulation_depths=simulation_depths,
                            world=parsed_map,
                            runner_configs=runner_configs,
                            folder_name=folder_name,
                            prompt_index=prompt_index,
                            model=model,
                            runs=runs,
                            c=c,
                            gamma=gamma,
                            debug=debug_flag)

def analysis(general_config: dict):
    root_dir = os.path.join("outputs", "llm_scoring")
    df, df_exploded = get_info(general_config=general_config, root_dir=root_dir)
    df_plan = get_planning_info(root_dir=root_dir)

    out_dir = os.path.join("outputs", "analysis")

    # Merge model-based and performance-based metrics into 1 df
    df_abstr = (df.groupby(['map_id','model','prompt_id'], observed=True)['best_score'].max().reset_index().rename(columns={'best_score':'model_based_score'}))
    df_merged = pd.merge(df_abstr, df_plan, on=['map_id','model','prompt_id'],how='inner')

    # Get new table for all rankings
    ranking_df = build_full_ranking_table(df_exploded=df_exploded, df_plan=df_plan)

    # Save ranking df
    df_save_path = os.path.join(out_dir, "ranking.csv")
    ranking_df.to_csv(df_save_path)

    rank_models(ranking_df)
    rank_models_prompts(ranking_df)

    # perform anova & other analyses
    print("Performaing analysis...")
    perform_ANOVA(df=df, df_exploded=df_exploded, out_dir=out_dir)
    perform_planning_analysis(df_plan=df_plan, out_dir=out_dir)
    print("Plotting distributions...")
    plot_distributions(df_exploded=df_exploded, out_dir=out_dir)
    print("Plotting heatmaps...")
    plot_gain_heatmaps(df_merged=df_merged, out_dir=out_dir)
    print(f"Plotting gain curves...")
    plot_gain_lines(df_merged=df_merged, out_dir=out_dir)
