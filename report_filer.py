from supabase import create_client, Client
from pathlib import Path
import uuid, os
import datetime
from dotenv import load_dotenv

# === LOAD ENV FILE FROM root/app/.env ===
env_path = Path(__file__).resolve().parent.parent / "app" / ".env"
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
REPORT_TYPE_ID = "89c1ffe7-2358-4957-95be-f144b2bead49"


# --- CHAPTER DATA ---
chapters = [
                {
                    "title": "Summary",
                    "instructions": "Construct a comprehensive summary of the user's story, highlighting significant experiences, challenges, and aspirations they've conveyed. This chapter aims to interlace the various threads of the user's life narrative, emphasizing the pivotal moments, hurdles, and dreams that have molded their identity. Drawing from Frankl's Logotherapeutic perspective on the intrinsic meaning of life, explore the user's distinct pursuit of purpose. Integrate Carl Rogers' Person-Centered approach by acknowledging their feelings and experiences without judgment. Using principles from Positive Psychology and the PERMA Model, provide a well-rounded view that bridges their past achievements, current aspirations, and potential for a future filled with meaning, engagement, relationships, accomplishment, and positive emotions. Additionally, critically examine the inconsistencies and unrealized potentials in their story. Question the alignment of their actions with their stated goals and values, confront any discrepancies or avoidance patterns, and encourage self-reflection on uncomfortable truths that might be crucial for growth.",
                    "length": 300,
                    "format": "Format Requirements: The answer should be provided in a JSON string like this (only provide the json as json str and make sure it can be interpreted by python code, enclosing property names in double quotes and please divide it into paragraphs by adding newline characters to improve readability): {\"Header\": \"Summary\",\"Content\": \"This is the summary text that provides a comprehensive summary of the user's story.\"}"
                },
                {
                    "title": "Values and Desires",
                    "instructions": "Explore and articulate three pivotal values and three profound desires that drive the user's actions and perhaps limits them in their successful searcg for meaning and purpose, referencing their narrative. While rooted in the principles of Logotherapy to recognize their striving for significance, integrate a critical examination to assess whether these values and desires truly align with their intrinsic motivations or are influenced by external factors and unexamined biases. For the desires, prioritize the critical aspects and confront the reader with how it may limit them. Utilize the lens of Person-Centered Therapy not only to validate and appreciate the user's experiences but also to challenge any discrepancies between their stated values and actual life choices. With insights from Positive Psychology and the PERMA Model, analyze how these values contribute to their well-being and personal growth, while also confronting areas where their actions may not align with their professed values. This profound reflection should not only dive deep into the interconnectedness of the user's values and desires with their life story while highlight areas of potential self-deception or avoidance, encouraging a brutally honest and transformative journey towards a life rich in meaning and authentic engagement.",
                    "length": 500,
                    "format": "Format Requirements: The answer should be provided in a JSON format like below (only provide the json as json str and make sure it can be interpreted by python code, enclosing property names in double quotes and all keys have values): {\"Header\": \"Values and Desires\",   \"Content\": [ \"With this introductory text, set the stage for the chapter with the detailed list of values and desires that follow.\",  {\"Header\": \"Value 1\", \"Content\": \"Description and analysis of Value 1\"},  {\"Header\": \"Value 2\", \"Content\": \"Description and analysis of Value 2\"},  ...,  {\"Header\": \"Key Themes Summary\", \"Content\": \"A concise summary of the main themes or topics covered in this chapter.\"}] }"
                },
                {
                    "title": "Barriers",
                    "instructions": "Conduct a bold and unflinching analysis of at least three significant barriers obstructing the user's quest for meaning and personal growth. Your focus should penetrate beyond the surface of shared experiences and narratives, zeroing in on the more critical aspects of internal conflicts and self-imposed limitations. Apply the principles of Logotherapy to expose how these barriers may represent a deeper existential void or misalignment with the user's true purpose in life. While incorporating insights from Person-Centered Therapy, prioritize brutal honesty over empathy and validation. It's essential to confront the user directly with the uncomfortable truths about their active role in maintaining these barriers. Employ concepts from Positive Psychology and the PERMA Model not just to understand but to critically assess the harmful impact of these barriers, emphasizing their negative effects on positive emotions, engagement, relationships, meaning, and accomplishments. For each identified barrier, provide a stark critique of its roots and repercussions. Propose strategies for dismantling these barriers that demand the user to face and challenge their existing mindset and behaviors head-on. Your questions should not merely invite introspection but enforce a rigorous self-evaluation, steering the user towards a raw and sometimes painful acknowledgment of their barriers to growth. This chapter is not just an analysis; it's a confrontation. It should serve as a relentless wake-up call, compelling the user to recognize and tackle the harsh realities about themselves and the choices they've made in life.",
                    "length": 400,
                    "format": "Format Requirements: The answer should be provided in a JSON format like below (only provide the json as json str and make sure it can be interpreted by python code, enclosing property names in double quotes and all keys have values): {\"Header\": \"Barriers\",   \"Content\": [  \"With this introductory text, set the stage for the chapter with the detailed list of barriers that follow.\",  {\"Header\": \"Barrier 1\", \"Content\": \"Description and analysis of Barrier 1\"},  {\"Header\": \"Barrier 2\", \"Content\": \"Description and analysis of Barrier 2\"},  ...,  {\"Header\": \"Key Themes Summary\", \"Content\": \"A concise summary of the main themes or topics covered in this chapter.\"}] }"
                },
                {
                    "title": "Potential Sources of Meaning",
                    "instructions": "Drawing from the user's narrative, begin by identifying a minimum of 4 potential sources of meaning with the highest probability of being a source of meaning, more sources if there are more. These insights should deeply resonate with the users story and be grounded in Viktor Frankl's Logotherapy's belief in life's intrinsic meaning, Carl Rogers' Person-Centered Therapy's emphasis on the individual's inherent capacity and drive towards self-actualization, and the guiding principles of Positive Psychology and the PERMA Model that center on human thriving. For each 'Potential Source of Meaning' you unveil, provide rich examples from the user's unique journey, illustrating how these sources align with their quest for purpose, self-direction, and holistic well-being. Each insight should be articulated with a focus on personal growth, authentic self-recognition, and the pursuit of genuine happiness and fulfillment. The insights provided may be new and under-explored by the user as they are reading this report to learn more things about themselves. Feel free to add potential sources that are not mentioned by the user but can fit their story based on what other people with similar experiences do.",
                    "length": 600,
                    "format": "Format Requirements: The answer should be provided in a JSON format like below (only provide the json as json str and make sure it can be interpreted by python code, enclosing property names in double quotes and all keys have values): {\"Header\": \"Potential Sources of Meaning\", \"Content\": [ \"With this introductory text, set the stage for the chapter with detailed list of potential sources of meaning and purpose.\", {\"Header\": \"Source 1\", \"Content\": \"Description and analysis of source 1\"}, {\"Header\": \"Source 2\", \"Content\": \"Description and analysis of Source2\"}, ... (continues for sources) ..., {\"Header\": \"Critical Analysis\", \"Content\": \"This section critically examines potential sources of meaning that the user might be avoiding or overlooking. It challenges the user to reflect on discrepancies between their stated values and actions, and encourages exploration of new areas for growth and fulfillment.\"}, {\"Header\": \"Key Themes Summary\", \"Content\": \"A concise summary of the main themes or topics covered in this chapter.\"}]}"
                },
                {
                    "title": "Recommendations On How To Implement More Meaning",
                    "instructions": "For this chapter, prioritize practical implementation and critical challenge to navigate through things that are holding the user back. Drawing from the 'Potential Sources of Meaning' identified in the previous chapter (chapter included below), formulate tailored recommendations for each, emphasizing the need for the user to confront and overcome personal barriers that may be hindering their implementation. Ground these suggestions in Viktor Frankl's Logotherapy, Carl Rogers' Person-Centered Therapy, and the PERMA Model from Positive Psychology. Each recommendation should not only provide a practical roadmap but also challenge the user to critically examine and break away from comfort zones, habitual patterns, and self-imposed limitations. For each 'Potential Source of Meaning,' present a clear and actionable strategy that encourages the user to take bold steps and make transformative changes. Emphasize the importance of active engagement and connection with these sources of meaning, while confronting fears, uncertainties, and complacency. The recommendations should be structured to not only offer a cohesive narrative but also to push the user towards significant personal growth and fulfillment. Reinforce every recommendation with an understanding that tangible and deliberate actions are necessary to incorporate these ideals into their daily life, moving beyond mere contemplation to proactive life changes.",
                    "length": 800,
                    "format": "Format Requirements: The answer should be provided in a JSON format like below:{\"Header\": \"Recommendations\", \"Content\": [\"With this introductory text, set the stage for the recommendations chapter, highlighting the need for critical self-evaluation and transformative actions.\", {\"Header\": \"Recommendation 1\",\"Content\": {\"Introduction\": \"Brief introduction to Recommendation 1, outlining its relevance.\",\"Action Steps\": \"Detailed steps for implementing Recommendation 1.\",\"Critical Challenge\": \"A section that challenges the user to confront personal barriers and embrace change as part of implementing this recommendation.\"} }, ... (continues for other recommendations),  {\"Header\": \"Key Themes Summary\", \"Content\": \"A concise summary of the main themes or topics covered in this chapter.\"}]}"
                },
                {
                    "title": "Additional Insights",
                    "instructions": "Reflect on the user's narrated moments of fulfillment and flow, analyzing both their positive aspects and the underlying challenges or missed opportunities. While embracing a non-judgmental, empathetic stance as in Carl Rogers' Person-Centered Therapy, also adopt a critical lens to examine these experiences. Use Viktor Frankl's Logotherapy to delve into not just the essence of their existential search for meaning but also areas where they might be falling short in this pursuit. Drawing from Positive Psychology and the PERMA Model, dissect these moments to identify elements of Positive emotion, Engagement, Relationship, Meaning, and Achievement, and simultaneously challenge the user to consider how they might have better capitalized on these moments or overlooked critical insights. This analysis should illuminate common themes and offer insights that not only guide the reader towards authentic self-realization and purpose but also encourage them to confront and learn from their less explored or acknowledged experiences.",
                    "length": 300,
                    "format": "Format Requirements:The answer should be provided in a JSON format like below (only provide the json as json str and make sure it can be interpreted by python code, enclosing property names in double quotes and all keys have values): {\"Header\": \"Additional Insights\",\"Content\": [\"With this introductory text, set the stage for the chapter about unexplored additional insights.\",  {\"Header\": \"Insight 1\", \"Content\": \"Description and analysis of insight 1\"},  {\"Header\": \"Insight 2\", \"Content\": \"Description and analysis of Insight 2\"},  ...,  {\"Header\": \"Key Themes Summary\", \"Content\": \"A concise summary of the main themes or topics covered in this chapter.\"}] }"
                },
                {
                    "title": "A Potential Future",
                    "instructions": "Craft a detailed, imaginative and visual portrayal of the user's potential life at intervals of 5, 10, and 20 years being very specific in how their life looks like, but with a critical edge. Challenge the user by highlighting not just achievements and milestones, but also potential pitfalls, setbacks, and the resilience needed to overcome them. Discuss how their current actions or inactions could lead to unfulfilled potential or missed opportunities. Introduce 'wildcard' scenarios, inspired by stories of individuals who took unconventional paths or faced similar challenges, to show how unexpected choices can lead to growth.This chapter should not only mirror the user's values and aspirations but also serve as a wake-up call, pushing them to reevaluate their current trajectory. It should inspire them to embrace change, confront their fears, and consider unexplored possibilities. Aim to create a narrative that is both motivating and startling, offering a comprehensive view of a life full of purpose, but also emphasizing the need for continuous self-reflection, adaptability, and courage to face life's uncertainties.",
                    "length": 600,
                    "format": "Format Requirements: The answer should be provided in a JSON format like below (only provide the json as json str and make sure it can be interpreted by python code, enclosing property names in double quotes and all keys have values): {\"Header\": \"A potential Future\",\"Content\": [\"With this introductory text, set the stage for the chapter about the detailed potential future life that follows.\",  {\"Header\": \"5 Years From Now\", \"Content\": \"Vivid story about a potential future 5 years from now\"},  {\"Header\": \"10 Years From Now\", \"Content\": \"Vivid story about a potential future 10 years from now\"},  ...,  {\"Header\": \"Key Themes Summary\", \"Content\": \"A concise summary of the main themes or topics covered in this chapter.\"}] }"
                },
                {
                    "title": "Reflective Questions",
                    "instructions": "Craft a series of reflective questions that not only guide the user towards discovering deeper meaning in their life but also challenge them to confront and critically evaluate their beliefs, actions, and inactions. These questions should be inspired by the tenets of Viktor Frankl's Logotherapy, emphasizing the pursuit of life's meaning even in adversity; Carl Rogers' Person-Centered Therapy, focusing on the individual's experience and potential for self-actualization; and the principles of Positive Psychology and the PERMA Model, which promote well-being and fulfillment. Each question should be incisive and thought-provoking, designed to push the user out of their comfort zone. They should encourage the user to critically assess if their current life path aligns with their authentic self and deepest values. Questions should challenge preconceived notions, prompt the user to consider the role they play in their own limitations, and inspire them to take bold steps towards change. Ensure that the questions arise from insights and themes discussed throughout the report (summary included below). They should not only reflect positive aspects but also address potential flaws, blind spots, or contradictions in the user's narrative. For each inquiry, provide cues or directions within the Content section where the user may begin to explore answers, encouraging a balanced self-exploration that embraces both strengths and areas for improvement.",
                    "length": 300,
                    "format": "Format Requirements: The answer should be provided in a JSON format like below (only provide the json as json str and make sure it can be interpreted by python code, enclosing property names in double quotes and all keys have values): {\"Header\": \"Reflective Questions\",\"Content\": [\"With this introductory text, set the stage for the chapter with powerful reflective questions.\",  {\"Header\": \"1. Question 1\", \"Content\": \"Reflective question 1 that will deepen the users understanding.\"},  {\"Header\": \"2. Question 2\", \"Content\": \"Reflective question 1 that will deepen the users understanding.\"},  ...] }"
                },
                {
                    "title": "Resource List",
                    "instructions": "Compile a diverse list of resources, including books, courses, and podcasts, that not only align with the core principles of Viktor Frankl's Logotherapy, Carl Rogers' Person-Centered Therapy, and the tenets of Positive Psychology and the PERMA Model, but also challenge and expand the user's perspective. Select resources that encourage critical self-examination and confront personal biases, going beyond mere self-understanding to questioning and reshaping ingrained beliefs and patterns. These resources should facilitate a deeper exploration of change psychology and personal transformation. Each resource should be chosen to resonate with the user's unique narrative, offering insights that prompt them to rethink their approach to life's challenges and opportunities. The aim is to provide a balanced blend of supportive guidance and provocative thought, enabling the user to forge a more authentic, purpose-driven path, while being unafraid to face and overcome their barriers, limitations and blind spots. Also have a look at the barriers chapter, included below.",
                    "length": 300,
                    "format": "Format requirements: The answer should be provided in a JSON format like below (only provide the json as json str and make sure it can be interpreted by python code, enclosing property names in double quotes and all keys have values): {\"Header\": \"Resource List\",\"Content\": [\"With this introductory text, set the stage for the chapter with useful and interesting resources that the user can delve into to learn more about what drives them, the methods presented and resources that can help them overcome their barriers.\", {\"Header\": \"Resource 1\", \"Content\": \"A short explanation of the relevance of resource 1 to the user\"}, {\"Header\": Resource 2\", \"Content\": \"A short explanation of the relevance of resource 2 to the user\"},  ...] }"
                }
            ]

