import os
import json
import httpx
from typing import Dict, Any, Optional, Tuple, List
from app.config import settings

class ModelProviderError(Exception):
    pass

class GemmaModelProvider:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.api_key = api_key or settings.GEMMA_API_KEY
        self.model = model or settings.GEMMA_MODEL or "gemma-4b"
        self.provider = (provider or settings.GEMMA_PROVIDER or "google").lower()
        self.base_url = base_url or settings.GEMMA_API_BASE_URL

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    async def check_connectivity(self) -> Tuple[bool, str]:
        if not self.is_configured():
            return False, "GEMMA_API_KEY is not configured in backend environment."
        
        try:
            # Simple test request to verify API key
            if self.provider == "google":
                url = f"https://generativelanguage.googleapis.com/v1beta/models?key={self.api_key}"
                async with httpx.AsyncClient(timeout=8.0) as client:
                    res = await client.get(url)
                    if res.status_code == 200:
                        return True, f"Successfully connected to Google Gemma/Gemini API provider ({self.model})."
                    else:
                        return False, f"Google API connection test failed with status code {res.status_code}."
            else:
                return True, f"Provider '{self.provider}' configured."
        except Exception as e:
            return False, f"Model provider connectivity check failed: {str(e)}"

    async def generate_action(
        self,
        issue_title: str,
        issue_body: str,
        tool_history: List[Dict[str, Any]],
        available_tools_description: str
    ) -> Optional[Dict[str, Any]]:
        """
        Sends context to Gemma model and receives the next structured action or final answer JSON.
        """
        if not self.is_configured():
            return None

        prompt = f"""You are the RepoXray AI Investigator Agent powered by Gemma 4.
Your goal is to investigate a GitHub issue, gather empirical evidence from the repository using tools, and synthesize an investigation report.

# ISSUE DETAILS
Title: {issue_title}
Description:
{issue_body[:1500]}

# AVAILABLE TOOLS
{available_tools_description}

# PREVIOUS INVESTIGATION TRACE & TOOL RESULTS
{json.dumps(tool_history, indent=2)}

# INSTRUCTIONS
1. Analyze the issue and the tool results so far.
2. Select the NEXT single tool action to gather more evidence, OR if you have enough evidence (or reached step limit), choose the "final_answer" action.
3. Respond ONLY with a single valid JSON object containing:
   - "thought": A concise string explaining your reasoning.
   - "tool": Name of the selected tool (e.g. "search_code", "read_file", "find_tests", "get_issue_state", "find_linked_prs", "read_contributing_guide", or "final_answer").
   - "arguments": A JSON object containing the required arguments for the selected tool.

For "final_answer", the "arguments" object MUST contain:
- "summary": A concise breakdown of what the issue describes and what evidence was found.
- "uncertainties": List of strings describing remaining unknowns.
- "contribution_steps": List of step objects: [{"step_number": 1, "title": "...", "description": "...", "action_type": "inspect_file"|"run_tests"|"maintainer_question"}]

JSON response:
"""

        try:
            raw_text = await self._call_model_api(prompt)
            if not raw_text:
                return None
            
            # Extract JSON block
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_text, re.DOTALL)
            if json_match:
                clean_json = json_match.group(1)
            else:
                json_match_raw = re.search(r'\{.*\}', raw_text, re.DOTALL)
                clean_json = json_match_raw.group(0) if json_match_raw else raw_text

            parsed = json.loads(clean_json)
            if isinstance(parsed, dict) and "tool" in parsed:
                return parsed
        except Exception as e:
            # Handle malformed response gracefully
            print(f"Model generation error: {e}")
            return None

        return None

    async def _call_model_api(self, prompt: str) -> Optional[str]:
        if self.provider == "google":
            # Call Google Gemini / Gemma REST API endpoint
            model_id = "gemini-1.5-flash" if "gemma" not in self.model.lower() else self.model
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={self.api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1000}
            }
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
                elif res.status_code == 404:
                    # Retry with fallback model gemini-1.5-flash if gemma-4b not registered in beta API endpoint
                    fallback_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
                    res_fb = await client.post(fallback_url, json=payload)
                    if res_fb.status_code == 200:
                        candidates = res_fb.json().get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                return parts[0].get("text", "")
        elif self.base_url:
            # OpenAI / Custom compatible REST API endpoint
            url = f"{self.base_url.rstrip('/')}/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2
            }
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    return data["choices"][0]["message"]["content"]
        return None
