"""
Preprocessing Pipeline for Vietnamese NLP Intent Classification.

This module implements text preprocessing for Vietnamese natural language input,
including normalization, slang conversion, punctuation removal, emoji removal,
spell correction, and sentence splitting for multi-intent detection.

**Validates: Requirements 14.1-14.7**
"""

import re
from dataclasses import dataclass
from typing import List


# ============================================================================
# SLANG DICTIONARY
# ============================================================================

SLANG_MAP = {
    "k": "không",
    "ko": "không",
    "hok": "không",
    "đc": "được",
    "dc": "được",
    "vs": "với",
    "j": "gì",
    "tks": "cảm ơn",
    "thanks": "cảm ơn",
    "ok": "được",
    "oke": "được"
}


# ============================================================================
# SPELL CORRECTION DICTIONARY
# ============================================================================

SPELL_CORRECTIONS = {
    "khong": "không",
    "duoc": "được",
    "voi": "với",
    "gi": "gì",
    "nha": "nhà",
    "toi": "tôi"
}


# ============================================================================
# SENTENCE SPLITTING KEYWORDS
# ============================================================================

SENTENCE_SPLIT_KEYWORDS = ["và", "rồi", "sau đó", "xong", "tiếp theo", "kế tiếp"]


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class PreprocessedText:
    """Result of preprocessing pipeline."""
    normalized_text: str
    original_text: str
    sentences: List[str]


# ============================================================================
# PREPROCESSING PIPELINE
# ============================================================================

