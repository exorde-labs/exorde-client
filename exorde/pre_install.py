from transformers import AutoModel, AutoTokenizer

from argostranslate import package
from typing import cast
import logging
from wtpsplit import WtP
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, pipeline
from huggingface_hub import hf_hub_download
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

print("importing wtpsplit....")
wtp = WtP("wtp-canine-s-1l")

models = [
    "SamLowe/roberta-base-go_emotions",
    "cardiffnlp/twitter-roberta-base-irony",
    "salesken/query_wellformedness_score",
    "marieke93/MiniLM-evidence-types",
    "alimazhar-110/website_classification"
]

def install_hugging_face_models(models):
    for model in models:
        __tokenizer__ = AutoTokenizer.from_pretrained(model)
        model = AutoModel.from_pretrained(model)

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
install_hugging_face_models(models)

### install (pre install) models target for English, and exclude low frequency ones to not overload the isntall
def is_english_target(s):
    return '→ English' in s

langs_to_exclude_from_preinstall = ["Azerbaijani", "Catalan", "Esperanto", "Persian"]

def is_to_exclude(s):
    for lang in langs_to_exclude_from_preinstall:
        if lang in s:
            return True
    return False

package.update_package_index()
available_packages = package.get_available_packages()
length = len(available_packages)
i = 0
installed_packages = 0
for pkg in available_packages:
    i += 1
    
    if( is_english_target(str(pkg)) and not is_to_exclude(str(pkg)) ):
        print(
            f" - installing translation module ({i}/{length}) : ({str(pkg)})"
        )

        # cast used until this is merged https://github.com/argosopentech/argos-translate/pull/329
        package.install_from_path(
            cast(package.AvailablePackage, pkg).download()
        )
        installed_packages += 1
logging.info(f"Installed Argos Lang packages: {str(installed_packages)}")
