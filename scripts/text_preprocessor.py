# text_preprocessor.py
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
import string
import ssl

# #region agent log
import json, time, os
_DBG_LOG = "/Users/lesliecoffie/school projects/BugDuplicateRecomender/.cursor/debug-8f82cd.log"
def _dbg(msg, data=None, hyp=None):
    entry = {"sessionId":"8f82cd","timestamp":int(time.time()*1000),"location":"text_preprocessor.py","message":msg,"data":data or {},"hypothesisId":hyp or ""}
    with open(_DBG_LOG, "a") as f: f.write(json.dumps(entry)+"\n")
# #endregion

class TextPreprocessor:
    def __init__(self):
        # Bypass SSL verification for NLTK downloads (macOS Python cert issue)
        _original_https_context = ssl._create_default_https_context
        ssl._create_default_https_context = ssl._create_unverified_context

        # Download required NLTK data (run once)
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            nltk.download('punkt_tab')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet')

        ssl._create_default_https_context = _original_https_context
        
        # #region agent log
        _dbg("NLTK downloads complete, checking resources", {
            "punkt_tab": self._resource_exists('tokenizers/punkt_tab'),
            "stopwords": self._resource_exists('corpora/stopwords'),
            "wordnet": self._resource_exists('corpora/wordnet'),
        }, "verify")
        # #endregion

        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Add custom stop words specific to bug reports
        self.custom_stops = {'bug', 'issue', 'error', 'problem', 'fix', 'please', 'thanks'}
        self.stop_words.update(self.custom_stops)

    # #region agent log
    @staticmethod
    def _resource_exists(path):
        try:
            nltk.data.find(path)
            return True
        except LookupError:
            return False
    # #endregion
    
    def preprocess(self, text, verbose=False):
        """
        Main preprocessing pipeline
        Returns cleaned, normalized text
        """
        if verbose:
            print(f"Original text: {text[:100]}...")
        
        # Step 1: Convert to lowercase
        text = text.lower()
        
        # Step 2: Remove code blocks (often contain noise)
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'`.*?`', '', text)  # Remove inline code
        
        # Step 3: Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text)
        
        # Step 4: Remove special characters but keep important ones
        # Keep letters, spaces, and some special chars that might be important
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        # Step 5: Remove extra whitespace
        text = ' '.join(text.split())
        
        # Step 6: Tokenization
        tokens = nltk.word_tokenize(text)
        
        if verbose:
            print(f"Tokens: {tokens[:10]}...")
        
        # Step 7: Remove stopwords and lemmatize
        processed_tokens = []
        for token in tokens:
            # Remove short tokens and stopwords
            if len(token) > 2 and token not in self.stop_words:
                # Lemmatize (reduce to root form)
                lemma = self.lemmatizer.lemmatize(token)
                processed_tokens.append(lemma)
        
        if verbose:
            print(f"Processed tokens: {processed_tokens[:10]}...")
        
        # Step 8: Join back into text
        processed_text = ' '.join(processed_tokens)
        
        if verbose:
            print(f"Final text: {processed_text[:100]}...")
        
        return processed_text
    
    def combine_text_with_weighting(self, title, body, title_weight=3):
        """
        Combine title and body with title weighting
        Title is repeated to give it more importance
        """
        # Preprocess title and body separately
        title_processed = self.preprocess(title)
        body_processed = self.preprocess(body)
        
        # Repeat title for weighting
        weighted_title = (title_processed + ' ') * title_weight
        
        # Combine
        combined = weighted_title + body_processed
        
        return combined.strip()
    
    def batch_preprocess(self, bug_reports, verbose=False):
        """
        Preprocess a batch of bug reports
        """
        processed_reports = []
        
        for report in bug_reports:
            combined_text = self.combine_text_with_weighting(
                report['title'], 
                report['body']
            )
            
            processed_reports.append({
                'id': report['id'],
                'text': combined_text,
                'original_title': report['title']
            })
            
            if verbose:
                print(f"\n--- Processing Bug #{report['id']} ---")
                print(f"Title: {report['title']}")
                print(f"Processed length: {len(combined_text)} chars")
        
        return processed_reports

# Test your preprocessor with dummy data
if __name__ == "__main__":
    # Quick test
    preprocessor = TextPreprocessor()
    
    test_text = "Game crashes when loading large textures!!! Please fix this bug."
    print("Testing preprocessing:")
    print(f"Input: {test_text}")
    print(f"Output: {preprocessor.preprocess(test_text)}")
    
    # Test with a bug report
    test_report = {
        'title': "Game crashes when loading large textures",
        'body': "When trying to load a texture larger than 4096x4096 pixels, the game crashes with 'out of memory' error."
    }
    
    combined = preprocessor.combine_text_with_weighting(test_report['title'], test_report['body'])
    print(f"\nCombined with weighting: {combined}")