class PreprocessingPipeline:
    """
    Preprocessing pipeline for Vietnamese text input.
    
    This pipeline applies the following steps in order:
    1. Lowercase conversion
    2. Slang normalization
    3. Punctuation removal
    4. Emoji and special character removal
    5. Spell correction
    6. Sentence splitting (for multi-intent)
    
    **Validates: Requirements 14.1-14.7**
    """
    
    def __init__(self):
        """Initialize preprocessing pipeline with dictionaries."""
        self.slang_map = SLANG_MAP
        self.spell_corrections = SPELL_CORRECTIONS
        self.split_keywords = SENTENCE_SPLIT_KEYWORDS
        
        # Compile emoji regex pattern for performance
        self.emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U0001F900-\U0001F9FF"  # supplemental symbols
            "\U0001FA00-\U0001FA6F"  # extended symbols
            "\U00002600-\U000026FF"  # miscellaneous symbols
            "\U0001F170-\U0001F251"  # enclosed characters
            "]+",
            flags=re.UNICODE
        )
    
    def preprocess(self, text: str) -> PreprocessedText:
        """
        Apply full preprocessing pipeline to input text.
        
        Pipeline steps:
        1. Lowercase conversion (Requirement 14.1)
        2. Slang normalization (Requirement 14.3)
        3. Punctuation removal (Requirement 14.2)
        4. Emoji and special character removal (Requirement 14.4)
        5. Spell correction (Requirement 14.6)
        6. Sentence splitting (Requirement 14.7)
        
        Args:
            text: Raw Vietnamese text input
            
        Returns:
            PreprocessedText with normalized text and metadata
            
        Raises:
            TypeError: If input is not a string
        """
        if not isinstance(text, str):
            raise TypeError("Input must be a string")
        
        # Store original text
        original = text
        
        # Apply preprocessing steps
        normalized = text.lower()  # Step 1: Lowercase
        normalized = self._remove_punctuation(normalized)  # Step 2: Punctuation removal
        normalized = self._remove_emoji(normalized)  # Step 3: Emoji removal
        normalized = self.normalize_slang(normalized)  # Step 4: Slang normalization
        normalized = self.correct_spelling(normalized)  # Step 5: Spell correction
        
        # Normalize whitespace
        normalized = ' '.join(normalized.split())
        
        # Step 6: Sentence splitting for multi-intent
        sentences = self.split_sentences(normalized)
        
        return PreprocessedText(
            normalized_text=normalized,
            original_text=original,
            sentences=sentences
        )
    
    def normalize_slang(self, text: str) -> str:
        """
        Convert Vietnamese slang to standard form.
        
        **Validates: Requirement 14.3**
        
        Slang mappings:
        - k/ko/hok → không
        - đc/dc → được
        - vs → với
        - j → gì
        - tks/thanks → cảm ơn
        - ok/oke → được
        
        Args:
            text: Input text with slang
            
        Returns:
            Text with normalized slang
        """
        words = text.split()
        normalized_words = [self.slang_map.get(word, word) for word in words]
        return " ".join(normalized_words)
    
    def split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences based on Vietnamese keywords.
        
        **Validates: Requirement 14.7**
        
        Keywords: và, rồi, sau đó, xong, tiếp theo, kế tiếp
        
        Args:
            text: Input text with multiple intents
            
        Returns:
            List of sentences
        """
        # Start with the full text as a single sentence
        sentences = [text]
        
        # Split by each keyword
        for keyword in self.split_keywords:
            new_sentences = []
            for sentence in sentences:
                # Split by keyword with spaces around it
                parts = sentence.split(f" {keyword} ")
                new_sentences.extend([s.strip() for s in parts if s.strip()])
            sentences = new_sentences
        
        # Return sentences or original text if no splits occurred
        return sentences if sentences else [text]
    
    def correct_spelling(self, text: str) -> str:
        """
        Correct common Vietnamese spelling mistakes.
        
        **Validates: Requirement 14.6**
        
        Common Vietnamese typos:
        - khong → không
        - duoc → được
        - voi → với
        - gi → gì
        - nha → nhà
        - toi → tôi
        
        Args:
            text: Input text with typos
            
        Returns:
            Text with corrected spelling
        """
        words = text.split()
        corrected_words = [self.spell_corrections.get(word, word) for word in words]
        return " ".join(corrected_words)
    
    def _remove_punctuation(self, text: str) -> str:
        """
        Remove punctuation while keeping semantic meaning.
        
        **Validates: Requirement 14.2**
        
        Removes common punctuation but preserves numbers and Vietnamese characters.
        
        Args:
            text: Input text with punctuation
            
        Returns:
            Text without punctuation
        """
        # Define punctuation to remove
        punctuation = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
        
        # Remove punctuation
        for char in punctuation:
            text = text.replace(char, " ")
        
        # Normalize whitespace
        return " ".join(text.split())
    
    def _remove_emoji(self, text: str) -> str:
        """
        Remove emoji and special characters.
        
        **Validates: Requirement 14.4**
        
        Uses regex pattern to remove emoji while preserving Vietnamese characters.
        
        Args:
            text: Input text with emoji
            
        Returns:
            Text without emoji
        """
        # Remove emoji using compiled regex pattern
        text = self.emoji_pattern.sub(r"", text)
        
        # Strip and return
        return text.strip()


# ============================================================================
# STANDALONE FUNCTIONS (for backward compatibility with tests)
# ============================================================================

def lowercase_text(text: str) -> str:
    """
    Convert text to lowercase.
    
    **Validates: Requirement 14.1**
    
    Args:
        text: Input Vietnamese text
        
    Returns:
        Lowercased text
    """
    return text.lower()


def normalize_slang(text: str) -> str:
    """
    Normalize Vietnamese slang to standard form.
    
    **Validates: Requirement 14.3**
    
    Args:
        text: Input text with slang
        
    Returns:
        Text with normalized slang
    """
    pipeline = PreprocessingPipeline()
    return pipeline.normalize_slang(text)


def remove_punctuation(text: str) -> str:
    """
    Remove punctuation while keeping semantic meaning.
    
    **Validates: Requirement 14.2**
    
    Args:
        text: Input text with punctuation
        
    Returns:
        Text without punctuation
    """
    pipeline = PreprocessingPipeline()
    return pipeline._remove_punctuation(text)


def remove_emoji(text: str) -> str:
    """
    Remove emoji and special characters.
    
    **Validates: Requirement 14.4**
    
    Args:
        text: Input text with emoji
        
    Returns:
        Text without emoji
    """
    pipeline = PreprocessingPipeline()
    return pipeline._remove_emoji(text)


def correct_spelling(text: str) -> str:
    """
    Correct common Vietnamese spelling mistakes.
    
    **Validates: Requirement 14.6**
    
    Args:
        text: Input text with typos
        
    Returns:
        Text with corrected spelling
    """
    pipeline = PreprocessingPipeline()
    return pipeline.correct_spelling(text)


def split_sentences(text: str) -> List[str]:
    """
    Split text into sentences based on Vietnamese keywords.
    
    **Validates: Requirement 14.7**
    
    Args:
        text: Input text with multiple intents
        
    Returns:
        List of sentences
    """
    pipeline = PreprocessingPipeline()
    return pipeline.split_sentences(text)
