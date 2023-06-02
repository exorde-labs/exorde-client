import datetime
from exorde_lab.analysis import tag
from exorde_lab.analysis.models import LanguageScore, Sentiment, Embedding, Gender, DescriptedSourceType, SourceType, DescriptedTextType, TextType, DescriptedEmotion, Emotion, DescriptedIrony, Irony, DescriptedAge, Age, Analysis
from exorde_lab.startup import meta_tagger_initialization
from exorde_data.models import Item, CreatedAt, Title, Content, Domain, Url


def test_analysis():
    test_item1 = Item(
        created_at=CreatedAt(
            str(datetime.datetime.now(None).isoformat()) + "Z"
        ),
        title=Title("some title"),
        content=Content("Ceci est un magnifique contenu francais"),
        domain=Domain("test.local"),
        url=Url("https://exorde.network/"),
    )
    test_item2 = Item(
        created_at=CreatedAt(
            str(datetime.datetime.now(None).isoformat()) + "Z"
        ),
        title=Title("some title two"),
        content=Content("This is the bitcoin crash we all waited for"),
        domain=Domain("twitter.com"),
        url=Url("https://twitter.com/ExordeLabs/status/1664647166189551618"),
    )

    list_item = [test_item1, test_item2]

    output = meta_tagger_initialization()
    # inputs are texts, nlp, device, mappings
    analysis_output_object = tag(list_item, output["nlp"], output["device"], output["mappings"])

    for e in analysis_output_object:
        assert isinstance(e, Analysis)
        print()
        print(e.langage_score)
        print(e.sentiment)
        assert(e.sentiment is not None)
