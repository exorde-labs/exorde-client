from transformers import AutoModel, AutoTokenizer

if __name__ == "__main__":
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
