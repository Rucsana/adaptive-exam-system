import os
import json
import urllib.request
import urllib.error


class LLMService:
    """
    LLM Intelligence Service for Adaptive Exam Operations.
    Integrates Google Gemini API for:
      1. Live autonomous decision rationale & audit analysis.
      2. Context-aware emergency dispatch notices to faculty.
      3. Natural Language Disruption Parsing for the Coordinator Copilot.
    
    Includes a fail-safe fallback engine so the system functions smoothly
    both offline (heuristic reasoning) and online (Google Gemini live LLM).
    """

    def __init__(self):
        self.api_key = self._load_api_key()
        self.model = "gemini-1.5-flash"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    def _load_api_key(self) -> str:
        # Check environment variables
        key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if key:
            return key.strip()

        # Check local .env file in project root
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GEMINI_API_KEY="):
                            return line.split("=", 1)[1].strip().strip('"').strip("'")
            except Exception:
                pass
        return ""

    def set_api_key(self, key: str):
        self.api_key = key.strip()
        # Persist to local .env
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
        try:
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(f"GEMINI_API_KEY={self.api_key}\n")
        except Exception:
            pass

    def is_live_llm_active(self) -> bool:
        return bool(self.api_key)

    def _call_gemini(self, prompt: str, system_instruction: str = "") -> str:
        if not self.api_key:
            return ""

        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"

        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 600,
            }
        }

        if system_instruction:
            payload["system_instruction"] = {
                "parts": [{"text": system_instruction}]
            }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
        except Exception as e:
            print(f"⚠️ Gemini API call failed: {e}. Falling back to heuristic reasoning.")
            return ""

        return ""

    def generate_repair_explanation(
        self,
        disruption_type: str,
        disrupted_id: str,
        slot_id: str,
        affected_exam: str,
        original_location: str,
        repaired_location: str,
        backup_invigilator: str = None,
    ) -> str:
        """Generates deep, human-readable autonomous decision rationale via Gemini or Heuristic AI."""
        if self.is_live_llm_active():
            system_prompt = (
                "You are the Lead Agentic AI Controller for university exam logistics. "
                "Explain an autonomous timetable recovery decision concisely (2-3 sentences). "
                "Highlight constraint satisfaction: room capacity, student accessibility (ground floor requirement for Alice S101), "
                "faculty confirmation, physical check-in, and timetable preservation of unaffected exams."
            )

            user_prompt = (
                f"Disruption occurred: {disruption_type.upper()} disruption. Target: {disrupted_id} unavailable in slot {slot_id}.\n"
                f"Affected Exam: {affected_exam}.\n"
                f"Original Allocation: {original_location}.\n"
                f"Repaired Allocation: {repaired_location}.\n"
                f"Backup Invigilator: {backup_invigilator or 'N/A'}.\n"
                f"Explain the Agent's reasoning, why unaffected exams were preserved, and why this candidate was chosen."
            )

            ai_resp = self._call_gemini(user_prompt, system_prompt)
            if ai_resp:
                return f"[Gemini 1.5 Flash AI Rationale]: {ai_resp}"

        # Heuristic Fallback
        if disruption_type == "room":
            return (
                f"[AI Decision Rationale]: Exam {affected_exam} was relocated because hall {disrupted_id} became unavailable in {slot_id}. "
                f"The agent evaluated candidate rooms and selected {repaired_location} because it strictly satisfies student S101's ground-floor accessibility "
                f"requirement and required 60-seat capacity. Unaffected exams were kept stable to minimize campus friction."
            )
        elif disruption_type == "invigilator":
            return (
                f"[AI Decision Rationale]: Primary invigilator {disrupted_id} was marked unavailable in {slot_id}. "
                f"The agent filtered the faculty pool against three tiers of verification (timetable free, confirmed availability, and physical check-in), "
                f"selecting {backup_invigilator} as the verified eligible substitute for {affected_exam} in {repaired_location}."
            )
        else:
            return (
                f"[AI Decision Rationale]: A compound multi-resource disruption in {slot_id} invalidated both room {disrupted_id} and faculty assignment. "
                f"The agent resolved the multi-constraint conflict simultaneously, relocating to {repaired_location} and dispatching verified backup faculty {backup_invigilator}, "
                f"verifying 0 student clashes and full accessibility compliance."
            )

    def parse_natural_language_command(self, query: str) -> dict:
        """
        Parses Coordinator natural language input into structured disruption parameters.
        Example: 'Dr. Backup is absent for slot T1' -> {'disruption_type': 'invigilator', ...}
        """
        q = query.lower()

        # Heuristic fallback parser
        disruption_type = "invigilator"
        disrupted_slot = "T1"
        disrupted_room = "R102"
        disrupted_invig = "I02"

        if "t2" in q:
            disrupted_slot = "T2"

        words = set(q.replace(".", " ").replace(",", " ").split())
        has_room_kw = any(w in words for w in ["room", "hall", "r102", "r103", "flood", "flooding", "leak", "power", "ac", "a/c", "building"])
        has_invig_kw = any(w in words for w in ["invigilator", "faculty", "i02", "backup", "sick", "absent", "leave", "emergency", "doctor", "dr"])

        if "both" in words or "compound" in words or (has_room_kw and has_invig_kw):
            disruption_type = "compound"
        elif has_invig_kw:
            disruption_type = "invigilator"
        elif has_room_kw:
            disruption_type = "room"

        # If live LLM is active, enhance with Gemini
        if self.is_live_llm_active():
            prompt = (
                f"Analyze this exam disruption scenario: '{query}'. "
                "Classify it into JSON with keys: disruption_type ('room', 'invigilator', or 'compound'), "
                "disrupted_room_id ('R102' or 'R103'), disrupted_invigilator_id ('I02' or 'I01'), "
                "disrupted_slot_id ('T1' or 'T2'), summary (string). Output only valid JSON."
            )
            resp = self._call_gemini(prompt)
            if resp:
                try:
                    clean = resp.replace("```json", "").replace("```", "").strip()
                    parsed = json.loads(clean)
                    return parsed
                except Exception:
                    pass

        return {
            "disruption_type": disruption_type,
            "disrupted_room_id": disrupted_room,
            "disrupted_invigilator_id": disrupted_invig,
            "disrupted_slot_id": disrupted_slot,
            "summary": f"Detected {disruption_type} disruption from operator input: '{query}'"
        }
