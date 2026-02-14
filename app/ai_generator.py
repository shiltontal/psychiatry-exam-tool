"""
Advanced MCQ Generator for Child Psychiatry Certification Exams
Based on NBME/USMLE standards with psychometric validation
"""

import json
import os
import anthropic
import config
from app.db import get_db
from app.pdf_extractor import get_topic_content
from app.mcq_validator import validate_mcq

# ============================================================================
# LANGUAGE CONFIGURATION
# ============================================================================

LANGUAGE_CONFIG = {
    'he': {
        'name': 'Hebrew',
        'dir': 'rtl',
        'option_labels': ['א', 'ב', 'ג', 'ד'],
        'no_subtopics': '(אין תת-נושאים מפורטים)',
        'no_content_error': 'לא נמצא תוכן מקבצי ה-PDF. אנא ודא שהקבצים הועלו ושיש מיפוי עמודים לנושא זה.',
    },
    'ar': {
        'name': 'Arabic',
        'dir': 'rtl',
        'option_labels': ['أ', 'ب', 'ج', 'د'],
        'no_subtopics': '(لا توجد مواضيع فرعية محددة)',
        'no_content_error': 'لم يتم العثور على محتوى من ملفات PDF. يرجى التأكد من رفع الملفات ووجود تعيين صفحات لهذا الموضوع.',
    }
}

# ============================================================================
# ENHANCED SYSTEM PROMPT - Board Certification Level (Hebrew)
# ============================================================================

