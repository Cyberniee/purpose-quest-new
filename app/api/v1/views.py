# app/api/v1/views.py
import os, logging
from uuid import UUID
from datetime import datetime, date
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.config.auth_config import supabase_client as supabase
from app.utils.common_utils import validate_data_presence
from app.modules.services.journal.journal_services import get_journal_entry_by_id, get_or_create_today_entry
from app.dependencies.auth import get_current_user_optional, get_current_user_required

router = APIRouter()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)
# directory=os.path.join(BASE_DIR, "static")

# print(f"BASE_DIR: {BASE_DIR}")
# print(f"Static files directory: {directory}")
# router.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

def static_file_url(filename: str) -> str:
    return f"/static/{filename}"

# Configure templates directory
templates = Jinja2Templates(directory="app/templates")
templates.env.globals['static_file_url'] = static_file_url



# Inject header variant
def inject_common_context(request, user, dev_mode=False):
    today_str = date.today().isoformat()

    has_today_entry = False
    if user:
        res = supabase.table("journal_entries") \
            .select("id") \
            .eq("user_id", user["id"]) \
            .eq("entry_date", today_str) \
            .limit(1) \
            .execute()
        has_today_entry = bool(res.data)

    return {
        "request": request,
        "user": user,
        "has_today_entry": has_today_entry,
        "dev_mode": dev_mode,
    }


# --------------------
# Public Page
# --------------------
@router.get("/", response_class=HTMLResponse)
async def homepage(request: Request, user: dict = Depends(get_current_user_optional)):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "user": user,
    })


@router.get("/shop", response_class=HTMLResponse)
async def shop_page(request: Request, user: dict = Depends(get_current_user_required)):
    context = inject_common_context(request, user)
    context["products"] = [
        {"id": 1, "name": "Purpose Report"},
        {"id": 2, "name": "Career Report"}
    ]
    return templates.TemplateResponse("shop.html", context)

# --------------------
# Questionnaire Page (logged in)
# --------------------
@router.get("/questionnaire/{product_id}", response_class=HTMLResponse)
async def questionnaire_page(
    product_id: int,
    request: Request,
    user: dict = Depends(get_current_user_required)
):
    questions = [
        {"id": 1, "text": "What motivates you?"},
        {"id": 2, "text": "How do you handle failure?"}
    ]
    context = inject_common_context(request, user)
    context["questions"] = questions
    context["product_id"] = product_id
    return templates.TemplateResponse("questionnaire.html", context)

# --------------------
# Post-purchase: Success / Cancel / Error
# --------------------
@router.get("/purchase/{status}", response_class=HTMLResponse)
async def purchase_status_page(
    status: str,
    request: Request,
    user: dict = Depends(get_current_user_required)
):
    if status not in ["success", "cancel", "error"]:
        raise HTTPException(status_code=404, detail="Page not found")

    context = inject_common_context(request, user)
    return templates.TemplateResponse(f"{status}.html", context)


# --------------------
# Account Page (logged in) ### IF THE USER IS NOT LOGGED IN, REDIRECT TO SIGN-IN PAGE...
# --------------------
@router.get("/account", response_class=HTMLResponse)
async def account_page(
    request: Request,
    user: dict = Depends(get_current_user_optional)
):
    ### DEV ###
    dev_mode = True
    ### DEV ###
    if not user:
        return RedirectResponse(url="/sign-in")

    context = inject_common_context(request, user, dev_mode)

    return templates.TemplateResponse("account.html", context)

@router.get("/account-settings", response_class=HTMLResponse)
async def account_page(
    request: Request,
    user: dict = Depends(get_current_user_optional)
):
    ### DEV ###
    dev_mode = True
    ### DEV ###
    if not user:
        return RedirectResponse(url="/sign-in")

    context = inject_common_context(request, user, dev_mode)

    return templates.TemplateResponse("settings.html", context)


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    user: dict = Depends(get_current_user_optional)
):
    ### DEV ###
    dev_mode = True
    ### DEV ###
    if not user:
        return RedirectResponse(url="/sign-in")

    context = inject_common_context(request, user, dev_mode)

    return templates.TemplateResponse("dashboard.html", context)



