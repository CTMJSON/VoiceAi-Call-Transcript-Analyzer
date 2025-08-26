# VoiceAi-Call-Transcript-Analyzer
This script automates the process of retrieving customer call transcripts from the CallTrackingMetrics (CTM) API and analyzes them using the OpenAI API (GPT-4). Specifically designed for businesses using a voice AI receptionist, it provides actionable feedback on AI agent performance and guidance for prompt improvements.

**Key Features:**

Fetches call records (with transcripts and summaries) from CTM using customizable agent/user IDs.

Submits each transcript, summary, and the current voice AI assistant’s prompt instructions to OpenAI’s GPT API for evaluation.

The AI dynamically assesses each call for conversational flow, clarity, instruction-following, and caller satisfaction.

Offers clear, bullet-pointed recommendations for updating or fine-tuning your voice AI prompt based on real interactions.

Outputs all data, analysis, and recommendations to a CSV file for reporting or further review.

Prints full API responses to assist with debugging data extraction.