SYSTEM_PROMPT_HE = """אתה מומחה בינלאומי מוביל בפסיכומטריקה ובפסיכיאטריה של הילד והמתבגר, בעל 20+ שנות ניסיון בפיתוח מבחני הסמכה רפואיים בסטנדרט NBME/USMLE.

# תחומי מומחיותך

## פסיכומטריקה ובניית מבחנים
- מומחה בעקרונות: תוקף (validity), מהימנות (reliability), כוח הבחנה (discrimination index)
- יודע למנוע פגמים נפוצים: cues, vagueness, ambiguity, testwiseness
- מכיר את טקסונומיית Bloom ויוצר שאלות ברמות חשיבה גבוהות בלבד

## פסיכיאטריה של הילד והמתבגר
- בקיא ב-DSM-5-TR וב-ICD-11
- מכיר לעומק את Dulcan's Textbook (2nd Ed), Kaplan & Sadock's Synopsis, AACAP Practice Parameters
- מבין את המציאות הקלינית הישראלית

# עקרונות חובה ליצירת שאלות

## סוגי שאלות — חייבים לבדוק חשיבה גבוהה:

### שאלות יישום (Application)
מציגות מקרה קליני ודורשות החלטה אבחנתית או טיפולית.
דוגמה: "נער בן 15 מגיע למרפאתך עם... מהו הטיפול הראשוני המועדף?"

### שאלות ניתוח (Analysis)
דורשות ניתוח של מידע קליני מורכב — תוצאות בדיקות, היסטוריה, דיווחי הורים — והסקת מסקנות.
דוגמה: "בהתבסס על הממצאים הבאים, מהי האבחנה הסבירה ביותר?"

### שאלות הערכה (Evaluation)
דורשות השוואה בין אפשרויות טיפוליות ובחירה מושכלת.
דוגמה: "איזו גישה טיפולית תהיה היעילה ביותר עבור מטופל זה?"

### שאלות סינתזה (Synthesis)
מצריכות שילוב מידע ממקורות שונים — מחקר, הנחיות, ניסיון קליני.
דוגמה: "בהתחשב בגיל המטופל, תחלואה נלווית, וההנחיות העדכניות, מהי הגישה המקיפה ביותר?"

## גיוון פורמט השאלות — חובה:

רק 35% מהשאלות צריכות להיות ויניטות קליניות מלאות. השאר צריכות להיות מגוונות:

### סוגי פורמטים (בחר בהתאם לרמת Bloom):
1. **ויניטה קלינית (35%)** — מקרה מפורט עם גיל, מגדר, תסמינים, היסטוריה
2. **שאלה ישירה (25%)** — "מהו מנגנון הפעולה של...?", "מהם הקריטריונים ל...?"
3. **תרחיש קצר (20%)** — משפט או שניים של הקשר קליני ללא פרטים מלאים
4. **שאלת השוואה (10%)** — "מה ההבדל בין X ל-Y?", "איזה מהבאים נכון לגבי...?"
5. **שאלת מנגנון/פתופיזיולוגיה (10%)** — "כיצד פועל...?", "מה הקשר בין...?"

### התאמה לרמת Bloom:
- **זכירה/הבנה** → העדף שאלות ישירות, השוואה, מנגנון
- **יישום/ניתוח** → העדף תרחיש קצר או ויניטה
- **הערכה/סינתזה** → העדף ויניטה מלאה

---

## מבנה הויניטה הקלינית (כשנדרשת):

### פתיחה
- גיל, מגדר, הקשר הפניה (מי הפנה ולמה)
- "ילדה בת 8 הופנתה על ידי רופאת הילדים שלה בעקבות..."

### גוף
- תסמינים עיקריים: משך, חומרה, הקשר
- היסטוריה רלוונטית: התפתחותית, משפחתית, רפואית
- ממצאי בדיקה רלוונטיים
- רק מידע הכרחי — ללא "רעש"

### סגירה
- מוביל באופן טבעי לשאלה
- "בהתחשב בתמונה הקלינית, מהו..."

### כללים:
- התיאור חייב להתאים מבחינה התפתחותית לגיל הילד
- שפה, התנהגות וקוגניציה חייבים להיות ריאליסטיים לגיל
- ללא stereotypes תרבותיים או מגדריים
- ללא סתירות פנימיות

## כללים פסיכומטריים — חובה:

### השאלה (Lead-in):
- ממוקדת: בודקת נקודה אחת בלבד
- ברורה: ניסוח חד-משמעי
- רלוונטית: מתייחסת ישירות לויניטה

### התשובות (Options):
- בדיוק 4 תשובות (א, ב, ג, ד)
- כל התשובות סבירות מבחינה קלינית
- רק תשובה אחת נכונה או טובה ביותר (Best Answer)
- אורך דומה בין כל התשובות
- עקביות דקדוקית עם השאלה
- Distractors מבוססים על טעויות נפוצות אמיתיות של מתמחים

### איסורים מוחלטים:
- ❌ "כל התשובות נכונות" / "אף תשובה לא נכונה"
- ❌ שאלות שליליות ("מה לא נכון?", "EXCEPT", "NOT")
- ❌ מונחים מוחלטים: "תמיד", "אף פעם", "בכל המקרים", "רק"
- ❌ רמזים בניסוח שמובילים לתשובה (grammatical cues)
- ❌ תשובה נכונה שארוכה/ספציפית יותר מהאחרות

## הסבר — חובה לכל שאלה:

### לתשובה הנכונה:
- נימוק קליני מבוסס-ראיות
- הפניה לתוכן המקור (ספר, פרק, עמוד)
- קישור לעקרונות DSM-5-TR/ICD-11 כשרלוונטי

### לכל תשובה שגויה:
- מדוע היא שגויה או פחות טובה
- מהי הטעות הנפוצה שמובילה לבחירה בה
- באיזה מצב קליני אחר היא כן הייתה נכונה (אם רלוונטי)

---

# פורמט פלט - JSON בלבד, ללא טקסט נוסף:

{
  "questions": [
    {
      "stem": "תיאור מקרה קליני מפורט (vignette) + שאלה ממוקדת (lead-in)",
      "options": {
        "A": "תשובה א - באורך דומה לשאר התשובות",
        "B": "תשובה ב",
        "C": "תשובה ג",
        "D": "תשובה ד"
      },
      "correct": "A",
      "explanation": "## התשובה הנכונה: A\\n\\n[הסבר מפורט של 3-4 משפטים עם נימוק קליני]\\n\\n**מקור:** [שם הספר], עמוד [מספר]\\n\\n---\\n\\n## מדוע התשובות האחרות שגויות:\\n\\n**B שגויה:** [הסבר] | **טעות נפוצה:** [מה גורם לבחירה השגויה] | **הייתה נכונה אם:** [באיזה מקרה]\\n\\n**C שגויה:** [הסבר] | **טעות נפוצה:** [מה גורם לבחירה השגויה] | **הייתה נכונה אם:** [באיזה מקרה]\\n\\n**D שגויה:** [הסבר] | **טעות נפוצה:** [מה גורם לבחירה השגויה] | **הייתה נכונה אם:** [באיזה מקרה]\\n\\n---\\n\\n**Clinical Pearl:** [טיפ קליני חשוב הקשור לשאלה]\\n\\n**Key Takeaway:** [המסר המרכזי שיש לזכור]",
      "difficulty": "medium",
      "bloom_level": "application",
      "category": "diagnosis",
      "clinical_pearl": "טיפ קליני קצר וחשוב",
      "key_takeaway": "המסר המרכזי של השאלה",
      "patient_age": 8,
      "patient_gender": "female"
    }
  ]
}

**שדות חובה:**
- stem: תיאור המקרה והשאלה
- options: בדיוק 4 תשובות (A, B, C, D)
- correct: האות של התשובה הנכונה
- explanation: הסבר מלא בפורמט למעלה
- difficulty: easy/medium/hard
- bloom_level: application/analysis/evaluation/synthesis
- category: diagnosis/treatment/pharmacology/assessment/emergency/development
- clinical_pearl: טיפ קליני
- key_takeaway: מסר מרכזי
- patient_age: גיל המטופל (0-18)
- patient_gender: male/female
"""

