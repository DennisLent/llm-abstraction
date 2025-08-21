import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def analyze_log_summary(general_config: dict, out_dir: str) -> None:
    """Analyse LLM scoring log summary for failures and run counts.

    Parameters
    ----------
    general_config : dict
        Repository configuration used to determine expected prompts.
    out_dir : str
        Directory where analysis figures and tables will be saved.
    """
    log_path = os.path.join("outputs", "llm_scoring", "log_summary.csv")
    if not os.path.exists(log_path):
        print(f"[WARN] {log_path} not found. Skipping log summary analysis.")
        return

    abstr_path = os.path.join("outputs", "maps", "map_abstractability.csv")
    df = pd.read_csv(log_path)

    # Derive map size from map name and join abstractability information
    df["map_size"] = df["map_name"].str.extract(r"map_(\d+)x").astype(int)
    if os.path.exists(abstr_path):
        df_abstr = pd.read_csv(abstr_path)
        df = df.merge(df_abstr, on="map_name", how="left")
    else:
        df["abstractability"] = "unknown"

    os.makedirs(out_dir, exist_ok=True)
    plot_dir = os.path.join(out_dir, "log_summary")
    os.makedirs(plot_dir, exist_ok=True)

    # ----------- Aggregations -----------
    model_fail = df.groupby("model_name")["num_fail"].sum().sort_values(ascending=False)
    prompt_fail = df.groupby("prompt_idx")["num_fail"].sum().sort_values(ascending=False)
    avg_runs_model = df.groupby("model_name")["total_runs"].mean().sort_values(ascending=False)
    avg_runs_prompt = df.groupby("prompt_idx")["total_runs"].mean().sort_values(ascending=False)
    avg_runs_model_prompt = (
        df.groupby(["model_name", "prompt_idx"])["total_runs"].mean().reset_index()
    )
    avg_runs_size = df.groupby("map_size")["total_runs"].mean().sort_index()
    avg_runs_abstr = df.groupby("abstractability")["total_runs"].mean()

    # Save tables
    model_fail.to_csv(os.path.join(plot_dir, "model_failures.csv"))
    prompt_fail.to_csv(os.path.join(plot_dir, "prompt_failures.csv"))
    avg_runs_model.to_csv(os.path.join(plot_dir, "avg_runs_per_model.csv"))
    avg_runs_prompt.to_csv(os.path.join(plot_dir, "avg_runs_per_prompt.csv"))
    avg_runs_model_prompt.to_csv(os.path.join(plot_dir, "avg_runs_model_prompt.csv"), index=False)
    avg_runs_size.to_csv(os.path.join(plot_dir, "avg_runs_map_size.csv"))
    avg_runs_abstr.to_csv(os.path.join(plot_dir, "avg_runs_abstractability.csv"))

    # ----------- Plots -----------
    plt.figure(figsize=(8, 4))
    model_fail.plot(kind="bar")
    plt.ylabel("Failures")
    plt.title("Total failures by model")
    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, "failures_by_model.png"))
    plt.close()

    plt.figure(figsize=(8, 4))
    prompt_fail.plot(kind="bar")
    plt.ylabel("Failures")
    plt.title("Total failures by prompt")
    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, "failures_by_prompt.png"))
    plt.close()

    plt.figure(figsize=(8, 4))
    avg_runs_model.plot(kind="bar")
    plt.ylabel("Average runs")
    plt.title("Average runs per model")
    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, "avg_runs_per_model.png"))
    plt.close()

    plt.figure(figsize=(8, 4))
    avg_runs_prompt.plot(kind="bar")
    plt.ylabel("Average runs")
    plt.title("Average runs per prompt")
    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, "avg_runs_per_prompt.png"))
    plt.close()

    if not avg_runs_model_prompt.empty:
        pivot = avg_runs_model_prompt.pivot(
            index="model_name", columns="prompt_idx", values="total_runs"
        )
        plt.figure(figsize=(12, max(4, len(pivot) * 0.4)))
        sns.heatmap(pivot, annot=True, fmt=".2f")
        plt.title("Average runs per model/prompt")
        plt.ylabel("Model")
        plt.xlabel("Prompt index")
        plt.tight_layout()
        plt.savefig(os.path.join(plot_dir, "avg_runs_model_prompt_heatmap.png"))
        plt.close()

    plt.figure(figsize=(6, 4))
    avg_runs_size.plot(kind="bar")
    plt.ylabel("Average runs")
    plt.title("Average runs by map size")
    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, "avg_runs_by_map_size.png"))
    plt.close()

    plt.figure(figsize=(6, 4))
    avg_runs_abstr.plot(kind="bar")
    plt.ylabel("Average runs")
    plt.title("Average runs by abstractability")
    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, "avg_runs_by_abstractability.png"))
    plt.close()

    # ----------- Missing combinations -----------
    n_prompts = len(general_config.get("llm", {}).get("compositions", []))
    prompts = list(range(n_prompts))
    maps = df["map_name"].unique()
    models = df["model_name"].unique()
    observed = set(zip(df.model_name, df.prompt_idx, df.map_name))
    missing_records = []
    for m in models:
        for p in prompts:
            for mp in maps:
                if (m, p, mp) not in observed:
                    missing_records.append({
                        "model_name": m,
                        "prompt_idx": p,
                        "map_name": mp,
                    })
    if missing_records:
        df_missing = pd.DataFrame(missing_records)
        df_missing.to_csv(os.path.join(plot_dir, "missing_combinations.csv"), index=False)
    else:
        # create empty file to indicate none missing
        pd.DataFrame(columns=["model_name", "prompt_idx", "map_name"]).to_csv(
            os.path.join(plot_dir, "missing_combinations.csv"), index=False
        )
