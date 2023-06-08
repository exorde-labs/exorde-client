
# Exorde DataHub Repository

Welcome to the DataHub repository! This repository is designed for use by Exorde Network clients who require data processing capabilities such as embedding, classification, and sentiment analysis. It specifically supports spotting and validation tasks related to the Exorde Protocol.

The Exorde Network's primary mission is to generate metadata at scale from a large, unstructured input stream of social media and web public content. To achieve this, we provide a range of machine learning and data tools in this repository. While these tools are built specifically for the Exorde Protocol, they can also be reused and improved upon.

The philosophy of the Exorde Data/ML systems is centered around scalability, portability, efficiency, and state-of-the-art technology. We strive to ensure that our tools are cutting-edge and can handle large-scale data processing tasks. We also encourage an open-source contribution model and plan to introduce bounties for contributions in the future.

## Embedded Data Tools (Protocol)

The following tools have been contributed by the HuggingFace community:

-   Zero-shot classifier: "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli"
-   Embeddings: "sentence-transformers/all-MiniLM-L6-v2"
-   Advertising detection: "djsull/kobigbird-spam-multi-label"
-   Emotion detection: "SamLowe/roberta-base-go_emotions"
-   Irony detection: "cardiffnlp/twitter-roberta-base-irony"

We have also developed the following models under the ExordeLabs organization (available at [https://huggingface.co/ExordeLabs](https://huggingface.co/ExordeLabs)):

-   Sentiment Analysis: "ExordeLabs/SentimentDetection"
-   Age Detection: "ExordeLabs/AgeDetection"
-   Gender Detection: "ExordeLabs/GenderDetection"
-   Hate Speech Detection: "ExordeLabs/HateSpeechDetection"

## Internal Data Tools (VM)

Within the virtual machine environment, we provide various data tools for preprocessing and pooling. These include:

### Dimensionality Reduction Preprocessing:

-   PCA
-   UMAP

### Dimensionality Reduction Pooling:

-   MMCA (Multiview Canonical Correlation Analysis)

### Clustering Preprocessing:

-   K-means
-   HDBSCAN
-   Spectral Clustering

### Clustering Pooling:

-   Agglomerative Clustering

### Topic Modeling Preprocessing:

-   SpaCy's syntaxic structures + similarity matrix
-   YAKE's keyword extraction (using tf-idf vectorizer) + LDA (Latent Dirichlet Allocation)
-   Scraping keyword frequency top 3

### Topic Modeling Pooling:

-   MultiviewKMeans: Finds the closest datapoint from the centroid

## On test:

### Clustering:

-   Clustering monitoring and reinforcement learning optimization
-   Information extraction for evolution tracking, anomaly detection, and overlapping analysis

### Topic Modeling:

-   HuggingFace smart summarization

We hope you find these tools useful in your data science projects. Feel free to explore, contribute, and improve upon them. If you have any questions or suggestions, please don't hesitate to reach out. Happy data processing!
