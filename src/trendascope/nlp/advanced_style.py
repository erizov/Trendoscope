"""
Advanced style analyzer with deep pattern recognition.
Extracts multi-level writing patterns from blog posts.
"""
from typing import List, Dict, Any, Set
import re
from collections import Counter, defaultdict


class AdvancedStyleAnalyzer:
    """Deep style learning from blog posts."""
    
    def __init__(self):
        """Initialize advanced style analyzer."""
        self.min_phrase_length = 3
        self.max_phrase_length = 15
    
    def extract_deep_patterns(
        self,
        posts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Extract multi-level style patterns.
        
        Args:
            posts: List of blog posts
        
        Returns:
            Dictionary with deep style patterns
        """
        return {
            # Structural patterns
            "opening_patterns": self._extract_openings(posts),
            "closing_patterns": self._extract_closings(posts),
            "paragraph_flow": self._analyze_paragraph_flow(posts),
            
            # Rhetorical devices
            "rhetorical_questions": self._find_rhetorical_questions(posts),
            "irony_markers": self._detect_irony_markers(posts),
            "historical_references": self._extract_historical_refs(posts),
            
            # Lexical preferences
            "preferred_adjectives": self._top_adjectives(posts),
            "transition_words": self._transition_patterns(posts),
            "signature_expressions": self._signature_phrases(posts),
            
            # Argumentation style
            "argument_patterns": self._analyze_arguments(posts),
            "counterpoint_markers": self._counterpoint_patterns(posts),
            "emphasis_techniques": self._emphasis_patterns(posts),
            
            # Statistics
            "avg_paragraph_count": self._avg_paragraphs(posts),
            "avg_sentence_per_paragraph": self._avg_sentences_per_para(posts),
            "punctuation_style": self._punctuation_analysis(posts),
        }
    
    def _extract_openings(self, posts: List[Dict]) -> List[str]:
        """Extract typical post opening patterns."""
        openings = []
        
        for post in posts:
            text = post.get('text', '') or post.get('text_plain', '')
            if not text:
                continue
            
            # Get first 1-2 sentences (up to 200 chars)
            first_part = text[:200]
            sentences = re.split(r'[.!?]+', first_part)
            
            if sentences:
                opening = sentences[0].strip()
                if len(opening) > 20:  # Meaningful opening
                    openings.append(opening)
        
        # Cluster similar openings
        return self._cluster_patterns(openings, max_results=10)
    
    def _extract_closings(self, posts: List[Dict]) -> List[str]:
        """Extract typical post closing patterns."""
        closings = []
        
        for post in posts:
            text = post.get('text', '') or post.get('text_plain', '')
            if not text:
                continue
            
            # Get last 1-2 sentences
            last_part = text[-300:]
            sentences = re.split(r'[.!?]+', last_part)
            
            if sentences:
                # Get last non-empty sentence
                for sentence in reversed(sentences):
                    closing = sentence.strip()
                    if len(closing) > 20:
                        closings.append(closing)
                        break
        
        return self._cluster_patterns(closings, max_results=10)
    
    def _analyze_paragraph_flow(self, posts: List[Dict]) -> Dict[str, Any]:
        """Analyze paragraph structure and flow."""
        para_counts = []
        para_lengths = []
        
        for post in posts:
            text = post.get('text', '') or post.get('text_plain', '')
            if not text:
                continue
            
            # Split by double newlines
            paragraphs = re.split(r'\n\s*\n', text)
            paragraphs = [p.strip() for p in paragraphs if p.strip()]
            
            para_counts.append(len(paragraphs))
            para_lengths.extend([len(p) for p in paragraphs])
        
        return {
            "avg_paragraphs": sum(para_counts) / len(para_counts) if para_counts else 0,
            "avg_paragraph_length": sum(para_lengths) / len(para_lengths) if para_lengths else 0,
            "typical_paragraph_count": self._mode(para_counts) if para_counts else 0,
        }
    
    def _find_rhetorical_questions(self, posts: List[Dict]) -> List[str]:
        """Find rhetorical questions."""
        questions = []
        
        for post in posts:
            text = post.get('text', '') or post.get('text_plain', '')
            if not text:
                continue
            
            # Find sentences ending with ?
            sentences = re.split(r'[.!?]+', text)
            for i, sentence in enumerate(sentences):
                if i < len(text) and text[text.find(sentence) + len(sentence):].startswith('?'):
                    question = sentence.strip()
                    if len(question) > 10:
                        questions.append(question + '?')
        
        # Return most common questions
        if questions:
            return [q for q, _ in Counter(questions).most_common(15)]
        return []
    
    def _detect_irony_markers(self, posts: List[Dict]) -> Dict[str, Any]:
        """Detect ironic expressions and sarcasm markers."""
        markers = {
            "quotation_usage": 0,
            "parenthetical_comments": [],
            "contrast_markers": [],
            "hyperbolic_expressions": [],
        }
        
        total_posts = len(posts)
        
        for post in posts:
            text = post.get('text', '') or post.get('text_plain', '')
            if not text:
                continue
            
            # Count quotation marks (ironic quotes)
            if '"' in text or '«' in text or '"' in text:
                markers["quotation_usage"] += 1
            
            # Find parenthetical comments
            parentheticals = re.findall(r'\([^)]{5,50}\)', text)
            markers["parenthetical_comments"].extend(parentheticals)
            
            # Contrast markers
            contrasts = re.findall(
                r'\b(но|однако|зато|впрочем|тем не менее)\b[^.!?]{10,100}',
                text,
                re.IGNORECASE
            )
            markers["contrast_markers"].extend(contrasts)
        
        # Calculate percentages and top examples
        markers["quotation_usage_pct"] = (markers["quotation_usage"] / total_posts * 100) if total_posts else 0
        markers["parenthetical_comments"] = list(set(markers["parenthetical_comments"]))[:10]
        markers["contrast_markers"] = [c for c, _ in Counter(markers["contrast_markers"]).most_common(10)]
        
        return markers
    
    def _extract_historical_refs(self, posts: List[Dict]) -> List[str]:
        """Extract historical references and parallels."""
        refs = []
        
        # Patterns for historical references
        patterns = [
            r'\b(история|исторически|в истории)\b.{10,100}',
            r'\b\d{4}\s*год[уа]?\b.{10,100}',
            r'\b(СССР|Советск|царск|империи)\b.{10,100}',
            r'\b(Петр|Ленин|Сталин|Горбачев|Ельцин)\b.{10,100}',
        ]
        
        for post in posts:
            text = post.get('text', '') or post.get('text_plain', '')
            if not text:
                continue
            
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                refs.extend(matches)
        
        # Return unique references
        return list(set(refs))[:20]
    
    def _top_adjectives(self, posts: List[Dict]) -> List[str]:
        """Extract most used adjectives."""
        # Russian adjective patterns (simplified)
        adj_patterns = [
            r'\b\w+(ный|ной|ная|ное|ные|ских|ского|ской)\b',
            r'\b\w+(кий|кой|кая|кое|кие)\b',
        ]
        
        adjectives = []
        
        for post in posts:
            text = post.get('text', '') or post.get('text_plain', '')
            if not text:
                continue
            
            for pattern in adj_patterns:
                matches = re.findall(pattern, text.lower())
                adjectives.extend(matches)
        
        # Filter out common ones
        common_adj = {'которые', 'этого', 'который', 'такой'}
        filtered = [adj for adj in adjectives if adj not in common_adj and len(adj) > 5]
        
        return [adj for adj, _ in Counter(filtered).most_common(30)]
    
    def _transition_patterns(self, posts: List[Dict]) -> List[str]:
        """Extract transition words and phrases."""
        transitions = []
        
        transition_markers = [
            r'\b(Итак|Таким образом|В итоге|В результате)\b',
            r'\b(Во-первых|Во-вторых|В-третьих|Наконец)\b',
            r'\b(С одной стороны|С другой стороны)\b',
            r'\b(Более того|К тому же|Кроме того)\b',
            r'\b(Следовательно|Поэтому|Отсюда)\b',
        ]
        
        for post in posts:
            text = post.get('text', '') or post.get('text_plain', '')
            if not text:
                continue
            
            for pattern in transition_markers:
                matches = re.findall(pattern, text, re.IGNORECASE)
                transitions.extend(matches)
        
        return [t for t, _ in Counter(transitions).most_common(15)]
    
    def _signature_phrases(self, posts: List[Dict]) -> List[str]:
        """Extract signature phrases unique to author."""
        all_phrases = []
        
        for post in posts:
            text = post.get('text', '') or post.get('text_plain', '')
            if not text:
                continue
            
            # Extract n-grams
            words = text.split()
            for n in range(3, 6):  # 3-5 word phrases
                for i in range(len(words) - n + 1):
                    phrase = ' '.join(words[i:i+n])
                    # Clean up
                    phrase = re.sub(r'[^\w\s-]', '', phrase).strip()
                    if len(phrase) > 15 and len(phrase) < 60:
                        all_phrases.append(phrase.lower())
        
        # Find phrases that appear multiple times
        phrase_counts = Counter(all_phrases)
        signature = [
            phrase for phrase, count in phrase_counts.items()
            if count >= 2  # Appears at least twice
        ]
        
        return signature[:25]
    
    def _analyze_arguments(self, posts: List[Dict]) -> Dict[str, Any]:
        """Analyze argumentation patterns."""
        patterns = {
            "uses_examples": 0,
            "uses_statistics": 0,
            "uses_quotes": 0,
            "uses_analogies": 0,
        }
        
        for post in posts:
            text = post.get('text', '') or post.get('text_plain', '')
            if not text:
                continue
            
            # Examples
            if re.search(r'\b(например|к примеру|допустим)\b', text, re.IGNORECASE):
                patterns["uses_examples"] += 1
            
            # Statistics/numbers
            if re.search(r'\d+\s*(процент|%|человек|тысяч)', text):
                patterns["uses_statistics"] += 1
            
            # Quotes
            if '"' in text or '«' in text:
                patterns["uses_quotes"] += 1
            
            # Analogies
            if re.search(r'\b(как|словно|подобно|аналогично)\b', text, re.IGNORECASE):
                patterns["uses_analogies"] += 1
        
        total = len(posts)
        return {
            k: f"{v}/{total} ({v/total*100:.0f}%)"
            for k, v in patterns.items()
        }
    
    def _counterpoint_patterns(self, posts: List[Dict]) -> List[str]:
        """Extract counterpoint introduction patterns."""
        counterpoints = []
        
        patterns = [
            r'\b(Но|Однако|Впрочем|Тем не менее|С другой стороны)\b[^.!?]{20,150}',
        ]
        
        for post in posts:
            text = post.get('text', '') or post.get('text_plain', '')
            if not text:
                continue
            
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                counterpoints.extend(matches)
        
        return [cp for cp, _ in Counter(counterpoints).most_common(10)]
    
    def _emphasis_patterns(self, posts: List[Dict]) -> Dict[str, int]:
        """Analyze emphasis techniques."""
        techniques = {
            "caps_usage": 0,
            "exclamation_points": 0,
            "italics_or_bold": 0,
            "repetition": 0,
        }
        
        for post in posts:
            text = post.get('text', '') or post.get('text_plain', '')
            if not text:
                continue
            
            # CAPS for emphasis
            caps_words = re.findall(r'\b[А-ЯЁA-Z]{3,}\b', text)
            techniques["caps_usage"] += len(caps_words)
            
            # Exclamation points
            techniques["exclamation_points"] += text.count('!')
            
            # Check for markdown or HTML emphasis
            if re.search(r'(\*\w+\*|_\w+_|<b>|<i>|<em>)', text):
                techniques["italics_or_bold"] += 1
        
        return techniques
    
    def _avg_paragraphs(self, posts: List[Dict]) -> float:
        """Calculate average paragraph count."""
        counts = []
        for post in posts:
            text = post.get('text', '') or post.get('text_plain', '')
            if text:
                paras = len(re.split(r'\n\s*\n', text))
                counts.append(paras)
        return sum(counts) / len(counts) if counts else 0
    
    def _avg_sentences_per_para(self, posts: List[Dict]) -> float:
        """Calculate average sentences per paragraph."""
        ratios = []
        for post in posts:
            text = post.get('text', '') or post.get('text_plain', '')
            if text:
                paras = re.split(r'\n\s*\n', text)
                for para in paras:
                    sentences = len(re.split(r'[.!?]+', para))
                    ratios.append(sentences)
        return sum(ratios) / len(ratios) if ratios else 0
    
    def _punctuation_analysis(self, posts: List[Dict]) -> Dict[str, float]:
        """Analyze punctuation usage patterns."""
        punct_counts = defaultdict(int)
        total_chars = 0
        
        for post in posts:
            text = post.get('text', '') or post.get('text_plain', '')
            if text:
                total_chars += len(text)
                punct_counts['comma'] += text.count(',')
                punct_counts['semicolon'] += text.count(';')
                punct_counts['colon'] += text.count(':')
                punct_counts['dash'] += text.count('—') + text.count('–')
                punct_counts['ellipsis'] += text.count('...')
                punct_counts['question'] += text.count('?')
                punct_counts['exclamation'] += text.count('!')
        
        # Normalize by total characters
        if total_chars > 0:
            return {
                k: v / total_chars * 1000  # per 1000 chars
                for k, v in punct_counts.items()
            }
        return dict(punct_counts)
    
    def _cluster_patterns(
        self,
        patterns: List[str],
        max_results: int = 10
    ) -> List[str]:
        """Cluster similar patterns and return representatives."""
        if not patterns:
            return []
        
        # Simple clustering by first few words
        clusters = defaultdict(list)
        for pattern in patterns:
            key = ' '.join(pattern.split()[:3])  # First 3 words
            clusters[key].append(pattern)
        
        # Return most common pattern from each cluster
        representatives = []
        for cluster_patterns in clusters.values():
            most_common = Counter(cluster_patterns).most_common(1)[0][0]
            representatives.append(most_common)
        
        return representatives[:max_results]
    
    def _mode(self, values: List) -> Any:
        """Get most common value."""
        if not values:
            return None
        return Counter(values).most_common(1)[0][0]


def get_enhanced_style_prompt(posts: List[Dict[str, Any]]) -> str:
    """
    Generate enhanced style prompt using deep analysis.
    
    Args:
        posts: List of analyzed blog posts
    
    Returns:
        Detailed style description string
    """
    analyzer = AdvancedStyleAnalyzer()
    patterns = analyzer.extract_deep_patterns(posts)
    
    prompt = f"""РАСШИРЕННЫЙ АНАЛИЗ СТИЛЯ:

Структура текста:
- Средняя длина: {patterns['paragraph_flow']['avg_paragraph_length']:.0f} символов на параграф
- Типично параграфов: {patterns['paragraph_flow']['typical_paragraph_count']}
- Предложений на параграф: {patterns['avg_sentence_per_paragraph']:.1f}

Риторические приемы:
- Риторические вопросы используются часто
- Ирония и сарказм через контраст и цитаты
- Исторические параллели для усиления аргументации

Характерные открытия постов:
{chr(10).join(f"- {opening}" for opening in patterns['opening_patterns'][:3])}

Типичные завершения:
{chr(10).join(f"- {closing}" for closing in patterns['closing_patterns'][:3])}

Аргументация:
{chr(10).join(f"- {k}: {v}" for k, v in patterns['argument_patterns'].items())}

Фирменные выражения:
{chr(10).join(f'- "{phrase}"' for phrase in patterns['signature_expressions'][:10])}
"""
    
    return prompt

