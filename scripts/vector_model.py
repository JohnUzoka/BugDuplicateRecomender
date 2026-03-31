# vector_model.py
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from text_preprocessor import TextPreprocessor
import pandas as pd

class VectorSpaceModel:
    def __init__(self, use_tfidf=True, max_features=5000):
        """
        Initialize the vector space model
        
        Parameters:
        - use_tfidf: Use TF-IDF weighting (vs simple term frequency)
        - max_features: Maximum number of features to keep
        """
        self.use_tfidf = use_tfidf
        self.max_features = max_features
        
        # Initialize TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=(1, 2),           # Use unigrams and bigrams
            min_df=2,                      # Ignore terms that appear in <2 docs
            max_df=0.8,                    # Ignore terms in >80% of docs
            sublinear_tf=True              # Use sublinear term frequency scaling
        )
        
        self.preprocessor = TextPreprocessor()
        self.vectors = None
        self.documents = []
        self.document_ids = []
        self.document_titles = {}
        
    def build_model(self, bug_reports, verbose=True):
        """
        Build the vector space model from bug reports
        
        Parameters:
        - bug_reports: List of bug report dictionaries
        - verbose: Print progress information
        """
        if verbose:
            print(f"Building vector space model from {len(bug_reports)} bug reports...")
        
        # Step 1: Preprocess all bug reports
        if verbose:
            print("Step 1: Preprocessing bug reports...")
        
        processed_docs = []
        for report in bug_reports:
            # Combine title and body with weighting
            text = self.preprocessor.combine_text_with_weighting(
                report['title'], 
                report['body']
            )
            
            processed_docs.append(text)
            self.document_ids.append(report['id'])
            self.document_titles[report['id']] = report['title']
        
        self.documents = processed_docs
        
        # Step 2: Create vectors
        if verbose:
            print("Step 2: Creating TF-IDF vectors...")
        
        self.vectors = self.vectorizer.fit_transform(processed_docs)
        
        if verbose:
            print(f"Model built successfully!")
            print(f"  - {self.vectors.shape[0]} documents")
            print(f"  - {self.vectors.shape[1]} features")
            print(f"  - Vocabulary size: {len(self.vectorizer.vocabulary_)}")
        
        return self
    
    def find_similar(self, query_bug, top_k=5, verbose=True):
        """
        Find similar bug reports to a query
        
        Parameters:
        - query_bug: Bug report dictionary
        - top_k: Number of similar reports to return
        - verbose: Print detailed information
        """
        if self.vectors is None:
            raise ValueError("Model not built yet. Call build_model() first.")
        
        # Step 1: Preprocess query
        query_text = self.preprocessor.combine_text_with_weighting(
            query_bug['title'],
            query_bug['body']
        )
        
        # Step 2: Convert to vector
        query_vector = self.vectorizer.transform([query_text])
        
        # Step 3: Calculate cosine similarities
        similarities = cosine_similarity(query_vector, self.vectors)[0]
        
        # Step 4: Get top K indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Step 5: Prepare results
        results = []
        for idx in top_indices:
            similarity_score = similarities[idx]
            if similarity_score > 0:  # Only return if there's some similarity
                doc_id = self.document_ids[idx]
                results.append({
                    'issue_id': doc_id,
                    'title': self.document_titles[doc_id],
                    'similarity': similarity_score,
                    'rank': len(results) + 1
                })
        
        if verbose:
            print(f"\n=== Top {len(results)} Similar Issues ===")
            for result in results:
                print(f"{result['rank']}. Issue #{result['issue_id']}: {result['title'][:60]}...")
                print(f"   Similarity: {result['similarity']:.3f}")
        
        return results
    
    def get_feature_importance(self, top_n=20):
        """
        Get the most important features (words) in the model
        """
        feature_names = self.vectorizer.get_feature_names_out()
        
        # Get average TF-IDF score for each feature
        avg_scores = np.array(self.vectors.mean(axis=0)).flatten()
        
        # Get top features
        top_indices = np.argsort(avg_scores)[-top_n:][::-1]
        
        important_features = []
        for idx in top_indices:
            important_features.append({
                'term': feature_names[idx],
                'avg_tfidf': avg_scores[idx]
            })
        
        return important_features
    
    def analyze_duplicate_candidates(self, new_bug, known_duplicates, top_k=10):
        """
        Analyze how well the model identifies known duplicates
        """
        # Get recommendations
        recommendations = self.find_similar(new_bug, top_k=top_k, verbose=False)
        
        # Check if known duplicates are in recommendations
        known_duplicate_ids = [dup['original_id'] for dup in known_duplicates 
                               if dup['duplicate_id'] == new_bug['id']]
        
        analysis = {
            'new_bug_id': new_bug['id'],
            'new_bug_title': new_bug['title'],
            'known_duplicates': known_duplicate_ids,
            'found_in_recommendations': [],
            'missed_duplicates': [],
            'precision_at_k': {},
            'mrr': 0
        }
        
        # Check each known duplicate
        for dup_id in known_duplicate_ids:
            found = False
            for rank, rec in enumerate(recommendations, 1):
                if rec['issue_id'] == dup_id:
                    found = True
                    analysis['found_in_recommendations'].append({
                        'issue_id': dup_id,
                        'rank': rank,
                        'similarity': rec['similarity']
                    })
                    break
            
            if not found:
                analysis['missed_duplicates'].append(dup_id)
        
        # Calculate MRR
        if analysis['found_in_recommendations']:
            reciprocal_ranks = [1/found['rank'] for found in analysis['found_in_recommendations']]
            analysis['mrr'] = np.mean(reciprocal_ranks)
        
        # Calculate precision at different K values
        for k in [1, 3, 5, 10]:
            relevant_found = sum(1 for rec in recommendations[:k] 
                                 if rec['issue_id'] in known_duplicate_ids)
            analysis['precision_at_k'][k] = relevant_found / k if k > 0 else 0
        
        return analysis

# Test your vector model with dummy data
if __name__ == "__main__":
    from dummy_data import get_dummy_bug_reports
    
    print("=== Testing Vector Space Model ===\n")
    
    # Load dummy data
    bug_reports = get_dummy_bug_reports()
    
    print(f"Loaded {len(bug_reports)} dummy bug reports")
    print()
    
    # Build model
    model = VectorSpaceModel(max_features=100)
    model.build_model(bug_reports, verbose=True)
    
    # Show important features
    print("\n=== Most Important Features ===")
    important = model.get_feature_importance(top_n=10)
    for i, feature in enumerate(important, 1):
        print(f"{i}. '{feature['term']}' (avg TF-IDF: {feature['avg_tfidf']:.3f})")
    
    # Test with a new bug report
    print("\n=== Testing with New Bug Report ===")
    test_bug = {
        'id': 999,
        'title': 'Memory crash on texture loading',
        'body': 'The game crashes when trying to load large texture files due to memory issues'
    }
    
    recommendations = model.find_similar(test_bug, top_k=3)
    