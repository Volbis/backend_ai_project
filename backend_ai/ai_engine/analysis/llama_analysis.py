
# Analise le contenu extrait des documents pour vérifier la cohérence et la conformité aux normes
# Calcul le risque de rejet basé sur l'analyse du contenu

import os
import json
import logging
from decouple import config

logger = logging.getLogger('ai_engine')

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
    logger.warning("openai not installed")

class LlamaAnalysis:
    def __init__(self):
        if OpenAI is None:
            logger.warning("OpenAI client not available. Using mock mode.")
            self.client = None
            return
 
        try:
            # OpenRouter configuration
            api_key = config('OPENROUTER_API_KEY', default=None)
            if not api_key or api_key == 'sk-or-v1-your-key-here':
                logger.warning("OPENROUTER_API_KEY not configured. Using mock mode.")
                self.client = None
                return
                
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
                timeout=30.0  # 30 seconds timeout
            )
            self.model = "meta-llama/llama-3-8b-instruct"
            logger.info(f"LlamaAnalysis initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize LlamaAnalysis: {e}")
            self.client = None

    def _call_llm(self, prompt: str) -> dict:
        if self.client is None:
            logger.warning("Using mock LLM response")
            return {}

        try:
            logger.info("Calling OpenRouter API...")
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert administrative document verifier. Output JSON only."},
                    {"role": "user", "content": prompt}
                ]
            )
            content = completion.choices[0].message.content
            # Basic cleanup to ensure JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            result = json.loads(content)
            logger.info("LLM call successful")
            return result
        except json.JSONDecodeError as e:
            logger.error(f"LLM returned invalid JSON: {e}")
            return {}
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return {}

    def verify_consistency(self, extracted_data: dict) -> list:
        try:
            text = extracted_data.get("fields", {}).get("raw_text", "")
            if not text:
                logger.warning("No text to verify consistency")
                return []
                
            prompt = f"""You are an expert document verifier. Analyze the following text extracted from an administrative document.

TEXT:
"{text}"

TASK:
Identify any logical inconsistencies such as:
- Dates in the future (for birth dates, issuance dates)
- Expired validity dates
- Conflicting information (e.g., different names, mismatched dates)
- Impossible dates (e.g., Feb 30, month 13)
- Age inconsistencies

Return ONLY a JSON object with this exact structure:
{{"inconsistencies": ["description of inconsistency 1", "description of inconsistency 2"]}}

If no inconsistencies are found, return:
{{"inconsistencies": []}}
"""
            response = self._call_llm(prompt)
            return response.get("inconsistencies", [])
        except Exception as e:
            logger.error(f"Consistency verification failed: {e}")
            return []

    def check_compliance(self, extracted_data: dict) -> float:
        try:
            text = extracted_data.get("fields", {}).get("raw_text", "")
            if not text:
                logger.warning("No text to check compliance")
                return 0.5
                
            prompt = f"""You are an expert document quality assessor. Analyze the following text extracted from an administrative document.

TEXT:
"{text}"

TASK:
Rate the document's compliance and quality on a scale of 0.0 to 1.0 based on:
1. Text legibility and clarity (0.3 weight)
2. Document completeness - all expected fields present (0.4 weight)
3. Information coherence and validity (0.3 weight)

SCORING GUIDE:
- 0.9-1.0: Excellent - Clear, complete, all information valid
- 0.7-0.9: Good - Minor issues, mostly complete
- 0.5-0.7: Fair - Some missing fields or unclear text
- 0.3-0.5: Poor - Significant issues with legibility or completeness
- 0.0-0.3: Very Poor - Mostly illegible or critically incomplete

Return ONLY a JSON object with this exact structure:
{{"score": 0.85, "reasoning": "brief explanation of the score"}}
"""
            response = self._call_llm(prompt)
            score = response.get("score", 0.5)
            reasoning = response.get("reasoning", "")
            
            if reasoning:
                logger.info(f"Compliance reasoning: {reasoning}")
            
            # Validate score is in valid range
            score = float(score) if isinstance(score, (int, float)) else 0.5
            score = max(0.0, min(1.0, score))  # Clamp between 0 and 1
            
            return score
        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            return 0.5
