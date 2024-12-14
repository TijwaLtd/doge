import streamlit as st
from app.form_assistance import FormAssistantService

class InteractiveFormFiller:
    def __init__(self, assistant, form_type, user_info):
        self.assistant = assistant
        self.form_type = form_type
        self.user_info = user_info
        
        # Generate initial form fields
        form_fields_response = self.assistant.generate_form_fields(form_type, user_info)
        self.form_fields = form_fields_response['fields']
        
        # Pre-fill known information from user_info
        self._pre_fill_known_fields()

    def _pre_fill_known_fields(self):
        """
        Pre-fill fields with known information from user_info
        """
        known_fields = {
            'Full Name': self.user_info.get('name', ''),
            'Email': self.user_info.get('email', ''),
            'Address': self.user_info.get('address', ''),
            'Social Security Number': self.user_info.get('ssn', '')
        }

        for field in self.form_fields:
            if field['label'] in known_fields and known_fields[field['label']]:
                field['value'] = known_fields[field['label']]

    def get_next_missing_field(self):
        """
        Find the next field that needs to be filled
        Considers a field empty if it has no value or is an empty string/None
        """
        for field in self.form_fields:
            # Check if field is required and truly empty
            if field['required']:
                # For text, email, date, number fields
                if field['type'] in ['text', 'email', 'date', 'number', 'select']:
                    if not field['value']:
                        return field
                
                # For file uploads
                elif field['type'] == 'file':
                    if field['value'] is None:
                        return field
        
        return None

    def process_user_input(self, user_input):
        """
        Process user input for the current field
        """
        current_field = self.get_next_missing_field()
        
        if current_field is None:
            return {
                'status': 'completed',
                'message': 'All required fields have been filled!'
            }
        
        # Validate and store input based on field type
        try:
            if current_field['type'] == 'file':
                # For file uploads, expect a file object
                if user_input is not None:
                    current_field['value'] = user_input
                else:
                    return {
                        'status': 'error',
                        'message': f'Please upload your {current_field["label"]}'
                    }
            elif current_field['type'] == 'select':
                if user_input in current_field['options']:
                    current_field['value'] = user_input
                else:
                    return {
                        'status': 'error',
                        'message': f'Invalid option. Please choose from {current_field["options"]}'
                    }
            elif current_field['type'] in ['text', 'email', 'date']:
                if user_input and user_input.strip():
                    current_field['value'] = user_input
                else:
                    return {
                        'status': 'error',
                        'message': f'Please provide a valid input for {current_field["label"]}'
                    }
            elif current_field['type'] == 'number':
                try:
                    numeric_input = float(user_input)
                    current_field['value'] = numeric_input
                except ValueError:
                    return {
                        'status': 'error',
                        'message': f'Please provide a valid numeric input for {current_field["label"]}'
                    }
            
            # Return next step
            next_field = self.get_next_missing_field()
            if next_field:
                return {
                    'status': 'continue',
                    'message': f'Please provide {next_field["label"]}',
                    'field': next_field
                }
            else:
                return {
                    'status': 'completed',
                    'message': 'All required fields have been filled!'
                }
        
        except Exception as e:
            return {
                'status': 'error',
                'message': f'An error occurred: {str(e)}'
            }

