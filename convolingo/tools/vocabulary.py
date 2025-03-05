import logging
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
import os
from datetime import datetime

from convolingo.utils.config import config, VOCABULARY_TOOL_ID

# Set up logging
logger = logging.getLogger(__name__)

class VocabularyTool:
    """Tool for managing vocabulary words during language learning sessions"""
    
    def __init__(self):
        """Initialize the vocabulary tool"""
        self.tool_id = VOCABULARY_TOOL_ID
        self.vocabulary_file = config.history_dir / "vocabulary.json"
        self.vocabulary = self._load_vocabulary()
    
    def _load_vocabulary(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load vocabulary from file or create new if doesn't exist"""
        if not self.vocabulary_file.exists():
            return {}
            
        try:
            with open(self.vocabulary_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading vocabulary: {e}")
            return {}
    
    def _save_vocabulary(self) -> bool:
        """Save vocabulary to file"""
        try:
            with open(self.vocabulary_file, 'w', encoding='utf-8') as f:
                json.dump(self.vocabulary, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving vocabulary: {e}")
            return False
    
    def handle_tool_call(self, text: str) -> Dict[str, Any]:
        """
        Handle a vocabulary tool call
        
        Args:
            text: Text containing vocabulary request
            
        Returns:
            Dict containing response data
        """
        logger.info(f"Vocabulary tool called with: {text}")
        
        # In a real implementation, this would parse the text and perform
        # the requested action. For now, it just logs the call.
        return {
            "success": True,
            "message": f"Processed vocabulary request: {text}",
            "tool_id": self.tool_id
        }
    
    def add_word(self, language: str, word: str, 
                translation: str, notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a word to the vocabulary
        
        Args:
            language: The language of the word
            word: The word to add
            translation: The translation of the word
            notes: Optional notes about the word
            
        Returns:
            Dict containing response data
        """
        if language not in self.vocabulary:
            self.vocabulary[language] = []
            
        # Create word entry
        word_entry = {
            "word": word,
            "translation": translation,
            "added_at": datetime.now().isoformat(),
            "review_count": 0,
            "last_reviewed": None
        }
        
        if notes:
            word_entry["notes"] = notes
            
        # Add to vocabulary
        self.vocabulary[language].append(word_entry)
        
        # Save vocabulary
        self._save_vocabulary()
        
        return {
            "success": True,
            "message": f"Added word '{word}' to {language} vocabulary",
            "word_entry": word_entry
        }
    
    def list_words(self, language: str) -> Dict[str, Any]:
        """
        List all words in a language
        
        Args:
            language: The language to list words for
            
        Returns:
            Dict containing response data with word list
        """
        if language not in self.vocabulary:
            return {
                "success": True,
                "message": f"No words found for {language}",
                "words": []
            }
            
        return {
            "success": True,
            "message": f"Found {len(self.vocabulary[language])} words for {language}",
            "words": self.vocabulary[language]
        }
    
    def search_word(self, language: str, query: str) -> Dict[str, Any]:
        """
        Search for a word in the vocabulary
        
        Args:
            language: The language to search in
            query: The search query
            
        Returns:
            Dict containing response data with search results
        """
        if language not in self.vocabulary:
            return {
                "success": True,
                "message": f"No words found for {language}",
                "results": []
            }
            
        # Simple case-insensitive search
        results = [
            word for word in self.vocabulary[language]
            if query.lower() in word["word"].lower() or 
               query.lower() in word["translation"].lower()
        ]
        
        return {
            "success": True,
            "message": f"Found {len(results)} matches for '{query}' in {language}",
            "results": results
        } 