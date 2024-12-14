import os
import io
import sqlite3
import json
import pytesseract
import PyPDF2
from dotenv import load_dotenv
from openai import OpenAI  
from typing import Dict, List, Any, Union

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
        

    def generate_form_fields(self, form_type: str, user_info: Dict[str, str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate dynamic form fields with document upload requirements
        """
        form_fields = {
            "tax-return": [
                {"label": "Full Name", "type": "text", "value": user_info.get('name', ''), "required": True},
                {"label": "Email", "type": "email", "value": user_info.get('email', ''), "required": True},
                {"label": "Address", "type": "text", "value": user_info.get('address', ''), "required": True},
                {"label": "Social Security Number", "type": "text", "value": user_info.get('ssn', ''), "required": True},
                {"label": "Income", "type": "number", "value": "", "required": True},
                {"label": "W-2 Form", "type": "file", "value": None, "required": True, 
                 "description": "Upload your W-2 form for income verification"},
                {"label": "1099 Forms", "type": "file", "value": None, "required": False, 
                 "description": "Upload additional income forms if applicable"},
                {"label": "Previous Year Tax Return", "type": "file", "value": None, "required": False, 
                 "description": "Upload previous year's tax return for reference"}
            ],
            "immigration-visa": [
                {"label": "Full Name", "type": "text", "value": user_info.get('name', ''), "required": True},
                {"label": "Email", "type": "email", "value": user_info.get('email', ''), "required": True},
                {"label": "Address", "type": "text", "value": user_info.get('address', ''), "required": True},
                {"label": "Passport Number", "type": "text", "value": "", "required": True},
                {"label": "Passport Copy", "type": "file", "value": None, "required": True, 
                 "description": "Upload a clear copy of your passport"},
                {"label": "Birth Certificate", "type": "file", "value": None, "required": True, 
                 "description": "Upload your birth certificate"},
                {"label": "Visa Type", "type": "select", "options": ["Tourist", "Work", "Student", "Permanent Resident"], "value": "", "required": True},
                {"label": "Proof of Employment/Education", "type": "file", "value": None, "required": True, 
                 "description": "Upload employment letter or educational documents"}
            ],
            "social-security-benefits": [
                {"label": "Full Name", "type": "text", "value": user_info.get('name', ''), "required": True},
                {"label": "Email", "type": "email", "value": user_info.get('email', ''), "required": True},
                {"label": "Address", "type": "text", "value": user_info.get('address', ''), "required": True},
                {"label": "Date of Birth", "type": "date", "value": "", "required": True},
                {"label": "Birth Certificate", "type": "file", "value": None, "required": True, 
                 "description": "Upload your birth certificate"},
                {"label": "Previous Pay Stubs", "type": "file", "value": None, "required": False, 
                 "description": "Upload recent pay stubs for income verification"},
                {"label": "Benefit Type", "type": "select", "options": ["Retirement", "Disability", "Survivors"], "value": "", "required": True}
            ],
            # Similar comprehensive field additions for other form types...
        }
        
        return {"fields": form_fields.get(form_type, [])}

    def process_document_upload(self,userInfo, uploaded_files: List[Any], form_type: str) -> Dict[str, Any]:
        """
        Comprehensive document processing using AI and OCR
        """
        if not self.client:
            return {
                "status": "error",
                "message": "AI client not available for document processing"
            }
        
        extracted_info = {}
        
        for uploaded_file in uploaded_files:
            # Read file content
            file_content = uploaded_file.read()
            file_name = uploaded_file.name
            file_extension = file_name.split('.')[-1].lower()
            
            try:
                # PDF Processing
                if file_extension == 'pdf':
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                
                # Image Processing (for scanned documents)
                elif file_extension in ['jpg', 'jpeg', 'png', 'tiff']:
                    text = pytesseract.image_to_string(io.BytesIO(file_content))
                
                else:
                    return {
                        "status": "error",
                        "message": f"Unsupported file type: {file_extension}"
                    }
                
                # Use AI to extract structured information
                extraction_prompt = f"""
                Extract structured information from this document for a {form_type} form excluding {userInfo}.
                
                Document Text:
                {text}
                
                Please provide a JSON response with extracted key-value pairs relevant to the form type.
                """
                
                response = self.client.chat.completions.create(
                    model="grok-beta",
                    messages=[
                        {"role": "system", "content": "You are an expert document information extractor."},
                        {"role": "user", "content": extraction_prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                
                # Parse extracted information
                parsed_info = json.loads(response.choices[0].message.content)
                extracted_info.update(parsed_info)
                
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Error processing {file_name}: {str(e)}"
                }
        
        return {
            "status": "success",
            "message": "Documents processed successfully",
            "extracted_info": extracted_info
        }

    def validate_form_fields(self, form_fields: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Enhanced validation to check document uploads and field requirements
        """
        missing_fields = []
        for field in form_fields:
            # Check required text fields
            if field['required'] and field['type'] != 'file':
                if not field['value'] or field['value'] == '':
                    missing_fields.append(field['label'])
            
            # Check required file uploads
            if field['required'] and field['type'] == 'file':
                if not field['value']:
                    missing_fields.append(f"{field['label']} Document")
        
        if missing_fields:
            return {
                "status": "error",
                "message": f"Please fill/upload the following required fields: {', '.join(missing_fields)}"
            }
        
        return {
            "status": "success",
            "message": "All required fields are filled"
        }