# ============================================================================
# BLOOM LEVEL INSTRUCTIONS
# ============================================================================

BLOOM_INSTRUCTIONS = {
    'knowledge': """
צור שאלת זכירה (Knowledge/Recall):
- שאלה ישירה על עובדה, הגדרה, או מונח
- לא נדרש מקרה קליני מורכב - יכול להיות קצר או ללא ויניטה
- דוגמאות: "מהו מנגנון הפעולה של methylphenidate?", "מהם הקריטריונים ל-ADHD לפי DSM-5?"
- בודק ידע בסיסי שהנבחן צריך לדעת בעל פה
""",
    'comprehension': """
צור שאלת הבנה (Comprehension):
- שאלה שדורשת הסבר או פרשנות של מושג
- יכול לכלול תרחיש קצר להמחשה
- דוגמאות: "מדוע SSRIs מועדפים על TCAs בילדים?", "כיצד מסביר המודל הקוגניטיבי את החרדה?"
- הנבחן צריך להבין את ה"למה", לא רק את ה"מה"
""",
    'application': """
צור שאלת יישום (Application):
- הצג מקרה קליני מפורט עם מספיק מידע לקבלת החלטה
- השאלה צריכה לדרוש יישום ידע תיאורטי על מקרה ספציפי
- דוגמאות: "מהו הטיפול הראשוני המועדף?", "מהו הצעד הבא בטיפול?"
- הנבחן צריך לדעת מה עושים, לא רק מה יודעים
""",
    'analysis': """
צור שאלת ניתוח (Analysis):
- הצג מידע קליני מורכב: תוצאות בדיקות, היסטוריה, דיווחי הורים/מורים
- הנבחן צריך לנתח ולהבחין בין פרטים רלוונטיים ללא-רלוונטיים
- דוגמאות: "מהי האבחנה הסבירה ביותר?", "מה הממצא המכריע?"
- כלול מסיחים (red herrings) קלים שנבחן חזק יזהה
""",
    'evaluation': """
צור שאלת הערכה (Evaluation):
- הצג מצב שבו יש מספר אפשרויות טיפוליות לגיטימיות
- הנבחן צריך להעריך יתרונות/חסרונות ולבחור את הטוב ביותר
- דוגמאות: "איזו גישה עדיפה?", "מה השיקול החשוב ביותר?"
- הדגש trade-offs בין אפשרויות
""",
    'synthesis': """
צור שאלת סינתזה (Synthesis):
- דרוש שילוב מידע ממקורות שונים: אנמנזה + בדיקה + הנחיות + מחקר
- הנבחן צריך לבנות תוכנית מקיפה או להגיע למסקנה מורכבת
- דוגמאות: "מהי התוכנית הטיפולית המקיפה ביותר?", "מה ההתערבות רב-ממדית?"
- דרוש אינטגרציה של ידע מכמה תחומים
"""
}

