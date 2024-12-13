import os
import sqlite3
import json
from dotenv import load_dotenv
from openai import OpenAI  # Still importing OpenAI, but we'll use Grok API for X.AI interactions.

load_dotenv()

class FormAssistantService:
    def __init__(self, api_key=None):
        """
        Initialize Grok client with X.AI endpoint
        """
        try:
            self.client = OpenAI(
                api_key=os.getenv('XAI_API_KEY'),
                base_url="https://api.x.ai/v1"  # Assuming this is the correct Grok API URL
            )
        except Exception as e:
            print(f"Failed to initialize client: {e}")
            self.client = None
        
        self.db_path = 'tax_data.db'

    def retrieve_user_info(self, ssn):
        """
        Retrieve user information from the database.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name, email, address
                FROM users 
                WHERE ssn = ?
            ''', (ssn,))
            
            result = cursor.fetchone()
            
            if result:
                return {
                    'name': result[0],
                    'email': result[1],
                    'address': result[2]
                }
            else:
                return {"message": "User not registered. Please register your details first."}
        
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return {"error": "Database error occurred. Please try again later."}
        finally:
            conn.close()

    def analyze_form_requirements(self, user_info, form_type):
        """
        Analyze form requirements with mock data if no AI client
        """
        if not self.client:
            return {
                "analysis": f"Mock analysis for {form_type} form. Requires additional documents: Birth Certificate, Proof of Income"
            }

        # Rest of the method remains the same as in the original implementation
        prompt = f"""
        You are an expert government form assistant. 
        
        User Information:
        {json.dumps(user_info)}
        
        Form Type: {form_type}
        
        Analyze the user's current information and the requirements for the {form_type} form.
        Provide a comprehensive response with:
        1. List of missing required fields
        2. Suggested documents that could help fill those fields
        3. Specific guidance on obtaining missing information
        4. Potential red flags or additional verification needs
        """
        
        try:
            response = self.client.chat.completions.create(
                model="grok-beta",
                messages=[
                    {"role": "system", "content": "You are a helpful government form assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                "analysis": response.choices[0].message.content
            }
        
        except Exception as e:
            print(f"Error in AI analysis: {e}")
            return {
                "error": "Unable to process form requirements automatically."
            }

    def ask_form_guidance(self, form_type, user_question):
        """
        Provide mock guidance if no AI client
        """
        if not self.client:
            return {
                "guidance": f"Mock guidance for {form_type}. Please consult official documentation for specific details."
            }

        # Rest of the method remains the same as in the original implementation
        try:
            prompt = f"""
            You are an expert government form and agency information assistant.

            Form Type: {form_type}

            User Question: {user_question}

            Please provide a comprehensive response that:
            1. Directly answers the user's specific question
            2. Provides context about why this information is collected
            3. Explains the legal basis for collecting this information
            4. Offers guidance on how to accurately complete the relevant sections
            5. Highlight any privacy protections or data usage policies
            """
            
            response = self.client.chat.completions.create(
                model="grok-beta",
                messages=[
                    {"role": "system", "content": "You are a helpful government form guidance assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                "guidance": response.choices[0].message.content
            }
        
        except Exception as e:
            print(f"Error in form guidance generation: {e}")
            return {
                "error": "Unable to generate form guidance automatically."
            }

    def determine_review_necessity(self, form_data):
        """
        Provide mock review necessity if no AI client
        """
        if not self.client:
            return {
                "review_analysis": "Based on the submitted information, this form may require manual review. Please be prepared to provide additional documentation if requested."
            }

        try:
            response = self.client.chat.completions.create(
                model="grok-beta",
                messages=[
                    {"role": "system", "content": "You are a fraud detection assistant."},
                    {"role": "user", "content": f"Analyze these form details for review necessity: {json.dumps(form_data)}"}
                ]
            )
            
            return {
                "review_analysis": response.choices[0].message.content
            }
        
        except Exception as e:
            print(f"Error in review determination: {e}")
            return {
                "error": "Unable to automatically assess form"
            }