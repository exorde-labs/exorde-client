# DataHub
Exorde's data team exclusive repository. 

- Embedded Data Tools (Protocol):

   // HuggingFace contributors
    - Zero-shot classifier ("MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli")
    - Embeddings ("sentence-transformers/all-MiniLM-L6-v2")
    - Advertising detection ("djsull/kobigbird-spam-multi-label")
    - Emotion detection ("j-hartmann/emotion-english-distilroberta-base")
    - Irony detection ("cardiffnlp/twitter-roberta-base-irony")
   // Home made models (https://huggingface.co/ExordeLabs)
    - Sentiment Analysis ("ExordeLabs/SentimentDetection")
    - Age Detection ("ExordeLabs/AgeDetection")
    - Gender Detection ("ExordeLabs/GenderDetection")
    - Hate Speech Detection ("ExordeLabs/HateSpeechDetection")
    
- Internal Data Tools (VM):

   // Dimensionality Reduction Preprocessing:
    - PCA
    - UMAP
    
   // Dimensionality Reduction Pooling:
    - MMCA (Multiview Canonical Correlation Analysis)
    
   // Clustering Preprocessing:
    - K-means
    - HDBSCAN
    - Spectral Clustering
    
   // Clustering Pooling:
    - Agglomerative Clustering
    
   // Topic Modelling Preprocessing:
    - SpaCy's syntaxic structures + similarity matrix
    - YAKE's keyword (+ tf-idf vectorizer) + LDA (Latent Dirichlet Allocation)
    - scraping keyword frequency top 3
    
   // Topic Modelling Pooling:
    - MultiviewKMeans => closest datapoint from the centroid
    
### On test:

   // Clustering:
   
    - Clustering monitoring and reinforcement learning optimization
    - Information extraction for evolution tracking, anomaly detection and overlapping analysis
    
   // Topic Modelling:
   
    - HuggingFace smart summarization
  
    
   
