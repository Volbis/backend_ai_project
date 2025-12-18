
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
                
            prompt = f"""
Analyze the following text from an administrative document:
"{text}"

Identify any logical inconsistencies (e.g., dates in the future for birth, conflicting names, expired validity).
Return a JSON object with a key "inconsistencies" containing a list of strings.
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
                
            prompt = f"""
Analyze the following text:
"{text}"

Rate the compliance of this document on a scale of 0.0 to 1.0 based on legibility and completeness.
Return a JSON object with a key "score" (float).
"""
            response = self._call_llm(prompt)
            score = response.get("score", 0.5)
            return float(score) if isinstance(score, (int, float)) else 0.5
        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            return 0.5
