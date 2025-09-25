import yaml

def load_config(yaml_file: str) -> dict:
    """Load a YAML configuration file.

    Parameters
    ----------
    yaml_file : str
        Path to the YAML file.

    Returns
    -------
    dict
        Parsed configuration dictionary. Returns an empty dict if the file
        is missing or cannot be parsed.
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
    """Parse string maps from YAML into 2D grids.

    Parameters
    ----------
    yaml_maps : list of str
        One or more string maps where rows are separated by newlines and
        cells are whitespace-separated.

    Returns
    -------
    list of list of list of str
        A list of 2D grids, where each grid is a list of rows and each row
        is a list of cell strings.

    Raises
    ------
    NameError
        If no maps are specified.
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
