"""
MCQ Quality Validator - Psychometric validation for generated questions
"""

from typing import List, Dict, Tuple

# Absolute terms that indicate poor question design
ABSOLUTE_TERMS = ['תמיד', 'אף פעם', 'בכל המקרים', 'לעולם לא', 'בהכרח', 'רק', 'always', 'never', 'only']

# All/none patterns to avoid
ALL_NONE_PATTERNS = ['כל התשובות', 'אף תשובה', 'כולן נכונות', 'all of the above', 'none of the above']

# Negative stem patterns (should be avoided)
NEGATIVE_PATTERNS = ['לא נכון', 'אינו', 'מלבד', 'למעט', 'EXCEPT', 'NOT', 'LEAST']


def validate_mcq(question: Dict) -> Tuple[bool, int, List[Dict]]:
    """
    Validate a single MCQ for psychometric quality.

    Returns:
        Tuple of (is_valid, score, issues)
        - is_valid: True if no critical errors
        - score: Quality score 0-100
        - issues: List of {rule, message, severity} dicts
    """
    issues = []

    stem = question.get('stem', '')
    options = question.get('options', {})
    correct = question.get('correct', '')
    explanation = question.get('explanation', '')

    # === STRUCTURAL CHECKS ===

    # Must have exactly 4 options
    option_count = len([k for k in ['A', 'B', 'C', 'D'] if options.get(k)])
    if option_count != 4:
        issues.append({
            'rule': 'option_count',
            'message': f'נדרשות בדיוק 4 תשובות, נמצאו {option_count}',
            'severity': 'error'
        })

    # Must have a correct answer
    if correct not in ['A', 'B', 'C', 'D']:
        issues.append({
            'rule': 'correct_answer',
            'message': f'תשובה נכונה לא תקינה: {correct}',
            'severity': 'error'
        })

    # === PSYCHOMETRIC CHECKS ===

    # Check for absolute terms in options
    for key in ['A', 'B', 'C', 'D']:
        option_text = options.get(key, '')
        for term in ABSOLUTE_TERMS:
            if term in option_text or term.lower() in option_text.lower():
                issues.append({
                    'rule': 'absolute_terms',
                    'message': f'תשובה {key} מכילה מונח מוחלט: "{term}"',
                    'severity': 'error'
                })

    # Check for "all/none of the above"
    for key in ['A', 'B', 'C', 'D']:
        option_text = options.get(key, '')
        for pattern in ALL_NONE_PATTERNS:
            if pattern in option_text or pattern.lower() in option_text.lower():
                issues.append({
                    'rule': 'all_none_above',
                    'message': f'תשובה {key} מכילה "כל/אף תשובה"',
                    'severity': 'error'
                })

    # Check for negative stems
    for pattern in NEGATIVE_PATTERNS:
        if pattern in stem or pattern.upper() in stem:
            issues.append({
                'rule': 'negative_stem',
                'message': f'השאלה מכילה ניסוח שלילי: "{pattern}"',
                'severity': 'warning'
            })

    # Check option length balance
    option_lengths = [len(options.get(k, '')) for k in ['A', 'B', 'C', 'D']]
    if option_lengths:
        min_len = min(option_lengths)
        max_len = max(option_lengths)
        if min_len > 0 and max_len > min_len * 2.5:
            longest_idx = option_lengths.index(max_len)
            longest_key = ['A', 'B', 'C', 'D'][longest_idx]
            issues.append({
                'rule': 'option_length_balance',
                'message': f'תשובה {longest_key} ארוכה משמעותית מהאחרות ({max_len} לעומת {min_len} תווים)',
                'severity': 'warning'
            })
            # Check if longest is correct - big red flag
            if longest_key == correct:
                issues.append({
                    'rule': 'correct_answer_longest',
                    'message': 'התשובה הנכונה היא הארוכה ביותר — רמז פסיכומטרי!',
                    'severity': 'error'
                })

    # Check stem length - but allow shorter stems for direct/knowledge questions
    # Only warn if very short (under 30 chars) which indicates incomplete question
    if len(stem) < 30:
        issues.append({
            'rule': 'stem_too_short',
            'message': 'השאלה קצרה מדי',
            'severity': 'warning'
        })

    # Check explanation exists
    if not explanation or len(explanation) < 50:
        issues.append({
            'rule': 'missing_explanation',
            'message': 'חסר הסבר מפורט לתשובה',
            'severity': 'warning'
        })

    # Check for source citation
    if 'מקור:' not in explanation and 'עמוד' not in explanation:
        issues.append({
            'rule': 'missing_source',
            'message': 'חסר ציטוט מקור (ספר ועמוד)',
            'severity': 'warning'
        })

    # === CALCULATE SCORE ===
    error_count = sum(1 for i in issues if i['severity'] == 'error')
    warning_count = sum(1 for i in issues if i['severity'] == 'warning')

    error_penalty = error_count * 20
    warning_penalty = warning_count * 5
    score = max(0, 100 - error_penalty - warning_penalty)

    is_valid = error_count == 0

    return is_valid, score, issues


def validate_batch(questions: List[Dict]) -> Dict:
    """
    Validate a batch of questions and return statistics.

    Returns:
        Dict with validation results and statistics
    """
    results = []
    valid_count = 0
    total_score = 0

    # Track correct answer distribution
    correct_distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0}

    for q in questions:
        is_valid, score, issues = validate_mcq(q)
        results.append({
            'question': q.get('stem', '')[:100] + '...',
            'is_valid': is_valid,
            'score': score,
            'issues': issues
        })

        if is_valid:
            valid_count += 1
        total_score += score

        correct = q.get('correct', '')
        if correct in correct_distribution:
            correct_distribution[correct] += 1

    # Check if correct answer distribution is skewed
    distribution_issues = []
    if questions:
        expected = len(questions) / 4
        for key, count in correct_distribution.items():
            if count > expected * 2:
                distribution_issues.append(f'תשובה {key} נכונה לעתים קרובות מדי ({count}/{len(questions)})')
            elif count == 0 and len(questions) >= 4:
                distribution_issues.append(f'תשובה {key} אף פעם לא נכונה')

    return {
        'total': len(questions),
        'valid': valid_count,
        'invalid': len(questions) - valid_count,
        'avg_score': round(total_score / len(questions)) if questions else 0,
        'correct_distribution': correct_distribution,
        'distribution_issues': distribution_issues,
        'details': results
    }