# ============================================================================
# CATEGORY INSTRUCTIONS
# ============================================================================

CATEGORY_INSTRUCTIONS = {
    'diagnosis': 'מקד את השאלה באבחנה מבדלת — הצג תמונה קלינית שיכולה להתאים למספר אבחנות וגרום לנבחן להבחין.',
    'treatment': 'מקד בבחירת טיפול — כלול שיקולים של גיל, תחלואה נלווית, העדפות משפחה, ורמת חומרה.',
    'pharmacology': 'מקד בפרמקולוגיה — מינון, תופעות לוואי, אינטראקציות, ומעקב. כלול גיל ומשקל הילד.',
    'assessment': 'מקד בהערכה ובדיקות — איזה כלי הערכה, איזו בדיקה מעבדתית, מה סדר העדיפויות.',
    'emergency': 'מקד במצבי חירום — סיכון אובדני, אגרסיה, פסיכוזה חריפה. הדגש urgency וסדר עדיפויות.',
    'development': 'מקד בהתפתחות — אבני דרך, סטיות מהנורמה, red flags. התאם לגיל ספציפי.',
    'comorbidity': 'מקד בתחלואה נלווית — הצג מטופל עם מספר אבחנות וגרום להבחנה בין תסמינים חופפים.',
    'psychotherapy': 'מקד בפסיכותרפיה — בחירת מודאליות, התאמה לגיל, יעדים טיפוליים, evidence-base.'
}

# ============================================================================
# DIFFICULTY DEFINITIONS
# ============================================================================

DIFFICULTY_MAP = {
    'easy': """רמת קושי: קל
- מקרה קליני עם מצג טיפוסי וקלאסי
- המסיחים שייכים לקטגוריות שונות בבירור
- שאלה על הצעד הראשון והברור ביותר
- מתאים למתמחה בשנה ראשונה""",

    'medium': """רמת קושי: בינוני
- מקרה עם מורכבות בינונית — תחלואה נלווית או הצגה לא טיפוסית
- המסיחים קרובים קלינית ושייכים לאותו אשכול
- דורש שקלול של מספר נתונים קליניים
- מתאים למתמחה בשנים 2-3""",

    'hard': """רמת קושי: קשה
- מקרה מורכב — הצגה נדירה, מספר אבחנות מתחרות, שיקולים סותרים
- המסיחים קרובים מאוד ודורשים הבחנה עדינה
- דורש ידע מעמיק של הנחיות עדכניות ומחקר
- מתאים למתמחה בכיר/מומחה"""
}

# ============================================================================
# CLINICAL TASK TYPES (legacy support)
# ============================================================================

CLINICAL_TASK_MAP = {
    'mixed': 'מגוון — שלב סוגי שאלות שונים',
    'apply': 'יישום ידע למקרה קליני',
    'discriminate': 'הבחנה בין אפשרויות קרובות',
    'decide_uncertain': 'קבלת החלטות בתנאי אי-ודאות',
    'prioritize': 'זיהוי דחיפות ותיעדוף',
    'integrate': 'אינטגרציה בין-תחומית',
    'evaluate': 'הערכה ביקורתית',
    'adapt': 'שיפוט קליני מורכב'
}

# ============================================================================
# USER PROMPT TEMPLATE
# ============================================================================

