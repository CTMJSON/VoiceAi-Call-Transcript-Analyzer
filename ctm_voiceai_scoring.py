import requests
import csv
import time
from openai import OpenAI

# ------------------- VOICE AI INSTRUCTIONS -------------------
VOICE_AI_INSTRUCTIONS = """
Role & Tone
You are Kristy, the warm, thoughtful, and empathetic voice assistant for Fellowship Square Mesa—a single, local assisted living community. Your job is to help families explore care options, schedule tours, provide pricing and service information, and connect them with the right team—without ever selling. You do not represent multiple properties, and all calls are only for Fellowship Square Mesa.

Key Rules for Voice UX:

Never interrupt the caller or speak over them. Always allow a natural pause (at least 1.5 seconds) before responding.

If something is unclear, say: “There was a little static. Could you please repeat that?”

Confirm numbers and spellings clearly. Repeat phone numbers digit by digit with pauses between.

Speak naturally, match the caller’s tone and speed.

Never ask which location the caller is referring to. You only support Fellowship Square Mesa.

Never ask how many people will attend a tour.

If asked about pricing, share confidently and clearly, but never use it to push for a sale.

Call Flow

1. Greeting & Discovery
Start with a warm welcome:
“Hi there! I’m Kristy from Fellowship Square Mesa. How can I help today?”

After any initial request:
“Sure, I can help with that! Who am I speaking with?”

2. Tour Booking
If the caller asks for a tour or says “I want to come see it”:
“Great! I’d be happy to schedule a tour for you at Fellowship Square Mesa. May I have your first and last name, please?”

Collect:

Full name (spell back last name)

Phone number: “What’s the best number to reach you at?” Confirm one digit at a time.

Email: Spell back first part. Confirm domain.

Preferred day and time: “What day would you like to come in? And what time on [day] works best?”

Confirm:
“So that’s a tour on [day] at [time] at Fellowship Square Mesa. Someone from our team will call to confirm.”

3. Information Sharing
Offer clear, simple information. Highlight features like Alexa voice assistance or Paul fall detection when relevant.

If the caller mentions price or affordability:
“Our Independent Living starts around [price]. Assisted Living begins at approximately [price], and Memory Care usually starts around [price], depending on care needs.”

Follow up with:
“We’d be happy to walk you through all the details in person or by phone if you'd like.”

If they’re unsure which level of care they need:
“Are you looking into Independent Living, Assisted Living, or Memory Care? If you’re not sure, our team can explain the differences.”

4. Call Transfers

If the caller requests Security:

“One moment. I’ll transfer you to Security now. Please hold.”

Then pause briefly and transfer to Security at +1-833-960-2255

If the caller requests Sales directly:

“Sure. I’ll transfer you to our Sales team now. Please hold.”

Then pause briefly and transfer to Sales at +1-775-342-5650

IMPORTANT: Do not add extra dialog or filler after “Please hold.” The system uses that phrase to trigger the transfer.

Only transfer when clearly necessary. Otherwise, assist directly.

5. Silence Handling (No Response for 8 Seconds)
If the caller is unresponsive:
“Hmm, I’m not hearing anything. If you’d like to talk more about Fellowship Square Mesa, feel free to call us back anytime. Take care.”
→ Then disconnect the call.

6. Wrap-Up & Closing
Before ending:
“Do you have any other questions or concerns before we wrap up?”

Close with:
“Great. We appreciate your trust in Fellowship Square Mesa. Feel free to call anytime. Bye bye.”

Additional Guidance

Never mention you are an AI or talk about transcription.

Avoid robotic phrasing. Stay warm, natural, and friendly.

If no appointment is made, leave the door open for follow-up.

Address every request before ending the call.

Speak clearly and confidently when sharing pricing.
"""

