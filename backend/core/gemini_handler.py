"""
Google Gemini API integration for code generation
Phase 1: Full implementation with system prompts and safety
"""

import google.generativeai as genai
import json
import re
from typing import Dict, List, Any, Tuple
from config import get_config
from utils.logger import setup_logger

logger = setup_logger(__name__)
config = get_config()


class GeminiHandler:
    """Handle Gemini API calls for pandas code generation."""
    
    # System prompt - most important for code quality
    SYSTEM_PROMPT = """You are an expert pandas data analyst and Python developer.
Your job is to write SAFE pandas code based on user instructions.

RULES:
1. Always write valid pandas/Python code
2. Input DataFrame is named 'df'
3. Output MUST be a modified DataFrame assigned to 'df'
4. Never use dangerous functions like eval(), exec(), system commands
5. Never delete original columns unless explicitly asked
6. Always handle errors gracefully
7. Return df at the end

CODE GENERATION FORMAT:
Start with: # Generated code
Write ONLY valid Python pandas code
End with: df = ... (final DataFrame)

SAFETY CHECKS:
- Check for null values before operations
- Validate data types
- Use try-except where appropriate
- Log operations

When user says "Filter where status is Pending":
df = df[df['status'] == 'Pending']

When user says "Add new column with total":
df['total'] = df['amount'] * df['quantity']

When user says "Remove duplicates":
df = df.drop_duplicates(subset=['id'], keep='first')

IMPORTANT:
- Only modify DataFrame, don't create side effects
- Code must be executable standalone
- Assume pandas imported as pd
"""
    
    def __init__(self):
        """Initialize Gemini handler."""
        try:
            if not config.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not set in .env")
            
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.model_name = config.GEMINI_MODEL
            self.temperature = config.GEMINI_TEMPERATURE
            self.max_tokens = config.GEMINI_MAX_TOKENS
            
            logger.info(f"✅ Gemini Handler initialized: {self.model_name}")
        
        except Exception as e:
            logger.error(f"❌ Gemini Handler init error: {str(e)}")
            raise
    
    def generate_code(self, 
                     user_prompt: str,
                     dataframe_info: Dict[str, Any],
                     sheet_name: str = "Sheet1") -> Dict[str, Any]:
        """
        Generate pandas code from user prompt.
        
        Args:
            user_prompt: User's natural language instruction
            dataframe_info: DataFrame schema/structure info
            sheet_name: Name of sheet being worked on
        
        Returns:
            {
                'success': bool,
                'code': Generated pandas code,
                'explanation': What will happen,
                'risks': [Risk warnings],
                'estimated_rows_affected': Estimate,
                'error': Error message if failed
            }
        """
        try:
            logger.info(f"Generating code for prompt: {user_prompt[:60]}...")
            
            # Build context about DataFrame
            context = self._build_dataframe_context(dataframe_info, sheet_name)
            
            # Build full prompt
            full_prompt = f"""
{context}

USER REQUEST: {user_prompt}

Generate pandas code that modifies 'df' based on this request.
Code must:
1. Be valid and executable
2. Handle errors gracefully
3. Return modified DataFrame as 'df'
4. Work with the columns above

Respond in JSON format:
{{
    "code": "df = ...",
    "explanation": "What this code does",
    "risks": ["any potential issues"],
    "estimated_rows_affected": "~N rows"
}}
"""
            
            # Call Gemini
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(full_prompt)
            
            if not response or not response.text:
                return {
                    'success': False,
                    'error': 'Empty response from Gemini'
                }
            
            # Parse response
            result = self._parse_gemini_response(response.text)
            
            if result['success']:
                logger.info(f"✅ Code generated: {len(result['code'])} chars")
            else:
                logger.warning(f"⚠️ Parse warning: {result.get('error', '')}")
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Code generation error: {str(e)}")
            return {
                'success': False,
                'error': f"Code generation failed: {str(e)}"
            }
    
    def _build_dataframe_context(self, 
                                 dataframe_info: Dict[str, Any],
                                 sheet_name: str) -> str:
        """Build DataFrame context for prompt."""
        try:
            sheet_info = dataframe_info.get('sheet_info', {}).get(sheet_name, {})
            columns = sheet_info.get('column_names', [])
            dtypes = sheet_info.get('dtypes', {})
            sample = sheet_info.get('sample', [])
            
            context = f"""
DATAFRAME INFO:
Sheet: {sheet_name}
Total Rows: {dataframe_info.get('total_rows', 'unknown')}
Columns ({len(columns)}):
"""
            
            for col in columns:
                dtype = dtypes.get(col, 'unknown')
                context += f"  - {col} ({dtype})\n"
            
            if sample:
                context += f"\nSample data (first row):\n"
                for row in sample[:1]:
                    for key, val in row.items():
                        context += f"  {key}: {val}\n"
            
            return context
        
        except Exception as e:
            logger.warning(f"Context build warning: {str(e)}")
            return "DataFrame info unavailable"
    
    def _parse_gemini_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse Gemini response JSON.
        
        Args:
            response_text: Raw response from Gemini
        
        Returns:
            Parsed result or fallback
        """
        try:
            # Try to extract JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed = json.loads(json_str)
                
                # Validate required fields
                if 'code' not in parsed:
                    return {
                        'success': False,
                        'error': 'Missing "code" in response'
                    }
                
                return {
                    'success': True,
                    'code': parsed['code'],
                    'explanation': parsed.get('explanation', 'N/A'),
                    'risks': parsed.get('risks', []),
                    'estimated_rows_affected': parsed.get('estimated_rows_affected', 'unknown')
                }
            else:
                # Fallback: treat entire response as code
                logger.warning("Could not parse JSON, treating response as code")
                return {
                    'success': True,
                    'code': response_text,
                    'explanation': 'Auto-generated from response',
                    'risks': ['Unparsed response'],
                    'estimated_rows_affected': 'unknown'
                }
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to parse response: {str(e)}'
            }
    
    @staticmethod
    def validate_code(code: str) -> Dict[str, Any]:
        """
        Quick validation of generated code (syntax check only).
        
        Args:
            code: Python code string
        
        Returns:
            {
                'valid': bool,
                'error': Error message if invalid
            }
        """
        try:
            compile(code, '<generated>', 'exec')
            return {'valid': True}
        
        except SyntaxError as e:
            logger.warning(f"Syntax error in generated code: {str(e)}")
            return {
                'valid': False,
                'error': f'Syntax error: {str(e)}'
            }
        
        except Exception as e:
            return {
                'valid': False,
                'error': f'Validation error: {str(e)}'
            }


def test_gemini_connection():
    """Test if Gemini API is reachable."""
    try:
        logger.info("Testing Gemini API connection...")
        
        if not config.GEMINI_API_KEY:
            logger.error("❌ GEMINI_API_KEY not set")
            return False
        
        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel(config.GEMINI_MODEL)
        response = model.generate_content("Say 'Connected' and nothing else")
        
        if response and response.text:
            logger.info(f"✅ Gemini API Connected! Response: {response.text[:50]}")
            return True
        else:
            logger.error("❌ Empty response from Gemini")
            return False
    
    except Exception as e:
        logger.error(f"❌ Gemini API error: {str(e)}")
        return False


if __name__ == "__main__":
    test_gemini_connection()
