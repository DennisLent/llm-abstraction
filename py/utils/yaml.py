import yaml

def load_config(yaml_file: str) -> dict:
    """
    Loading function that can be used for both the general configs and the prompt configurations
    """
    try:
        with open(yaml_file, "r") as file:
            config = yaml.safe_load(file)
            print(f"Successfully loaded {yaml_file}")
            return config
    except FileNotFoundError:
        print(f"Config file {yaml_file} not found")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing yaml file: {e}")
        return {}

def parse_maps(yaml_maps: list) -> list[list[list[str]]]:
    """
    Function that parses the maps from yaml into a python to be in the form list[list[str]].
    The function can take multiple maps and will just return a list.
    """
    if not yaml_maps:
        raise NameError("No maps specified")
    
    parsed_maps = []
    
    for raw_map in yaml_maps:
        lines = raw_map.strip().splitlines()
        grid = []
        for line in lines:
            row = line.strip().split()
            grid.append(row)
        parsed_maps.append(grid)

    return parsed_maps
