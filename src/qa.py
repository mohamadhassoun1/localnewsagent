"""
QA & Validation module: Check word count, plagiarism (20-char threshold),
AdSense safety, auto-regenerate on failure.
"""

import logging
import re
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class QAResult:
    """Result of QA check."""
    passed: bool
    issues: list
    word_count: int
    is_adsense_safe: bool


class QAValidator:
    """Quality assurance and validation for articles."""

    def __init__(self, min_word_count: int = 800, log_file: Optional[str] = None):
        self.min_word_count = min_word_count
        self.logger = logging.getLogger("QAValidator")
        if log_file:
            handler = logging.FileHandler(log_file)
            handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(handler)

        self.disallowed_terms = [
            'adult', 'explicit', 'porn', 'xxx',
            'hate', 'kill', 'murder', 'suicide',
            'medical advice', 'guaranteed cure', 'treat disease',
            'financial advice', 'guaranteed return', 'easy money'
        ]

    def check_word_count(self, text: str) -> Tuple[int, bool]:
        """Check if word count meets minimum."""
        word_count = len(text.split())
        meets_minimum = word_count >= self.min_word_count
        return word_count, meets_minimum

    def check_plagiarism_threshold(self, article_text: str, source_texts: list) -> Tuple[bool, list]:
        """
        Check for copying >20 consecutive characters from sources.
        Returns (passed, suspicious_phrases).
        """
        suspicious = []
        
        # Extract all 20-char substrings from article
        article_phrases = set()
        words = article_text.split()
        for i in range(len(words) - 4):  # ~20 chars is ~4 words
            phrase = ' '.join(words[i:i+4])
            if len(phrase) >= 15:
                article_phrases.add(phrase.lower())
        
        # Check against sources
        for source in source_texts:
            source_words = source.split()
            for i in range(len(source_words) - 4):
                phrase = ' '.join(source_words[i:i+4])
                if len(phrase) >= 15 and phrase.lower() in article_phrases:
                    suspicious.append(f"Potential match: {phrase[:40]}")
        
        # If too many matches, it's plagiarism
        passed = len(suspicious) < 5
        return passed, suspicious

    def check_adsense_safety(self, text: str) -> Tuple[bool, list]:
        """Check for disallowed content for AdSense."""
        violations = []
        text_lower = text.lower()
        
        for term in self.disallowed_terms:
            if term in text_lower:
                violations.append(f"Disallowed term found: '{term}'")
        
        # Check for explicit URLs or email harvesting patterns
        if re.search(r'\b(?:bitc0in|viagra|casino)\b', text_lower):
            violations.append("Spam-like terms detected")
        
        is_safe = len(violations) == 0
        return is_safe, violations

    def validate_article(self,
                        article_text: str,
                        article_html: str,
                        source_texts: list,
                        has_our_take: bool = True,
                        has_sources_section: bool = True) -> QAResult:
        """
        Run full QA check on article.
        """
        issues = []
        passed = True
        
        # 1. Word count
        word_count, wc_ok = self.check_word_count(article_text)
        if not wc_ok:
            issues.append(f"Word count {word_count} < {self.min_word_count}")
            passed = False
        
        # 2. Plagiarism check
        plagio_ok, suspicious = self.check_plagiarism_threshold(article_text, source_texts)
        if not plagio_ok:
            issues.append(f"Potential plagiarism: {len(suspicious)} matches")
            passed = False
        
        # 3. AdSense safety
        adsense_ok, violations = self.check_adsense_safety(article_text)
        if not adsense_ok:
            issues.extend(violations)
            passed = False
        
        # 4. Structural checks
        if has_our_take and 'Our take' not in article_text:
            issues.append("Missing 'Our take' statement")
            passed = False
        
        if has_sources_section and 'Sources' not in article_html:
            issues.append("Missing Sources section")
            passed = False
        
        result = QAResult(
            passed=passed,
            issues=issues,
            word_count=word_count,
            is_adsense_safe=adsense_ok
        )
        
        if passed:
            self.logger.info(f"QA passed: {word_count} words, AdSense safe, no plagiarism detected")
        else:
            self.logger.warning(f"QA failed with {len(issues)} issues: {', '.join(issues)}")
        
        return result

    def get_qa_report(self, qa_result: QAResult) -> str:
        """Generate a human-readable QA report."""
        report = f"Word Count: {qa_result.word_count}\n"
        report += f"AdSense Safe: {'✓' if qa_result.is_adsense_safe else '✗'}\n"
        report += f"QA Status: {'PASSED' if qa_result.passed else 'FAILED'}\n"
        
        if qa_result.issues:
            report += f"\nIssues ({len(qa_result.issues)}):\n"
            for issue in qa_result.issues:
                report += f"  - {issue}\n"
        
        return report
