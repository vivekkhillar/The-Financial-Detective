"""
Tokenization Module
==================

This module handles tokenization and preprocessing of raw messy text
for better processing by the LLM model.

COMPETITION COMPLIANCE:
- ✅ NO REGEX USED - All text processing uses simple string operations
- ✅ NO regex used for entity or relationship extraction
- ✅ All entity/relationship extraction is done 100% by LLM in extractor.py

:Author: Vivek Khillar
:Date: 2025-12-24
:Version: 1.0
"""

from typing import List, Dict
from .utils import setup_logger
from .config import Config

logger = setup_logger()


class TextTokenizer:
    """
    Tokenizes and preprocesses raw text using only string operations (NO REGEX).
    """
    
    def __init__(self, chunk_size: int = 4000, chunk_overlap: int = 300):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize the raw text using only string operations (NO REGEX)
        All entity/relationship extraction is done by LLM only.
        """
        if not text:
            return ""
        
        logger.info("Cleaning text using string operations only (minimal cleaning)...")
        
        # Only remove excessive whitespace (more than 2 spaces)
        while '   ' in text:  # Only remove 3+ consecutive spaces
            text = text.replace('   ', '  ')
        
        # Only remove excessive newlines (more than 3 consecutive) 
        while '\n\n\n\n' in text:  
            text = text.replace('\n\n\n\n', '\n\n\n')
        
        # Normalize page separators (simple string replacement) - but keep them
        text = text.replace('---PAGE BREAK---', '--- PAGE BREAK ---')
        text = text.replace('--- PAGE ---', '--- PAGE BREAK ---')
        
        # Only remove leading/trailing whitespace from entire text
        text = text.strip()
        
        logger.info(f"Text cleaned (minimal). Original length: {len(text)} characters")
        return text

    def split_into_sentences(self, text: str) -> List[str]:
        """ Split text into sentences using simple string operations (NO REGEX). """
        
        if not text:
            return []
        
        sentences = []
        current_sentence = []
        i = 0
        
        while i < len(text):
            char = text[i]
            current_sentence.append(char)
            
            # Check for sentence ending punctuation
            if char in '.!?':
                # Look ahead to see if next char is space and following is capital
                if i + 1 < len(text):
                    next_char = text[i + 1]
                    if next_char == ' ':
                        # Check if character after space is capital letter or currency
                        if i + 2 < len(text):
                            char_after_space = text[i + 2]
                            if char_after_space.isupper() or char_after_space in '₹$':
                                # End of sentence found
                                sentence = ''.join(current_sentence).strip()
                                if sentence:
                                    sentences.append(sentence)
                                current_sentence = []
                                i += 1  # Skip the space
                                continue
                    elif next_char == '\n':
                        # Newline after punctuation might indicate sentence end
                        sentence = ''.join(current_sentence).strip()
                        if sentence:
                            sentences.append(sentence)
                        current_sentence = []
                        i += 1  # Skip the newline
                        continue
            
            i += 1
        
        # Add remaining text as a sentence
        if current_sentence:
            sentence = ''.join(current_sentence).strip()
            if sentence:
                sentences.append(sentence)
        
        # Filter out empty sentences
        sentences = [s for s in sentences if s.strip()]
        
        logger.info(f"Split text into {len(sentences)} sentences")
        return sentences

    def chunk_text_by_sentences(self, sentences: List[str]) -> List[Dict[str, any]]:
        """
        Chunk sentences into larger blocks with overlap.
        """
        chunks = []
        current_chunk_sentences = []
        current_chunk_length = 0

        for sentence in sentences:
            sentence_length = len(sentence) + 1  # +1 for space/newline

            if current_chunk_length + sentence_length <= self.chunk_size:
                current_chunk_sentences.append(sentence)
                current_chunk_length += sentence_length
            else:
                # Current sentence doesn't fit, save current chunk
                if current_chunk_sentences:
                    chunk_text = ' '.join(current_chunk_sentences)
                    chunks.append({
                        'text': chunk_text,
                        'size': len(chunk_text),
                        'sentence_count': len(current_chunk_sentences),
                        'chunk_index': len(chunks)
                    })

                # Start new chunk with overlap
                overlap_sentences = []
                overlap_length = 0
                # Add sentences from the end of the previous chunk to create overlap
                for i in range(len(current_chunk_sentences) - 1, -1, -1):
                    s = current_chunk_sentences[i]
                    if overlap_length + len(s) + 1 <= self.chunk_overlap:
                        overlap_sentences.insert(0, s)
                        overlap_length += len(s) + 1
                    else:
                        break
                
                current_chunk_sentences = overlap_sentences + [sentence]
                current_chunk_length = overlap_length + sentence_length
        
        # Add the last chunk if it exists
        if current_chunk_sentences:
            chunk_text = ' '.join(current_chunk_sentences)
            chunks.append({
                'text': chunk_text,
                'size': len(chunk_text),
                'sentence_count': len(current_chunk_sentences),
                'chunk_index': len(chunks)
            })
        
        return chunks

    def chunk_text_by_paragraphs(self, text: str) -> List[Dict[str, any]]:
        """
        Split text into paragraphs based on double newlines.
        """
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        chunks = []
        current_chunk_paragraphs = []
        current_chunk_length = 0

        for paragraph in paragraphs:
            paragraph_length = len(paragraph) + 2  # +2 for double newline

            if current_chunk_length + paragraph_length <= self.chunk_size:
                current_chunk_paragraphs.append(paragraph)
                current_chunk_length += paragraph_length
            else:
                if current_chunk_paragraphs:
                    chunk_text = '\n\n'.join(current_chunk_paragraphs)
                    chunks.append({
                        'text': chunk_text,
                        'size': len(chunk_text),
                        'paragraph_count': len(current_chunk_paragraphs),
                        'chunk_index': len(chunks)
                    })

                overlap_paragraphs = []
                overlap_length = 0
                for i in range(len(current_chunk_paragraphs) - 1, -1, -1):
                    p = current_chunk_paragraphs[i]
                    if overlap_length + len(p) + 2 <= self.chunk_overlap:
                        overlap_paragraphs.insert(0, p)
                        overlap_length += len(p) + 2
                    else:
                        break
                
                current_chunk_paragraphs = overlap_paragraphs + [paragraph]
                current_chunk_length = overlap_length + paragraph_length
        
        if current_chunk_paragraphs:
            chunk_text = '\n\n'.join(current_chunk_paragraphs)
            chunks.append({
                'text': chunk_text,
                'size': len(chunk_text),
                'paragraph_count': len(current_chunk_paragraphs),
                'chunk_index': len(chunks)
            })
        
        return chunks

    def chunk_text_fixed_size(self, text: str) -> List[Dict[str, any]]:
        """
        Chunk text into fixed-size blocks, attempting to break at word boundaries.
        """
        chunks = []
        start = 0
        text_length = len(text)
        chunk_index = 0
        
        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            chunk_text = text[start:end]
            
            # Try to find a space or newline near the end to break cleanly
            if end < text_length:
                # Look for last space or newline in the chunk
                last_space = chunk_text.rfind(' ')
                last_newline = chunk_text.rfind('\n')
                break_point = max(last_space, last_newline)
                
                if break_point != -1 and break_point > self.chunk_size * 0.8:
                    chunk_text = chunk_text[:break_point]
                    end = start + break_point
            
            chunks.append({
                'text': chunk_text.strip(),
                'size': len(chunk_text),
                'chunk_index': chunk_index
            })
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start < 0:
                start = 0
            chunk_index += 1
        
        return chunks

    def tokenize(self, text: str, clean: bool = True, chunk: bool = False, 
                 chunk_strategy: str = "sentence") -> Dict[str, any]:
        """ Main tokenization method.  """
        
        logger.info("Starting tokenization process...")
        
        original_length = len(text)
        
        # Clean text if requested
        if clean:
            text = self.clean_text(text)
        
        result = {
            'original_length': original_length,
            'processed_length': len(text),
            'text': text
        }
        
        # Chunk text if requested
        if chunk:
            logger.info(f"Chunking text using '{chunk_strategy}' strategy...")
            if chunk_strategy == "sentence":
                sentences = self.split_into_sentences(text)
                chunks = self.chunk_text_by_sentences(sentences)
            elif chunk_strategy == "paragraph":
                chunks = self.chunk_text_by_paragraphs(text)
            elif chunk_strategy == "fixed":
                chunks = self.chunk_text_fixed_size(text)
            else:
                logger.warning(f"Unknown chunk strategy: {chunk_strategy}. No chunking applied.")
                chunks = []
            
            result['chunks'] = chunks
            result['chunk_count'] = len(chunks)
            result['chunk_strategy'] = chunk_strategy
            logger.info(f"Tokenization complete: {len(chunks)} chunks created")
        else:
            logger.info("Tokenization complete: text processed without chunking")
        
        return result