USER_PROMPT_TEMPLATE = """צור {count} שאלות MCQ ברמת מבחן הסמכה בנושא: {topic_he} ({topic_en})

## הגדרות לשאלה זו:

**רמת קושי:**
{difficulty}

**רמת חשיבה (Bloom):**
{bloom_instruction}

**קטגוריית שאלה:**
{category_instruction}

**מטרת השאלה:** {clinical_task}

---

## הנושא שייך לפרק: {chapter_he}

### תת-נושאים שנבחרו (צור שאלות רק על אלו):
{subtopics_list}

---

## חומר מקור מספרי הלימוד — זה המקור היחיד שלך:

{content}

---

## הנחיות קריטיות:

1. **בסס כל שאלה אך ורק על החומר למעלה** — אל תמציא מידע
2. **ציין מקור מדויק בהסבר** — שם ספר + מספר עמוד (ראה "--- Page X ---")
3. **הסבר מפורט לכל תשובה שגויה** — מה הטעות, מתי זה כן נכון
4. **כלול Clinical Pearl ו-Key Takeaway** בכל שאלה
5. **גוון פורמטים** — רק 35% ויניטות! השאר: שאלות ישירות, תרחיש קצר, השוואה, מנגנון
6. **ודא שאורך התשובות דומה** — אל תתן רמזים פסיכומטריים

## פורמט: החזר JSON בלבד, ללא backticks, ללא טקסט נוסף."""

# ============================================================================
# ARABIC SYSTEM PROMPT
# ============================================================================

SYSTEM_PROMPT_AR = """أنت خبير دولي رائد في القياس النفسي والطب النفسي للأطفال والمراهقين، مع أكثر من 20 عامًا من الخبرة في تطوير امتحانات الشهادات الطبية بمعايير NBME/USMLE.

# مجالات خبرتك

## القياس النفسي وبناء الاختبارات
- خبير في المبادئ: الصدق (validity)، الموثوقية (reliability)، قوة التمييز (discrimination index)
- تعرف كيفية منع العيوب الشائعة: التلميحات، الغموض، قابلية الاختبار
- تعرف تصنيف بلوم وتنشئ أسئلة بمستويات تفكير عليا

## الطب النفسي للأطفال والمراهقين
- متمكن من DSM-5-TR و ICD-11
- على دراية عميقة بـ Dulcan's Textbook و Kaplan & Sadock's Synopsis

# قواعد إلزامية لإنشاء الأسئلة

## تنويع تنسيق الأسئلة — إلزامي:

35% فقط من الأسئلة يجب أن تكون حالات سريرية كاملة. البقية متنوعة:

1. **حالة سريرية (35%)** — حالة مفصلة مع العمر والجنس والأعراض والتاريخ
2. **سؤال مباشر (25%)** — "ما هي آلية عمل...؟"، "ما هي معايير...؟"
3. **سيناريو قصير (20%)** — جملة أو جملتين من السياق السريري
4. **سؤال مقارنة (10%)** — "ما الفرق بين X و Y؟"
5. **سؤال آلية/فيزيولوجيا مرضية (10%)** — "كيف يعمل...؟"

## قواعد القياس النفسي — إلزامية:

### الخيارات (Options):
- بالضبط 4 إجابات (أ، ب، ج، د)
- جميع الإجابات معقولة سريرياً
- إجابة واحدة صحيحة فقط أو الأفضل (Best Answer)
- أطوال متشابهة بين جميع الإجابات

### محظورات مطلقة:
- ❌ "جميع الإجابات صحيحة" / "لا توجد إجابة صحيحة"
- ❌ أسئلة سلبية ("ما هو غير صحيح؟"، "EXCEPT"، "NOT")
- ❌ مصطلحات مطلقة: "دائماً"، "أبداً"، "في جميع الحالات"، "فقط"

## الشرح — إلزامي لكل سؤال:

### للإجابة الصحيحة:
- تبرير سريري قائم على الأدلة
- إشارة إلى المصدر (الكتاب، الفصل، الصفحة)

### لكل إجابة خاطئة:
- لماذا هي خاطئة أو أقل جودة
- ما هو الخطأ الشائع الذي يؤدي لاختيارها
- في أي حالة سريرية أخرى ستكون صحيحة (إذا كان ذلك مناسباً)

---

# تنسيق الإخراج - JSON فقط، بدون نص إضافي:

{
  "questions": [
    {
      "stem": "وصف الحالة السريرية + السؤال المركز",
      "options": {
        "A": "الإجابة أ",
        "B": "الإجابة ب",
        "C": "الإجابة ج",
        "D": "الإجابة د"
      },
      "correct": "A",
      "explanation": "## الإجابة الصحيحة: A\\n\\n[شرح مفصل]\\n\\n**المصدر:** [اسم الكتاب]، صفحة [رقم]\\n\\n---\\n\\n## لماذا الإجابات الأخرى خاطئة:\\n\\n**B خاطئة:** [شرح]\\n\\n**C خاطئة:** [شرح]\\n\\n**D خاطئة:** [شرح]\\n\\n---\\n\\n**Clinical Pearl:** [نصيحة سريرية]\\n\\n**Key Takeaway:** [الرسالة الرئيسية]",
      "difficulty": "medium",
      "bloom_level": "application",
      "category": "diagnosis",
      "clinical_pearl": "نصيحة سريرية قصيرة ومهمة",
      "key_takeaway": "الرسالة الرئيسية للسؤال",
      "patient_age": 8,
      "patient_gender": "female"
    }
  ]
}
"""

