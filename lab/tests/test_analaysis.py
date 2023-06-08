import os

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
from exorde_lab.analysis import tag
from exorde_lab.analysis.models import Analysis
from exorde_lab.startup import meta_tagger_initialization


def test_analysis():
    test_item1: str = "As I progress through implementing the different methods of calculating cosine, I will be comparing them from two perspectives: runtime and accuracy."
    test_item2: str = "For runtime, each function is executed 100 million times using a range of input values and it is timed using time.h's clock function."
    list_item = [test_item1, test_item2]

    output = meta_tagger_initialization()
    # inputs are texts, nlp, device, mappings
    analysis_output_object = tag(
        list_item, output["nlp"], output["device"], output["mappings"]
    )

    for e in analysis_output_object:
        assert isinstance(e, Analysis)
        print()
        print(e.langage_score)
        print(e.sentiment)
        assert e.sentiment is not None
