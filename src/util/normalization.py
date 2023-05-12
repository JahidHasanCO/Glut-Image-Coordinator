import configparser

def normalizeValue(value):
    # Load configuration file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Get initial values for graph_max and graph_min
    graph_max = config.getint('graph', 'max', fallback=1)
    graph_min = config.getint('graph', 'min', fallback=0)
    range = graph_max + graph_min
    norm = round((value * range) - graph_min,4)
    return norm