# ============================================================================
# ARABIC BLOOM INSTRUCTIONS
# ============================================================================

BLOOM_INSTRUCTIONS_AR = {
    'knowledge': """
أنشئ سؤال تذكر (Knowledge/Recall):
- سؤال مباشر عن حقيقة أو تعريف أو مصطلح
- لا يتطلب حالة سريرية معقدة
- أمثلة: "ما هي آلية عمل methylphenidate؟"، "ما هي معايير ADHD وفقاً لـ DSM-5؟"
""",
    'comprehension': """
أنشئ سؤال فهم (Comprehension):
- سؤال يتطلب شرح أو تفسير مفهوم
- أمثلة: "لماذا يُفضل SSRIs على TCAs عند الأطفال؟"
""",
    'application': """
أنشئ سؤال تطبيق (Application):
- قدم حالة سريرية مفصلة مع معلومات كافية لاتخاذ قرار
- أمثلة: "ما هو العلاج الأولي المفضل؟"، "ما هي الخطوة التالية في العلاج؟"
""",
    'analysis': """
أنشئ سؤال تحليل (Analysis):
- قدم معلومات سريرية معقدة: نتائج فحوصات، تاريخ، تقارير الوالدين
- أمثلة: "ما هو التشخيص الأكثر احتمالاً؟"، "ما هو الاكتشاف الحاسم؟"
""",
    'evaluation': """
أنشئ سؤال تقييم (Evaluation):
- قدم موقفاً فيه عدة خيارات علاجية مشروعة
- أمثلة: "أي نهج أفضل؟"، "ما هو الاعتبار الأهم؟"
""",
    'synthesis': """
أنشئ سؤال تركيب (Synthesis):
- يتطلب دمج معلومات من مصادر مختلفة
- أمثلة: "ما هي الخطة العلاجية الأكثر شمولاً؟"
"""
}

# ============================================================================
# ARABIC CATEGORY INSTRUCTIONS
# ============================================================================

CATEGORY_INSTRUCTIONS_AR = {
    'diagnosis': 'ركز السؤال على التشخيص التفريقي — قدم صورة سريرية يمكن أن تناسب عدة تشخيصات.',
    'treatment': 'ركز على اختيار العلاج — شمل اعتبارات العمر والأمراض المصاحبة وتفضيلات العائلة.',
    'pharmacology': 'ركز على علم الأدوية — الجرعة والآثار الجانبية والتفاعلات والمتابعة.',
    'assessment': 'ركز على التقييم والفحوصات — أي أداة تقييم، أي فحص مخبري.',
    'emergency': 'ركز على حالات الطوارئ — خطر الانتحار، العدوانية، الذهان الحاد.',
    'development': 'ركز على التطور — المعالم التطورية، الانحرافات عن المعيار.',
    'comorbidity': 'ركز على الأمراض المصاحبة — قدم مريضاً بعدة تشخيصات.',
    'psychotherapy': 'ركز على العلاج النفسي — اختيار الطريقة، الملاءمة للعمر.'
}

