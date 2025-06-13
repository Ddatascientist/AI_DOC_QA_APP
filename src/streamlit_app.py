import streamlit as st
import tempfile
from pathlib import Path
from code_base import file_processor, model_pipeline
import pandas as pd
    

var = ["pdf", "txt", "docx", "csv", "xlsx", "xls"]  

@ st.cache_data
def upload_doc(upload):
    # Write uploaded file to a temp file
    suffix = Path(upload.name).suffix  # e.g., '.pdf', '.txt', '.docx'
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(upload.read())
        tmp_file_path = tmp_file.name
        
    return file_processor(tmp_file_path)

def download(q, a):
    # creates dict for the question and answer
    st.session_state.qust_ans.append({"Question": q, "Answer": a})
    # Create DataFrame from stored Q&A
    if st.session_state.qust_ans:
        df = pd.DataFrame(st.session_state.qust_ans)

        # Show table
        # st.subheader("Q&A History from your Document")
        # st.dataframe(df)
        
        global csv_file
        # Convert DataFrame to CSV
        csv_file = df.to_csv(index=False).encode('utf-8')
        
        return csv_file

def main():
    # page layput setup
    st.set_page_config(page_title="Ask_Your_Doc", layout="wide")
        
    st.title("Document Inquiry")
    st.write("Upload your document, then choose a file from the dropdown")
    
    # create an empty list to store QA
    if 'qust_ans' not in st.session_state:
        st.session_state.qust_ans = []
    # Upload widget
    file = st.file_uploader("Upload Your File", type=var, accept_multiple_files=True)     
 

    with st.sidebar:
        # dropdown widget
        option = st.selectbox(
            "Select A Document From List",
            [f.name for f in file],
            index=None,
            placeholder="Choose a doc to question",
            )
        
        # file selection
        if option: 
            for d in file:
                if d.name == option:
                    with st.spinner("loading your doc"):
                        file_doc = upload_doc(d)
        st.write(" ")
        st.write(" ")
        st.write(" ")
        
        # receives user input
        global prompt
        prompt = st.text_area(label="Type in your question(s)", height=200)
        st.write(" ")
        st.write(" ")
        # Generate button widget
        generate = st.button(label="Generate Answer")
        
        
            
    # logit to control generate button            
    if generate:
        if not file:
            st.error(body="Please upload a file!!")
        if not option:
            st.error(body="Please select a file!!")
        if not prompt:
            st.error("Please type in your question in the text area!!")
        else:
            st.warning("⚠ Please note, this is a free openai version, may take few minutes to load")
            with st.spinner(text="🔥 loading...."):
                # Run model pipeline to receive AI answer
                gen_answer = model_pipeline(file_doc, prompt)
                st.header("AI Response")
                st.write(gen_answer)
            
            # logit to control download button    
            if gen_answer:
                # download button to download QA as a csv
                download_btn = st.download_button(
                    label="📥 Download Answers as CSV",
                    data=download(prompt, gen_answer),
                    file_name=f'AI Answers from {option}.csv',
                    mime='text/csv'
                    )
                

           

            


    
          
    
    

    
        
if __name__ == "__main__":
    main()






