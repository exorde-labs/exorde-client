from transformers import AutoModel, AutoTokenizer

from argostranslate import package
from typing import cast


def pre_install():
    models = [
        "SamLowe/roberta-base-go_emotions",
        "cardiffnlp/twitter-roberta-base-irony",
        "salesken/query_wellformedness_score",
        "marieke93/MiniLM-evidence-types",
        "alimazhar-110/website_classification",
        # "ExordeLabs/SentimentDetection",
    ]

    def install_hugging_face_models(models):
        for model in models:
            __tokenizer__ = AutoTokenizer.from_pretrained(model)
            model = AutoModel.from_pretrained(model)

    install_hugging_face_models(models)

    package.update_package_index()
    available_packages = package.get_available_packages()
    length = len(available_packages)
    i = 0
    for pkg in available_packages:
        i += 1
        print(
            f" - installing translation module ({i}/{length}) : ({str(pkg)})"
        )

        # cast used until this is merged https://github.com/argosopentech/argos-translate/pull/329
        package.install_from_path(
            cast(package.AvailablePackage, pkg).download()
        )