# ============================================================================
# ARABIC USER PROMPT TEMPLATE
# ============================================================================

USER_PROMPT_TEMPLATE_AR = """أنشئ {count} أسئلة MCQ بمستوى امتحان الشهادة في موضوع: {topic_en}

## إعدادات هذا السؤال:

**مستوى الصعوبة:**
{difficulty}

**مستوى التفكير (Bloom):**
{bloom_instruction}

**فئة السؤال:**
{category_instruction}

---

## الموضوع ينتمي إلى الفصل: {chapter_en}

### المواضيع الفرعية المختارة:
{subtopics_list}

---

## مادة المصدر من الكتب الدراسية — هذا مصدرك الوحيد:

{content}

---

## تعليمات حاسمة:

1. **استند كل سؤال فقط على المادة أعلاه** — لا تخترع معلومات
2. **اذكر المصدر بدقة في الشرح** — اسم الكتاب + رقم الصفحة (انظر "--- Page X ---")
3. **شرح مفصل لكل إجابة خاطئة** — ما هو الخطأ، متى تكون صحيحة
4. **شمل Clinical Pearl و Key Takeaway** في كل سؤال
5. **نوّع التنسيقات** — 35% فقط حالات سريرية! البقية: أسئلة مباشرة، سيناريو قصير
6. **تأكد من أن أطوال الإجابات متشابهة**

## التنسيق: أعد JSON فقط، بدون backticks، بدون نص إضافي."""


# ============================================================================
# MAIN GENERATION FUNCTION
# ============================================================================

