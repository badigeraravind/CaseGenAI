import streamlit as st
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')

st.title('CaseGen')
st.write('Transform your features to AI powered test cases instantly.')

feature_desc = st.text_area('Describe your feature below',height=150)

tc_type = st.multiselect('Choose your desired testcase types',['Happy Cases', 'Interruptions','Negative Cases'])

platform_type = st.multiselect('Choose your desired platform',['Android','iOS','Cross-Platform','Web'])

if 'test_cases' not in st.session_state:
    st.session_state.test_cases = []

if st.button('Create'):
    if not feature_desc.strip():
        st.warning('Please write your feature description!')
    elif not tc_type:
        st.warning('Please select at least one test case type!')
    else:
        selected_tc_types = ','.join(tc_type)
        prompt = f'''
        You are an expert QA engineer specializing in gaming. Given the following feature description, generate thorough test cases of type:{selected_tc_types} on platform {platform_type}.
        Return ONLY a valid JSON array. No markdown, no code blocks, no explanation.
        Each object must have exactly these keys: "test_id", "test_name", "steps", "expected_output"        
        Group the test cases by type (e.g. all Happy Scenarios together, then all negative Cases together, etc.)
        This is the feature description:{feature_desc}
        '''

        with st.spinner('Thinking..'):
            response = model.generate_content(prompt)
    
        try:
            raw = response.text.strip()
            if raw.startswith('```'):
                raw = raw.split('```')[1]
            elif raw.startswith('json'):
                raw = raw[4:]

            st.session_state.test_cases = json.loads(raw)
        except json.JSONDecodeError:
            st.error('AI returned an unexpected format. Please try again.')
            st.session_state.test_cases = []
    
    if st.session_state.test_cases:
        st.subheader('Created Test Cases')
        st.code(json.dumps(st.session_state.test_cases, indent=2), language='json')


        st.download_button(
            label='Download',
            data=json.dumps(st.session_state.test_cases, indent=2).encode('utf-8'),
            file_name='test_cases.json',
            mime='application/json'
        )
