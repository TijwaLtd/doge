import streamlit as st
from grok_api import GrokAPI


grok_api = GrokAPI()


st.title("Smart Tax Filing System")


form_data = {
    "name": st.text_input("Name"),
    "email": st.text_input("Email"),
    "ssn": st.text_input("SSN"),
    "income": st.text_input("Annual Income"),
    "deductions": st.text_input("Deductions")
}


if st.button("Validate and Auto-Fill"):
    with st.spinner("Validating and auto-filling the form..."):
        response = grok_api.validate_and_fill_form(form_data)

        if isinstance(response, dict) and "error" in response:
            st.error(f"Error: {response['error']}")
        elif "message" in response:
            st.info("Grok's Response:")
            st.text(response["message"])
        else:
            st.success("Form validated and auto-filled successfully!")
            
            st.subheader("Auto-Filled Form:")
            for field, value in response.items():
                st.text_input(field.capitalize(), value)
            
            missing_fields = []
            if isinstance(response, dict):
                missing_fields = response.get("missing_fields", [])

            if missing_fields:
                st.warning("Some fields are missing. Please complete the form manually.")
                for field in missing_fields:
                    st.text_input(field.capitalize())