def main():
    st.title("🏛️ AI Interactive Form Assistant")

    # Initialize session state variables
    if 'verified_ssn' not in st.session_state:
        st.session_state.verified_ssn = None
    if 'interactive_form' not in st.session_state:
        st.session_state.interactive_form = None
    if 'form_chat_history' not in st.session_state:
        st.session_state.form_chat_history = []
    if 'form_completed' not in st.session_state:
        st.session_state.form_completed = False
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = 'Apply'
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Initialize the form assistant service
    assistant = FormAssistantService()

    # Sidebar for agency selection
    st.sidebar.header("Government Agencies")
    selected_agency = st.sidebar.radio(
        "Select an Agency", 
        [
            "IRS (Tax Forms)", 
            "USCIS (Immigration)", 
            "Social Security Administration", 
            "Department of State (Passport)", 
            "Small Business Administration", 
            "Department of Education (Student Loans)"
        ]
    )

    # Mode selection
    st.sidebar.header("Service Mode")
    st.session_state.current_mode = st.sidebar.radio(
        "Select Mode", 
        ["Apply", "Consult"]
    )

    # Mapping agencies to form types
    agency_form_map = {
        "IRS (Tax Forms)": "tax-return",
        "USCIS (Immigration)": "immigration-visa",
        "Social Security Administration": "social-security-benefits",
        "Department of State (Passport)": "passport-application",
        "Small Business Administration": "business-license",
        "Department of Education (Student Loans)": "student-loan-application"
    }
    form_type = agency_form_map[selected_agency]

    # SSN Verification (only once)
    if not st.session_state.verified_ssn:
        st.header("SSN Verification")
        ssn = st.text_input("Enter your Social Security Number (SSN)", type="password")

        if st.button("Verify SSN"):
            if not ssn:
                st.error("Please enter your SSN")
                return

            # Retrieve user info
            user_info = assistant.retrieve_user_info(ssn)

            if "message" not in user_info and "error" not in user_info:
                st.session_state.verified_ssn = ssn
                st.session_state.user_info = user_info
                st.success("SSN Verified Successfully!")
            else:
                st.error(user_info.get("message", "An error occurred during SSN verification"))

    # Main application flow after SSN verification
    if st.session_state.verified_ssn:
        # Apply Mode
        if st.session_state.current_mode == 'Apply':
            # Initialize interactive form if not already done
            if st.session_state.interactive_form is None:
                st.session_state.interactive_form = InteractiveFormFiller(
                    assistant, 
                    form_type, 
                    st.session_state.user_info
                )

            # Form Completion Logic
            if not st.session_state.form_completed:
                # Display chat history
                for message in st.session_state.form_chat_history:
                    if message['role'] == 'system':
                        st.info(message['content'])
                    elif message['role'] == 'user':
                        st.chat_message("user").write(message['content'])
                    else:
                        st.chat_message("assistant").write(message['content'])

                # If no chat history, start with first prompt
                if not st.session_state.form_chat_history:
                    first_field = st.session_state.interactive_form.get_next_missing_field()
                    if first_field:
                        st.session_state.form_chat_history.append({
                            'role': 'system', 
                            'content': f"Let's fill out your {selected_agency} form. First, we need your {first_field['label']}"
                        })
                    else:
                        st.session_state.form_completed = True

                # File upload for file-type fields
                uploaded_file = None
                current_field = st.session_state.interactive_form.get_next_missing_field()
                
                if current_field and current_field['type'] == 'file':
                    uploaded_file = st.file_uploader(
                        f"Upload {current_field['label']}", 
                        type=['pdf', 'png', 'jpg', 'jpeg', 'tiff']
                    )

                # Chat input for other field types
                user_input = st.chat_input(f"Please provide {current_field['label'] if current_field else 'next information'}")

                # Process user input
                if user_input or uploaded_file:
                    # Add user input to chat history
                    if user_input:
                        st.session_state.form_chat_history.append({
                            'role': 'user', 
                            'content': user_input
                        })
                    
                    # Process the input
                    input_to_process = uploaded_file if current_field and current_field['type'] == 'file' else user_input
                    result = st.session_state.interactive_form.process_user_input(input_to_process)

                    # Handle different processing results
                    if result['status'] == 'continue':
                        st.session_state.form_chat_history.append({
                            'role': 'system', 
                            'content': result['message']
                        })
                    elif result['status'] == 'completed':
                        st.session_state.form_completed = True
                        st.session_state.form_chat_history.append({
                            'role': 'system', 
                            'content': result['message']
                        })
                    elif result['status'] == 'error':
                        st.session_state.form_chat_history.append({
                            'role': 'system', 
                            'content': result['message']
                        })

            # Form Completed - Preview and Edit
            else:
                st.header("Form Submission Preview")
                
                # Display all filled fields
                for field in st.session_state.interactive_form.form_fields:
                    st.write(f"**{field['label']}**: {field['value']}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Submit Form"):
                        st.success("Form submitted successfully!")
                
                with col2:
                    if st.button("Edit Form"):
                        # Reset to allow editing
                        st.session_state.form_completed = False
                        st.session_state.form_chat_history = []
                        st.experimental_rerun()

        # Consult Mode
        elif st.session_state.current_mode == 'Consult':
            st.header(f"Consult - {selected_agency}")
            
            # Display chat history
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    st.chat_message("user").write(message['content'])
                else:
                    st.chat_message("assistant").write(message['content'])
            
            # Chat input
            user_input = st.chat_input("Ask a question about the form")
            
            if user_input:
                # Add user message to chat history
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': user_input
                })
                
                # Get guidance from assistant
                guidance = assistant.ask_form_guidance(
                    form_type,
                    user_input
                )
                
                # Add assistant response to chat history
                response = guidance.get('guidance', 'I apologize, but I cannot provide a specific answer at this moment.')
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': response
                })
                
                # Rerun to display the new messages
                st.experimental_rerun()

        # Reset SSN Verification
        if st.sidebar.button("Reset SSN Verification"):
            st.session_state.verified_ssn = None
            st.session_state.interactive_form = None
            st.session_state.form_chat_history = []
            st.session_state.form_completed = False
            st.session_state.chat_history = []

if __name__ == "__main__":
    main()