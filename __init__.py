from functools import wraps

import numpy as np


def dismantler_wrapper(func):
    @wraps(func)
    def wrapped(network, *args, **kwargs):
        scores = func(network, *args, **kwargs)
        if not isinstance(scores, np.ndarray):
            scores = np.asarray(scores, dtype=float)

        static_id = network.vertex_properties.get("static_id")
        original_id = network.vertex_properties.get("original_id")
        ranked_nodes = []

        for vertex in network.vertices():
            idx = int(static_id[vertex]) if static_id is not None else int(vertex)
            score = float(scores[idx])
            node_id = int(original_id[vertex]) if original_id is not None else idx
            ranked_nodes.append((node_id, score))

        ranked_nodes.sort(key=lambda item: item[1], reverse=True)
        return ranked_nodes

    return wrapped
