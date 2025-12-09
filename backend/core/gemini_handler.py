
import google.generativeai as genai
from config import get_config
from utils.logger import setup_logger

logger = setup_logger(__name__)
config = get_config()

class GeminiHandler:
    """Handle Gemini API calls."""
    
    def __init__(self):
        """Initialize Gemini handler."""
        try:
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.model_name = config.GEMINI_MODEL
            self.temperature = config.GEMINI_TEMPERATURE
            self.max_tokens = config.GEMINI_MAX_TOKENS
            logger.info(f"✅ Gemini Handler initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"❌ Gemini Handler init error: {str(e)}")
            raise
    
    def generate_code(self, user_prompt, dataframe_info):
        """
        Generate pandas code from user prompt.
        
        Args:
            user_prompt: User's natural language instruction
            dataframe_info: DataFrame metadata
        
        Returns:
            {
                'success': bool,
                'code': 'pandas code',
                'explanation': 'what will happen',
                'risks': [warnings]
            }
        """
        logger.info(f"Generating code for prompt: {user_prompt[:50]}...")
        
        # Placeholder - actual implementation in Phase 1
        return {
            'success': True,
            'code': 'df = df',  # Dummy code
            'explanation': 'Placeholder - Phase 1 implementation',
            'risks': []
        }

def test_gemini_connection():
    """Test if Gemini API is reachable."""
    try:
        logger.info("Testing Gemini API connection...")
        
        # Test API key
        if not config.GEMINI_API_KEY:
            logger.error("❌ GEMINI_API_KEY not set in .env")
            return False
        
        # Try simple API call
        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel(config.GEMINI_MODEL)
        response = model.generate_content("Say 'Connected'")
        
        logger.info(f"✅ Gemini API Connected! Response: {response.text[:50]}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Gemini API error: {str(e)}")
        return False

if __name__ == "__main__":
    test_gemini_connection()
