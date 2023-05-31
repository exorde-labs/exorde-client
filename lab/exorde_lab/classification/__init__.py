def zero_shot(item, labeldict, classifier, max_depth=None, depth=0):
    """
    Perform zero-shot classification on the input text using a pre-trained language model.

    Args:
    - text (str): The input text to be classified.
    - labeldict (dict): A dictionary that maps each label to its corresponding sub-labels, or None if the label has no sub-labels.
    - path (list, optional): A list containing the path of labels from the root to the current label. Defaults to None.
    - depth (int, optional): The current depth in the label hierarchy. Defaults to 0.
    - max_depth (int, optional): The maximum depth in the label hierarchy to explore. Defaults to None (i.e., explore the entire hierarchy).

    Returns:
    - path (list): A list containing the path of labels from the root to the predicted label. If the label hierarchy was not explored fully and the max_depth parameter was set, the path may not be complete.
    """
    text_ = item.content
    texts = [text_]
    keys = list(labeldict.keys())
    output = classifier(texts, keys, multi_label=False, max_length=32)

    labels_list = list()

    for i in range(len(texts)):
        labels = [
            output[i]["labels"][x]
            for x in range(len(output[i]["labels"]))
            if output[i]["scores"][x] > 0.1
        ]
        labels_list.append(labels)

    depth += 1
    if depth == max_depth:
        _labels = labels
        return labels
    else:
        output_list = list()
        keys = list(labeldict[labels_list[0][0]].keys())
        output = classifier(
                texts, keys, multi_label=False, max_length=32
            )
        item.classification = Classification(Topic(output[0]["labels"][0]), Weight(output[0]["scores"][0]))
    return item