# --------------------
# Product pages
# --------------------

@router.get("/product/{token_id}", response_class=HTMLResponse)
async def open_product_token_page(
    request: Request,
    token_id: str,
    user: dict = Depends(get_current_user_required)
):
    try:
        # Fetch access token and validate ownership
        token_res = supabase.table("report_access_tokens") \
            .select("*") \
            .eq("access_token", token_id) \
            .eq("user_id", str(user["id"])) \
            .single() \
            .execute()

        if not validate_data_presence(token_res):
            return RedirectResponse(url="/account")

        token = token_res.data
        logger.info(f"Token data: {token}")
        
        if token["status"] == "done":
            return RedirectResponse(f"/report/{token['report_id']}")

        report_type_id = token["report_type_id"]

        # Create or retrieve input session
        session_res = supabase.table("report_input_sessions") \
            .select("*") \
            .eq("user_id", str(user["id"])) \
            .eq("report_type_id", str(report_type_id)) \
            .eq("report_access_token_id", token["id"]) \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()

            
            
        # If session exists, use it; otherwise, create a new one
        if session_res.data:
            input_session = session_res.data[0]

            update_fields = {}
            if token["first_open"]:
                update_fields["first_open"] = False

            if not token.get("input_session_id"):
                update_fields["input_session_id"] = input_session["id"]

            if update_fields:
                supabase.table("report_access_tokens") \
                    .update(update_fields) \
                    .eq("id", token["id"]) \
                    .execute()

            
        else:
            create_res = supabase.table("report_input_sessions").insert({
                "user_id": str(user["id"]),
                "report_type_id": str(report_type_id),
                "report_access_token_id": token["id"],
            }).execute()
            
            input_session = create_res.data[0]
            supabase.table("report_access_tokens") \
                .update({"status": "in progress", "input_session_id": input_session['id']}) \
                .eq("id", token["id"]) \
                .execute()

        # Get questions
        questions_res = supabase.table("questions") \
            .select("id, question_title, question_text, is_required") \
            .eq("report_type_id", str(report_type_id)) \
            .order("question_order", desc=False) \
            .execute()

        context = inject_common_context(request, user, dev_mode=True)
        context.update({
            "questions": questions_res.data,
            "session_id": input_session["id"],
            "token_id": token_id,
            "report_type_id": report_type_id,
            "first_open": token["first_open"]
        })
        return templates.TemplateResponse("product.html", context)

    except Exception as e:
        logger.error(f"Error opening product page for token {token_id}: {e}")
        return RedirectResponse(url="/account")

@router.get("/report/{report_id}", response_class=HTMLResponse)
async def report_page(request: Request, report_id: str, user: dict = Depends(get_current_user_required)):
    report = supabase.table("reports").select("*, report_input_sessions(user_id)").eq("id", report_id).eq("report_input_sessions.user_id", user["id"]).single().execute()
    if not report.data:
        raise HTTPException(404, detail="Report not found")

    # Fetch chapters
    chapters = supabase.table("report_chapters").select("content, order_index, chapters(title)").eq("report_id", report_id).order("order_index").execute()

    context = inject_common_context(request, user, dev_mode=True)
    context.update({
        "report": report.data,
        "chapters": chapters.data
    })

    return templates.TemplateResponse("pq_report.html", context)

# --------------------
# Jounraling pages
# --------------------

@router.get("/journal/archive", response_class=HTMLResponse)
async def archive_page(
    request: Request,
    user: dict = Depends(get_current_user_optional)
):
    logger.info('rendering archive page')
    ### DEV ###
    dev_mode = True
    ### DEV ###
    if not user:
        return RedirectResponse(url="/sign-in")

    context = inject_common_context(request, user, dev_mode)

    return templates.TemplateResponse("archive.html", context)