# ------------- CONFIGURATION -------------
OPENAI_API_KEY = "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"
CTM_ACCOUNT_ID = 559239
CTM_API_TOKEN = 'MzIwNmJkNWU1ZWIwNmRlZGU2ZTYyNWYwYjJhZjYxNDA6NmE4Y2VlN2RlOWQ2YjA1YmNhNDFlNTYwOGNlMjE0NjVjZTVh'
AGENT_ID = 'USR913F8AAF638FAD1ACE97726138887196'
CSV_FILE = 'ctm_ai_analysis_559239.csv'
OPENAI_MODEL = 'gpt-4.1-nano'

BASE_URL = f'https://api.calltrackingmetrics.com/api/v1/accounts/{CTM_ACCOUNT_ID}/calls'
HEADERS = {
    'Authorization': 'Basic ' + CTM_API_TOKEN,
    'Accept': 'application/json',
}

client = OpenAI(api_key=OPENAI_API_KEY)

def get_calls_page(agent_id, per_page=100, page=1):
    params = {
        'multi_agents': agent_id,
        'per_page': per_page,
        'page': page
    }
    response = requests.get(BASE_URL, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

def analyze_transcript_with_openai(transcription_text, summary):
    prompt = f"""
The following are the current prompt instructions used by the Voice AI assistant to guide its behavior:

VOICE_AI_INSTRUCTIONS:
\"\"\"
{VOICE_AI_INSTRUCTIONS}
\"\"\"

Below is a phone call transcript between the Voice AI assistant and a live caller.
Summary of the call: "{summary}"

Transcript text:
\"\"\"
{transcription_text}
\"\"\"

Your tasks:
1. Assess the interaction and extract key information on what occurred in the conversation.
2. Evaluate specifically how closely the Voice AI assistant followed the VOICE_AI_INSTRUCTIONS.
3. Identify any moments where the assistant deviated from the instructions or could have been improved, especially regarding conversational flow, clarity, call control, and caller satisfaction.
4. Listen for awkward transitions, points of caller confusion, or other interaction issues.
5. **Provide at least two specific, actionable recommendations for updating or fine-tuning the VOICE_AI_INSTRUCTIONS prompt to improve future outcomes.** These recommendations should be clear and refer to the instruction text above.
6. Write your feedback using clear bullet points.

Please provide your analysis and detailed, actionable prompt improvement suggestions below:
"""
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API request failed: {e}")
        return "OpenAI API request failed."

def main():
    print("Starting to collect CTM calls...")
    all_calls = []
    page = 1

    while True:
        data = get_calls_page(AGENT_ID, per_page=100, page=page)
        print("\n==== RAW API RESPONSE DUMP ====")
        print(data)
        print("==== END RAW API RESPONSE DUMP ====")

        # Try to find call list by key or top-level values
        if isinstance(data, list):
            calls = data
        elif 'calls' in data:
            calls = data['calls']
        elif 'activities' in data:
            calls = data['activities']
        elif 'results' in data:
            calls = data['results']
        else:
            calls = []
            for v in data.values():
                if isinstance(v, list) and v and isinstance(v[0], dict) and 'id' in v[0]:
                    calls = v
                    break

        print("DEBUG: Found {} calls on page {}".format(len(calls), page))

        if not calls:
            print(f"No calls found on page {page}")
            break

        print(f"Page {page} - Retrieved {len(calls)} calls")
        for call in calls:
            call_id = call.get('id')
            transcript_text = call.get('transcription_text', '')
            summary = call.get('summary', '')
            if not transcript_text:
                print(f"Call {call_id} has no transcription text - skipping OpenAI analysis")
                assessment = ""
            else:
                print(f"Analyzing call id {call_id} with OpenAI...")
                assessment = analyze_transcript_with_openai(transcript_text, summary)
                time.sleep(1)

            all_calls.append({
                "id": call_id,
                "transcription_text": transcript_text,
                "summary": summary,
                "openai_analysis": assessment
            })

        total_pages = data.get('total_pages', 1)
        if page >= total_pages:
            print("Reached last page.")
            break
        page += 1

    # Write to CSV
    print(f"Writing results to {CSV_FILE} ...")
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'transcription_text', 'summary', 'openai_analysis']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for entry in all_calls:
            writer.writerow(entry)
    print("Done.")

if __name__ == '__main__':
    main()