import random


def weighted_choice(weight_dicts: list[dict[str, float]]) -> str:
    """
    Returns a randomly chosen key, considering weights from multiple dictionaries.

    Args:
        weight_dicts (list[dict[str, float]]): A list of dictionaries where
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
            final_weights[key] *= weight

    # use the combined weights for making the final choice
    total_weight = sum(final_weights.values())
    choice = random.uniform(0, total_weight)
    cumulative_weight = 0

    for option, weight in final_weights.items():
        cumulative_weight += weight
        if choice < cumulative_weight:
            return option

    # This will only execute if the choice exceeds the cumulative weight
    # Return first item if it occurs
    return next(iter(final_weights))
