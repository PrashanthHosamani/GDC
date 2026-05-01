from openai import OpenAI
from models import Fee, Placement, Course, Result, Association
from seed import CHATBOT_RESPONSES
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.environ.get("OPENROUTER_API_KEY", "missing-key"),
)

def get_db_context_string(student=None):
    context = "COLLEGE DATA:\n"

    # Fees - group by branch/year
    fees = Fee.query.all()
    context += "Fees:\n"
    for f in fees:
        context += f"  {f.branch.upper()} Yr{f.year}: ₹{f.amount} (due {f.due_date})\n"

    # Only upcoming placements
    placements = Placement.query.filter_by(status='upcoming').all()
    if placements:
        context += "Upcoming Placements:\n"
        for p in placements:
            context += f"  {p.company_name} | {p.job_role} | {p.drive_date} | Eligible: {p.eligible_branches} | ₹{p.salary_min}-{p.salary_max}\n"
    else:
        context += "Upcoming Placements: None currently.\n"

    # Courses - just unique branches
    courses = Course.query.all()
    branches = list({c.branch.upper() for c in courses})
    context += f"Courses offered: {', '.join(branches)}\n"

    # Associations
    associations = Association.query.all()
    if associations:
        context += "Clubs/Associations: " + ", ".join(a.name for a in associations) + "\n"

    # Student-specific info
    if student:
        context += f"\nStudent: {student.name}, {student.branch.upper()}, Year {student.year}\n"
        results = Result.query.filter_by(student_id=student.id).order_by(Result.semester).all()
        if results:
            context += "Results: " + ", ".join(f"Sem{r.semester} {r.subject}: {r.marks}/{r.max_marks}({r.grade})" for r in results) + "\n"

    # Key static facts only (not every response)
    key_facts = ['attendance', 'library', 'contact', 'admission', 'scholarship']
    context += "Key Info:\n"
    for key, response in CHATBOT_RESPONSES.items():
        if any(k in key for k in key_facts):
            context += f"  {response}\n"

    return context

def get_chatbot_response(user_query, student=None, chat_history=None):
    if chat_history is None:
        chat_history = []
        
    db_context = get_db_context_string(student)
    
    system_prompt = f"""You are GDC Buddy, a helpful, friendly, and knowledgeable assistant specifically for Govinda Dasa College (GDC).
You must use the following live database context and general college information to answer the user's question accurately.

STRICT BOUNDARIES:
- You are ONLY allowed to answer questions related to Govinda Dasa College, its courses, admissions, fees, placements, student results, associations, and campus facilities.
- If a user asks a question completely unrelated to the college, education, or their student life (e.g., "tell me a joke", "write code", "recipe for cake"), you MUST politely decline to answer by stating: "I am a specialized assistant for Govinda Dasa College and can only help with college-related queries."
- When discussing Fees, DO NOT mention the due date unless the user explicitly asks for deadlines or when the fees are due.
- If the answer to a college-related question is not in the context, politely let them know you don't have that specific information but provide the contact details from the general info.
- If the user asks a general conversational question (like "hello", "how are you"), answer warmly but bring the topic back to the college.
- Do not expose the fact that you are being fed a 'DATABASE CONTEXT', just speak naturally as if you know it.
- Format your answers using markdown for readability (bolding, bullet points). 
- CRITICAL INSTRUCTION: Your answers MUST be extremely concise, direct, and short. Do not write lengthy paragraphs. Provide only the exact information requested without conversational filler or fluff. Ensure absolute accuracy.

{db_context}
"""

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(chat_history[-10:]) # keep last 10 messages from frontend history
    messages.append({"role": "user", "content": user_query})
    
    try:
        stream = client.chat.completions.create(
          model="deepseek/deepseek-chat",
          messages=messages,
          stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                yield f"data: {content}\n\n"
                
    except Exception as e:
        print(f"OpenRouter Error: {e}")
        yield f"data: I'm having trouble connecting to my AI brain right now. Please try again later!\n\n"
