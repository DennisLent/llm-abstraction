from py import preview_prompts, load_config, mcts, evaluate_prompt, preview_maps, llm_abstraction, analysis
import argparse

# Main parser
parser = argparse.ArgumentParser(description="Run LLM abstractions and see how good they are")
command_arg = parser.add_subparsers(dest="command", required=True, help="Available commands")

# Subparser for prompt preview
preview_prompt_parser = command_arg.add_parser("preview-prompts", help="Preview generated prompts before execution")

# Subparser for map preview
preview_maps_parser = command_arg.add_parser("preview-maps", help="Preview generated maps before execution")

# Subparser for running pure MCTS (debug flag)
mcts_parser = command_arg.add_parser("mcts", help="Preview generated prompts before execution")
mcts_parser.add_argument("-d", "--debug", action="store_true", help="Run showing only the MCTS game tree")

# Subparser for running pure prompt scoring (debug flag, prompt index [required], model name [required])
prompt_benchmarking_parser = command_arg.add_parser("score-prompts", help="Generate prompts for a given map and have them scored")
prompt_benchmarking_parser.add_argument("-d", "--debug", action="store_true", help="Run showing debug information")
prompt_benchmarking_parser.add_argument("-i", "--index", type=int, nargs="+", required=True, help="Indicate which prompt to use based on the index")
prompt_benchmarking_parser.add_argument("-m", "--model", type=str, nargs="+", required=True, help="Indicate which model to use using the name as specified in the ollama library: https://ollama.com/library")

# Subparser for running prompt scoring alongside MCTS (debug flag, prompt index [required], model name [required])
benchmark_llm_parser = command_arg.add_parser("benchmark-llm", help="Generate prompts for a given map, score them and evaluate them using MCTS")
benchmark_llm_parser.add_argument("-d", "--debug", action="store_true", help="Run showing debug information")
benchmark_llm_parser.add_argument("-i", "--index", type=int, nargs="+", required=True, help="Indicate which prompt to use based on the index")
benchmark_llm_parser.add_argument("-m", "--model", type=str, nargs="+", required=True, help="Indicate which model to use using the name as specified in the ollama library: https://ollama.com/library")
benchmark_llm_parser.add_argument("-g", "--maps", type=str, nargs="+", help="Select a specific map hash to only run on that map (that must be present in the config)")

# Subparser for analysis
analysis_parser = command_arg.add_parser("analysis", help="Analyze the benchmarking results")

def main():
    args = parser.parse_args()
    if args.command:
        general_config = load_config("config.yml")
        prompt_config = load_config("config_prompts.yml")

        if args.command == "preview-prompts":
            preview_prompts(general_config=general_config, prompt_config=prompt_config)
        
        if args.command == "preview-maps":
            preview_maps(general_config=general_config)
        
        if args.command == "mcts":

            mcts(general_config=general_config, show_mcts=args.debug)
        
        if args.command == "score-prompts":
            
            for model in args.model:
                for idx in args.index:
                    print(f">> Running {model} @ prompt index {idx}")
                    scored_responses = evaluate_prompt(general_config=general_config, 
                                                    prompt_config=prompt_config, 
                                                    model=model, 
                                                    prompt_index=idx, 
                                                    debug=args.debug)
            
            for map in scored_responses.keys():
                cleaned_responses = scored_responses[map]["cleaned_responses"]
                scores = scored_responses[map]["scores"]
                print(f"----- {args.model} @ prompt index {args.index} -> {map} -----")
                print(cleaned_responses)
                print(scores)
        
        if args.command == "benchmark-llm":

            for model in args.model:
                for idx in args.index:
                    print(f">> Running {model} @ prompt index {idx}")
                    llm_abstraction(general_config=general_config,
                                    prompt_config=prompt_config,
                                    model=model,
                                    prompt_index=idx,
                                    map_hashes=args.maps,
                                    debug=args.debug)
        
        if args.command == "analysis":
            analysis(general_config=general_config)

    else:
        print("No arguments specified...\nSee the help guide below")
        parser.print_help()

if __name__ == "__main__":
    main()