@router.get("/journal/today", response_class=HTMLResponse)
async def entry_page(
    request: Request,
    user: dict = Depends(get_current_user_optional)
):
    ### DEV ###
    dev_mode = True
    ### DEV ###
    if not user:
        return RedirectResponse(url="/sign-in")

    context = inject_common_context(request, user, dev_mode)

    return templates.TemplateResponse("journal_entry.html", context)


@router.get("/journal/{entry_id}", response_class=HTMLResponse)
async def open_journal_entry(
    entry_id: str,
    request: Request,
    user=Depends(get_current_user_optional),
):
    
    entry = await get_journal_entry_by_id(entry_id, user["id"])

    logger.info(f'entry we got: {entry}')
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    entry_date_obj = datetime.strptime(entry["entry_date"], "%Y-%m-%d").date()

    return templates.TemplateResponse(
        "journal_entry.html",
        {
            "request": request,
            "entry_id": entry["id"],
            "entry_date": entry["entry_date"],
            "content": entry["content"],
            "display_date": entry_date_obj.strftime("%A, %B %d, %Y"),
        },
    )



# --------------------
# utility Pages
# --------------------
@router.get("/success", response_class=HTMLResponse)
async def success_page(request: Request, user: dict = Depends(get_current_user_optional)):
    if not user:
        return RedirectResponse("/sign-in")
    context = inject_common_context(request, user)
    return templates.TemplateResponse("success.html", context)

@router.get("/cancel", response_class=HTMLResponse)
async def cancel_page(request: Request, user: dict = Depends(get_current_user_optional)):
    if not user:
        return RedirectResponse("/sign-in")
    context = inject_common_context(request, user)
    return templates.TemplateResponse("cancel.html", context)

@router.get("/refund", response_class=HTMLResponse)
async def cancel_page(request: Request, user: dict = Depends(get_current_user_optional)):
    context = inject_common_context(request, user)
    return templates.TemplateResponse("refund_policy.html", context)

@router.get("/terms-of-service", response_class=HTMLResponse)
async def cancel_page(request: Request, user: dict = Depends(get_current_user_optional)):
    context = inject_common_context(request, user)
    return templates.TemplateResponse("terms_of_service.html", context)



# --------------------
# Auth Pages
# --------------------

@router.get("/sign-in", response_class=HTMLResponse)
async def sign_in_get(request: Request, user: dict = Depends(get_current_user_optional)):
    if user:
        return RedirectResponse("/account/")
    context = inject_common_context(request)
    return templates.TemplateResponse("user_signin.html", context)

@router.get("/finish-sign-up", response_class=HTMLResponse)
async def auth_sign_in(request: Request, user: dict = Depends(get_current_user_optional)):
    '''Displays the magic-link sign-in page for Habit Hero users. Checks if the user is logged in and passes the status to the template.

        Request Type: GET
        Response Class: HTMLResponse
        Path: /auth-sign-in
        Purpose: Display the sign-in page for Habit Hero users using a magic link.
        Dependencies: user_info from get_user_auth_status
    '''
    context = inject_common_context(request, user)
    return templates.TemplateResponse("_user_access.html", context)



@router.get("/sign-up", response_class=HTMLResponse)
async def sign_up_get(request: Request, user: dict = Depends(get_current_user_optional)):
    if user:
        return RedirectResponse("/account/")
    context = inject_common_context(request)
    return templates.TemplateResponse("user_register.html", context)


@router.get("/recovery", response_class=HTMLResponse)
async def recovery_get(request: Request):
    context = inject_common_context(request)
    return templates.TemplateResponse("user_password_reset.html", context)


@router.get("/password-reset", response_class=HTMLResponse)
async def password_reset(request: Request, user: dict = Depends(get_current_user_optional)):
    context = inject_common_context(request, user)
    return templates.TemplateResponse("user_password_reset.html", context)