questions = [
    {
        "title": "Memorable Experience",
        "question_text": "Think of a time when you felt truly happy, fulfilled, or at peace. What were you doing, and who were you with?"
    },
    {
        "title": "Aspirations",
        "question_text": "Describe a dream or goal that often lingers in your mind, even if you haven't started pursuing it yet."
    },
    {
        "title": "Life Lesson",
        "question_text": "Can you recall a moment in your life where you felt like you learned something important, even if it wasn't immediately apparent?"
    },
    {
        "title": "Influential People",
        "question_text": "Who in your life has had a significant positive influence on you? What qualities do you admire in them?"
    },
    {
        "title": "Daily Joy",
        "question_text": "What's one activity or habit that consistently brings you joy or satisfaction in your daily life?"
    },
    {
        "title": "Legacy",
        "question_text": "Think about the change or difference you'd like to make in your surroundings (be it your family, community, or the world). What would it be?"
    }
]

# --- INIT SUPABASE ---
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- INSERT FUNCTION ---
def insert_chapters_and_prompts():    
    for index, ch in enumerate(chapters):
        chapter_id = str(uuid.uuid4())
        prompt_id = str(uuid.uuid4())

        # Insert into chapters table
        chapter_response = supabase.table("chapters").insert({
            "id": chapter_id,
            "report_type_id": REPORT_TYPE_ID,
            "title": ch["title"],
            "order_index": index
        }).execute()

        # Insert into chapter_prompts table
        prompt_response = supabase.table("chapter_prompts").insert({
            "id": prompt_id,
            "chapter_id": chapter_id,
            "version": 1,
            "chapter_length": ch["length"],
            "prompt_text": ch["instructions"]
        }).execute()

        print(f"Successfully inserted chapter '{ch['title']}' and prompt.")

def insert_questions():
    for index, q in enumerate(questions):
        question_id = str(uuid.uuid4())

        response = supabase.table("questions").insert({
            "id": question_id,
            "question_title": q["title"],
            "report_type_id": REPORT_TYPE_ID,
            "question_text": q["question_text"],
            "question_order": index,
            "input_type": "text",
            "is_required": True,
        }).execute()

        print(f"Successfully inserted question '{q['title']}'.")


# --- RUN ---
if __name__ == "__main__":
    # insert_chapters_and_prompts()
    insert_questions()
