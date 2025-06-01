import logging
import pytz
from fastapi import APIRouter, Request, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from app.utils.common_utils import validate_data_presence
from app.config.auth_config import supabase_client as supabase
from app.modules.tasks.report_generation import generate_report_chapter
from app.modules.services.auth.auth_utils import AuthenticationUtils

logger = logging.getLogger(__name__)
report_router = APIRouter()

class SaveAnswerPayload(BaseModel):
    input_session_id: str | None = None  # Allow null for first-time users
    question_id: str
    answer_text: str
    report_type_id: str
    user_id: str

class GenerationRequest(BaseModel):
    token_id: str


@report_router.get("/answers/{session_id}")
async def get_saved_answers(session_id: UUID):
    try:
        response = supabase.table("user_answers") \
            .select("question_id, answer_text") \
            .eq("input_session_id", str(session_id)) \
            .execute()
        data = response.data if response.data else []
        return {"status": "ok", "answers": data}
    except Exception as e:
        logger.error(f"Error fetching answers for session {session_id}: {e}")
        return {"status": "error", "message": str(e)}


@report_router.post("/answer")
async def autosave_answer(payload: SaveAnswerPayload):
    try:
        # Step 1: Create session if not provided
        input_session_id = payload.input_session_id

        if not input_session_id:
            session_res = supabase.table("report_input_sessions").insert({
                "user_id": str(payload.user_id),
                "report_type_id": str(payload.report_type_id),
                "created_at": datetime.now(datetime.timezone.utc).isoformat()
            }).execute()

            if not validate_data_presence(session_res):
                raise Exception("Failed to create input session")

            input_session_id = session_res.data[0]["id"]
            logger.info(f"input session: {input_session_id}")

        # Step 2: Check for existing answer
        existing = supabase.table("user_answers") \
            .select("id") \
            .eq("input_session_id", str(input_session_id)) \
            .eq("question_id", str(payload.question_id)) \
            .limit(1) \
            .execute()
        logger.info(f"Existing answer check: {existing.data}")


        if existing.data:
            # Step 3a: Update existing answer
            supabase.table("user_answers").update({
                "answer_text": payload.answer_text,
                "created_at": datetime.now(pytz.timezone('utc')).isoformat()
            }).eq("id", existing.data[0]["id"]).execute()
        else:
            # Step 3b: Insert new answer
            supabase.table("user_answers").insert({
                "input_session_id": str(input_session_id),
                "question_id": str(payload.question_id),
                "answer_text": payload.answer_text,
                "created_at": datetime.now(pytz.timezone('utc')).isoformat()
            }).execute()

        return {"status": "ok", "input_session_id": input_session_id}

    except Exception as e:
        logger.error(f"Autosave failed: {e}")
        return {"status": "error", "message": str(e)}



@report_router.post("/start-generation")
async def trigger_report_generation(request: GenerationRequest, user=Depends(AuthenticationUtils.get_authenticated_user)):
    token_id = request.token_id
    # 1. Validate token
    token_res = supabase.table("report_access_tokens").select("*").eq("access_token", token_id).eq("user_id", user["id"]).single().execute()
    if not token_res.data:
        raise HTTPException(status_code=404, detail="Token not found")
    
    token = token_res.data
    session_id = token["input_session_id"]
    report_type_id = token["report_type_id"]

    # 2. Update token status
    supabase.table("report_access_tokens").update({"status": "generating"}).eq("id", token["id"]).execute()

    # 3. Create report
    report_res = supabase.table("reports").insert({
        "report_type_id": report_type_id,
        "input_session_id": session_id,
        "status": "generating",
        "version": 1,
        "generated_at": datetime.now(pytz.timezone('utc')).isoformat()
    }).execute()

    report_id = report_res.data[0]["id"]

    # 4. Fetch answers
    answers_res = supabase.table("user_answers").select("question_id, answer_text, questions(question_text)").eq("input_session_id", session_id).execute()
    user_answers = []
    for a in answers_res.data:
        question_text = a.get("questions", {}).get("question_text", "").strip()
        answer_text = a.get("answer_text", "").strip()

        if question_text and answer_text:
            user_answers.append({
                "question": question_text,
                "answer": answer_text
            })


    # 5. Fetch chapters and prompts
    chapters_res = supabase.table("chapters").select("id, order_index").eq("report_type_id", report_type_id).order("order_index").execute()
    
    for chapter in chapters_res.data:
        prompt_res = supabase.table("chapter_prompts").select("id, prompt_text").eq("chapter_id", chapter["id"]).order("version", desc=True).limit(1).execute()
        prompt = prompt_res.data[0]

        # 6. Dispatch task
        generate_report_chapter.apply_async(
            args=[{
                "session_id": session_id,
                "report_id": report_id,
                "report_type_id": report_type_id,
                "chapter_id": chapter["id"],
                "chapter_prompt_id": prompt["id"],
                "order_index": chapter["order_index"],
                "prompt": prompt["prompt_text"],
                "user_answers": user_answers
            }],
            queue="reports"
        )

    return {"status": "started", "report_id": report_id}

@report_router.get("/progress/{token_id}")
async def get_report_progress(token_id: str, user=Depends(AuthenticationUtils.get_authenticated_user)):
    token_res = supabase.table("report_access_tokens") \
        .select("report_id, report_type_id") \
        .eq("access_token", token_id) \
        .eq("user_id", user["id"]) \
        .single().execute()

    if not token_res.data:
        raise HTTPException(status_code=404, detail="Token not found")

    report_id = token_res.data["report_id"]
    report_type_id = token_res.data["report_type_id"]

    report_res = supabase.table("reports") \
        .select("progress, status") \
        .eq("id", report_id) \
        .single().execute()

    total_chapters_res = supabase.table("chapters").select("id").eq("report_type_id", report_type_id).execute()
    total_chapters = len(total_chapters_res.data)

    return {
        "progress": report_res.data["progress"],
        "total": total_chapters,
        "status": report_res.data["status"]
    }
