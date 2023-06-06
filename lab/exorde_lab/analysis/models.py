from madtypes import MadType


class Sentiment(float, metaclass=MadType):
    description = "Measure of post sentiment from negative to positive (-1 = negative, +1 = positive, 0 = neutral)"
    annotation = float


class Embedding(list, metaclass=MadType):
    description = "Vector/numerical representation of the translated content (field: translation), produced by a NLP encoder model"
    annotation = list[float]


class LanguageScore(float, metaclass=MadType):
    description = "Readability score of the text"
    annotation = float


class Gender(dict, metaclass=MadType):
    male: float
    female: float
    description = "Probable gender (female or male) of the author"


class SourceType(dict, metaclass=MadType):
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
    news: float
    description = "Category of the source that has produced the post"


class TextType(dict, metaclass=MadType):
    assumption: float
    anecdote: float
    none: float
    definition: float
    testimony: float
    other: float
    study: float
    description = "Type (category) of the post (article, etc)"


class Emotion(dict, metaclass=MadType):
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


class Irony(dict, metaclass=MadType):
    irony: float
    non_irony: float
    description = "Measure of how much a post is ironic (in %)"


class Age(dict, metaclass=MadType):
    below_twenty: float
    twenty_thirty: float
    thirty_forty: float
    forty_more: float
    description = "Measure author's age"


class Analysis(dict, metaclass=MadType):
    language_score: LanguageScore
    sentiment: Sentiment
    embedding: Embedding
    gender: Gender
    source_type: SourceType
    text_type: TextType
    emotion: Emotion
    irony: Irony
    age: Age
