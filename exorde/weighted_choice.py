import random
from typing import List, Dict


def weighted_choice(weight_dicts: List[Dict[str, float]]) -> str:
    """
    Returns a randomly chosen key, considering weights from multiple dictionaries.

    Args:
        weight_dicts (List[Dict[str, float]]): A list of dictionaries where
                                               each dictionary represents a different
                                               feature's weights.

    Returns:
        str: A randomly chosen key.
    """
    # initialize final weights dictionary with keys from the first weight dictionary
    final_weights = {key: 1.0 for key in weight_dicts[0].keys()}

    # multiply weights for each key from all weight dictionaries
    for weights in weight_dicts:
        for key, weight in weights.items():
            final_weights[key] *= weights.get(key, 1.0)

    # use the combined weights for making the final choice
    total_weight = sum(final_weights.values())
    choice = random.uniform(0, total_weight)
    cumulative_weight = 0

    for option, weight in final_weights.items():
        cumulative_weight += weight
        if choice < cumulative_weight:
            return option

    # This will only execute if the choice exceeds the cumulative weight
    # Return the first item if it occurs
    return next(iter(final_weights))


# Example usage:
if __name__ == "__main__":
    layer1 = {"A": 0.5, "B": 0.7, "C": 0.3}
    layer2 = {"A": 0, "B": 0.4, "C": 0}
    layer3 = {"A": 0.9, "B": 0.5, "C": 0.1}

    weights = [layer1, layer2, layer3]

    num_samples = 10
    for _ in range(num_samples):
        choice = weighted_choice(weights)
        print(f"Chosen: {choice}")
