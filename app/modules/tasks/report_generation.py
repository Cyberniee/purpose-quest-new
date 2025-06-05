# app/modules/tasks/report_generation.py

from app.celery_worker import celery_app
from app.config.auth_config import supabase_client as supabase
from app.core.ai_client import get_openai_client
from app.config import config
import logging, time, random

logger = logging.getLogger(__name__)

openai = get_openai_client()

LOREM_TEXTS = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer nec odio. Praesent libero. Sed cursus ante dapibus diam.",
    "Sed nisi. Nulla quis sem at nibh elementum imperdiet. Duis sagittis ipsum. Praesent mauris.",
    "Fusce nec tellus sed augue semper porta. Mauris massa. Vestibulum lacinia arcu eget nulla.",
    "Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.",
    "Curabitur sodales ligula in libero. Sed dignissim lacinia nunc. Curabitur tortor. Pellentesque nibh."
]


@celery_app.task
def generate_report_chapter(chapter_data):
    try:
        # Extract necessary data from chapter_data
        report_type_id = chapter_data["report_type_id"]
        user_answers = chapter_data["user_answers"]
        prompt_template = chapter_data["prompt"]
        report_id = chapter_data["report_id"]
        chapter_id = chapter_data["chapter_id"]
        chapter_prompt_id = chapter_data["chapter_prompt_id"]
        order_index = chapter_data["order_index"]

        # Combine answers into one string
        answers_text = "\n".join(
            [f"{a['question']}: {a['answer']}" for a in user_answers]
        )
        final_prompt = prompt_template.replace("{{answers}}", answers_text)

        
        # Generate chapter content using OpenAI API
        ai_response = openai.chat.completions.create(
            model=config.openai.model,
            messages=[{"role": "user", "content": final_prompt}],
            temperature=config.openai.temperature,
            frequency_penalty=config.openai.frequency_penalty,
            presence_penalty=config.openai.presence_penalty,
        )

        content = ai_response.choices[0].message.content.strip()


        supabase.table("report_chapters").insert({
            "report_id": report_id,
            "chapter_id": chapter_id,
            "chapter_prompt_id": chapter_prompt_id,
            "order_index": order_index,
            "content": content
        }).execute()

        logger.info(f"Chapter {chapter_id} saved to report {report_id}")
        
        # Count how many chapters are already done for this report
        done_count_res = supabase.table("report_chapters") \
            .select("id", count="exact") \
            .eq("report_id", report_id) \
            .execute()

        supabase.table("reports").update({
            "progress": done_count_res.count
        }).eq("id", report_id).execute()
        
        # Mark report as done if all chapters are completed
        total_chapters_res = supabase.table("chapters").select("id").eq("report_type_id", report_type_id).execute()
        if done_count_res.count == len(total_chapters_res.data):
            supabase.table("reports").update({"status": "completed"}).eq("id", report_id).execute()


    except Exception as e:
        logger.error(f"Failed to generate chapter: {e}")
        

@celery_app.task
def generate_report_chapter_mock(chapter_data):
    try:
        # Simulate OpenAI API delay
        time.sleep(10)

        # Extract necessary data
        report_type_id = chapter_data["report_type_id"]
        report_id = chapter_data["report_id"]
        chapter_id = chapter_data["chapter_id"]
        chapter_prompt_id = chapter_data["chapter_prompt_id"]
        order_index = chapter_data["order_index"]

        # Generate mock content
        content = random.choice(LOREM_TEXTS)

        # Insert into DB
        supabase.table("report_chapters").insert({
            "report_id": report_id,
            "chapter_id": chapter_id,
            "chapter_prompt_id": chapter_prompt_id,
            "order_index": order_index,
            "content": content
        }).execute()

        logger.info(f"[MOCK] Chapter {chapter_id} saved to report {report_id}")

        # Update progress
        done_count_res = supabase.table("report_chapters") \
            .select("id", count="exact") \
            .eq("report_id", report_id) \
            .execute()

        supabase.table("reports").update({
            "progress": done_count_res.count
        }).eq("id", report_id).execute()

        # Complete if all chapters are done
        total_chapters_res = supabase.table("chapters") \
            .select("id") \
            .eq("report_type_id", report_type_id) \
            .execute()

        if done_count_res.count == len(total_chapters_res.data):
            supabase.table("reports").update({
                "status": "completed"
            }).eq("id", report_id).execute()

    except Exception as e:
        logger.error(f"[MOCK] Failed to generate chapter: {e}")