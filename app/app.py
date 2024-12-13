import streamlit as st
import sqlite3
import json
from modified_form import FormAssistantService

# Initialize the form assistant service
assistant = FormAssistantService()

def main():
    st.title("🏛️ AI Government Form Assistant")

    # Initialize session state variables if not already set
    if 'verified_ssn' not in st.session_state:
        st.session_state.verified_ssn = None
    if 'show_assistance_chat' not in st.session_state:
        st.session_state.show_assistance_chat = False
    if 'current_form_type' not in st.session_state:
        st.session_state.current_form_type = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = 'Apply'

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
        st.header(f"{st.session_state.current_mode} Mode - {selected_agency}")
        ssn = st.text_input("Enter your Social Security Number (SSN)", type="password")

        if st.button("Verify SSN"):
            if not ssn:
                st.error("Please enter your SSN")
                return

            # Retrieve user info
            user_info = assistant.retrieve_user_info(ssn)

            if "message" not in user_info and "error" not in user_info:
                st.session_state.verified_ssn = ssn
                st.success("SSN Verified Successfully!")
            else:
                st.error(user_info.get("message", "An error occurred during SSN verification"))

    # Main application flow after SSN verification
    if st.session_state.verified_ssn:
        # Apply Mode
        if st.session_state.current_mode == 'Apply':
            if not st.session_state.show_assistance_chat:
                # Retrieve user info again (could cache this earlier)
                user_info = assistant.retrieve_user_info(st.session_state.verified_ssn)

                # Analyze form requirements
                if "message" not in user_info and "error" not in user_info:
                    form_analysis = assistant.analyze_form_requirements(user_info, form_type)
                    
                    st.header(f"Apply for {selected_agency} Form")
                    st.subheader("Form Analysis")
                    if "analysis" in form_analysis:
                        st.info(form_analysis["analysis"])
                        
                        # Document Upload Section
                        st.subheader("Document Upload")
                        uploaded_file = st.file_uploader("Upload Supporting Documents", accept_multiple_files=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Fill Form Manually"):
                                st.session_state.fill_manually = True
                        
                        with col2:
                            if st.button("Get Form Assistance"):
                                # Set session state for assistance chat
                                st.session_state.show_assistance_chat = True
                                st.session_state.current_form_type = form_type
                                st.session_state.chat_history = []

                    else:
                        st.error("Unable to process form requirements")
                else:
                    st.error(user_info.get("message", "An error occurred"))

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

        # Reset SSN Verification Button
        if st.sidebar.button("Reset SSN Verification"):
            st.session_state.verified_ssn = None
            st.session_state.show_assistance_chat = False
            st.session_state.chat_history = []

if __name__ == "__main__":
    main()