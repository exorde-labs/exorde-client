from madtypes import Schema, Annotation


class Sentiment(str, metaclass=Annotation):
    description = "Measure of post sentiment from negative to positive (-1 = negative, +1 = positive, 0 = neutral)"
    annotation = float


class Embedding(list, metaclass=Annotation):
    description = "Vector/numerical representation of the translated content (field: translation), produced by a NLP encoder model"
    annotation = list[float]


class LanguageScore(float, metaclass=Annotation):
    description = "Readability score of the text"
    annotation = float


class Gender(Schema):
    male: float
    female: float


class DescriptedGender(Gender, metaclass=Annotation):
    description = "Probable gender (female or male) of the author"
    annotation = Gender


class SourceType(Schema):
    social: float
    computers: float
    games: float
    business: float
    streaming: float
    ecommerce: float
    forums: float
    photography: float
    travel: float
    adult: float
    law: float
    sports: float
    education: float
    food: float
    health: float


class DescriptedSourceType(SourceType, metaclass=Annotation):
    description = "Category of the source that has produced the post"
    annotation = SourceType


class TextType(Schema):
    assumption: float
    anecdote: float
    none: float
    definition: float
    testimony: float
    other: float
    study: float


class DescriptedTextType(TextType, metaclass=Annotation):
    description = "Type (category) of the post (article, etc)"
    annotation = TextType


class Emotion(Schema):
    love: float
    admiration: float
    joy: float
    approval: float
    caring: float
    excitement: float
    gratitude: float
    desire: float
    anger: float
    optimism: float
    disapproval: float
    grief: float
    annoyance: float
    pride: float
    curiosity: float
    neutral: float
    disgust: float
    disappointment: float
    realization: float
    fear: float
    relief: float
    confusion: float
    remorse: float
    embarrassement: float
    surprise: float
    sadness: float
    nervousness: float


class DescriptedEmotion(Emotion, metaclass=Annotation):
    description = ""
    annotation = Emotion


class Irony(Schema):
    irony: float
    non_irony: float


class DescriptedIrony(Irony, metaclass=Annotation):
    description = "Measure of how much a post is ironic (in %)"
    annotation = Irony


class Age(Schema):
    bellow_twenty: float
    twenty_thirty: float
    thirty_forty: float
    forty_more: float


class DescriptedAge(Age, metaclass=Annotation):
    description = "Measure author's age"
    annotation = Age


class Analysis(Schema):
    langage_score: LanguageScore
    sentiment: Sentiment
    embedding: Embedding
    gender: DescriptedGender
    source_type: DescriptedSourceType
    text_type: DescriptedTextType
    emotion: DescriptedEmotion
    irony: DescriptedIrony
    age: DescriptedAge
