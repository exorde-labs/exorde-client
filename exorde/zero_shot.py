from exorde_data.models import Item
from exorde.models import Classification, Translation


def zero_shot(
    item: Translation, lab_configuration, max_depth=None, depth=0
) -> Classification:
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
    labeldict = lab_configuration["labeldict"]
    classifier = lab_configuration["classifier"]
    text_ = item.translation
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

    keys = list(labeldict[labels_list[0][0]].keys())
    output = classifier(texts, keys, multi_label=False, max_length=32)
    return Classification(
        label=output[0]["labels"][0], score=output[0]["scores"][0]
    )