def generate_questions(topic_id, count=3, difficulty='medium', clinical_task='mixed',
                       subtopic_ids=None, bloom_level='application', category='diagnosis',
                       language='he'):
    """
    Generate high-quality MCQ questions based on textbook content.

    Args:
        topic_id: ID of the topic from the syllabus
        count: Number of questions to generate
        difficulty: easy/medium/hard
        clinical_task: Type of clinical task (legacy)
        subtopic_ids: Optional list of subtopic IDs to focus on
        bloom_level: application/analysis/evaluation/synthesis
        category: diagnosis/treatment/pharmacology/assessment/emergency/development
        language: 'he' for Hebrew, 'ar' for Arabic

    Returns:
        List of created question IDs
    """
    db = get_db()
    topic = db.execute("SELECT * FROM topics WHERE id = ?", (topic_id,)).fetchone()
    if not topic:
        raise ValueError(f"Topic {topic_id} not found")

    # Get language config
    lang_config = LANGUAGE_CONFIG.get(language, LANGUAGE_CONFIG['he'])

    # Get subtopics
    if subtopic_ids:
        placeholders = ','.join('?' for _ in subtopic_ids)
        subtopics = db.execute(
            f"SELECT hebrew, english FROM topics WHERE parent_id = ? AND id IN ({placeholders})",
            [topic_id] + subtopic_ids
        ).fetchall()
    else:
        subtopics = db.execute(
            "SELECT hebrew, english FROM topics WHERE parent_id = ?", (topic_id,)
        ).fetchall()

    if language == 'ar':
        subtopics_text = '\n'.join(
            f'- {s["english"]}' for s in subtopics
        ) or lang_config['no_subtopics']
    else:
        subtopics_text = '\n'.join(
            f'- {s["hebrew"]} ({s["english"]})' for s in subtopics
        ) or lang_config['no_subtopics']

    # Get topic mapping
    mapping = db.execute(
        "SELECT * FROM topic_mappings WHERE topic_id = ?", (topic_id,)
    ).fetchone()
    if not mapping and topic['parent_id']:
        mapping = db.execute(
            "SELECT * FROM topic_mappings WHERE topic_id = ?", (topic['parent_id'],)
        ).fetchone()

    # Extract textbook content
    content = get_topic_content(dict(mapping) if mapping else None)
    if not content:
        raise ValueError(lang_config['no_content_error'])

    # Select prompts based on language
    if language == 'ar':
        system_prompt = SYSTEM_PROMPT_AR
        bloom_instruction = BLOOM_INSTRUCTIONS_AR.get(bloom_level, BLOOM_INSTRUCTIONS_AR['application'])
        category_instruction = CATEGORY_INSTRUCTIONS_AR.get(category, CATEGORY_INSTRUCTIONS_AR['diagnosis'])
        user_prompt = USER_PROMPT_TEMPLATE_AR.format(
            count=count,
            topic_en=topic['english'],
            difficulty=DIFFICULTY_MAP.get(difficulty, DIFFICULTY_MAP['medium']),
            bloom_instruction=bloom_instruction,
            category_instruction=category_instruction,
            chapter_en=topic['chapter_en'],
            subtopics_list=subtopics_text,
            content=content,
        )
    else:
        system_prompt = SYSTEM_PROMPT_HE
        bloom_instruction = BLOOM_INSTRUCTIONS.get(bloom_level, BLOOM_INSTRUCTIONS['application'])
        category_instruction = CATEGORY_INSTRUCTIONS.get(category, CATEGORY_INSTRUCTIONS['diagnosis'])
        user_prompt = USER_PROMPT_TEMPLATE.format(
            count=count,
            topic_he=topic['hebrew'],
            topic_en=topic['english'],
            difficulty=DIFFICULTY_MAP.get(difficulty, DIFFICULTY_MAP['medium']),
            bloom_instruction=bloom_instruction,
            category_instruction=category_instruction,
            clinical_task=CLINICAL_TASK_MAP.get(clinical_task, CLINICAL_TASK_MAP['mixed']),
            chapter_he=topic['chapter_he'],
            subtopics_list=subtopics_text,
            content=content,
        )

    # Call Claude API
    api_key = os.environ.get('ANTHROPIC_API_KEY', '') or config.CLAUDE_API_KEY
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set.")

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=8192,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
        temperature=0.7,
    )

    raw = response.content[0].text

    # Parse JSON response
    text = raw
    if '```json' in text:
        text = text.split('```json', 1)[1].split('```', 1)[0]
    elif '```' in text:
        text = text.split('```', 1)[1].split('```', 1)[0]

    data = json.loads(text.strip())
    questions = data.get('questions', [])

    # Log generation
    tokens = response.usage.input_tokens + response.usage.output_tokens
    db.execute(
        "INSERT INTO generation_log (topic_id, prompt_used, raw_response, questions_created, model_used, tokens_used) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (topic_id, user_prompt[:2000], raw[:5000], len(questions), config.CLAUDE_MODEL, tokens)
    )
    db.commit()

    # Validate and store questions
    created = []
    for q in questions:
        # Run psychometric validation
        is_valid, score, issues = validate_mcq(q)

        # Log validation issues if any
        if issues:
            print(f"[MCQ Validator] Score: {score}, Issues: {[i['message'] for i in issues]}")

        opts = q.get('options', {})
        explanation = q.get('explanation', '')

        # Add clinical pearl and key takeaway to explanation if provided
        if q.get('clinical_pearl'):
            explanation += f"\n\n**Clinical Pearl:** {q['clinical_pearl']}"
        if q.get('key_takeaway'):
            explanation += f"\n\n**Key Takeaway:** {q['key_takeaway']}"

        cursor = db.execute(
            "INSERT INTO questions (topic_id, stem_he, option_a, option_b, option_c, option_d, option_e, "
            "correct_answer, explanation_he, difficulty, bloom_level, question_type, status, ai_generated, language) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'draft', 1, ?)",
            (topic_id, q.get('stem', ''),
             opts.get('A', ''), opts.get('B', ''), opts.get('C', ''), opts.get('D', ''),
             opts.get('E', ''), q.get('correct', 'A'),
             explanation,
             q.get('difficulty', difficulty),
             q.get('bloom_level', bloom_level),
             q.get('category', category),
             language)
        )
        created.append(cursor.lastrowid)

    db.commit()
    return created
