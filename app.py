import streamlit as st
import os
from utils import extract_news, generate_report

# Streamlit Web Interface
st.title("News Summarization and Text-to-Speech Application")

# Input the company name
company = st.text_input("Enter the Company's Name")
generate_report_button = st.button("Generate Report")

#  Cenerate report by clicking the button
if generate_report_button and company:
    with st.spinner("Extracting news articles and generating the report"):
        try:
            articles = extract_news(company)
            report = generate_report(articles, company)
            
            st.subheader(f"Report on {company}")
            for i in report["Articles"]:
                st.write(f"**Title**: {i['Title']}")
                st.write(f"**Summary**: {i['Summary']}")
                st.write(f"**Sentiment**: {i['Sentiment']}")
                st.write(f"**Topics**: {', '.join(i['Topics'])}")
                st.write("______________________________________________________")
            
            st.subheader("Comparative Sentiment Score")
            st.write("**Sentiment Distribution**")
            st.write(report["Comparative Sentiment Score"]["Sentiment Distribution"])
            
            st.write("**Topic Overlap**")
            st.write(", ".join(report["Comparative Sentiment Score"]["Topic Overlap"]))
            
            st.write("**Coverage Differences**")
            for d in report["Comparative Sentiment Score"]["Coverage Differences"]:
                st.write(f"- {d['Comparison']}: {d['Impact']}")
            
            st.write("**Topic Overview**")
            st.write(f"Topic Overlap: {', '.join(report['Comparative Sentiment Score']['Topic Overview']['Topic Overlap'])}")
            for article, unique_topics in report["Comparative Sentiment Score"]["Topic Overview"]["Unique Topics per Article"].items():
                st.write(f"{article}: {', '.join(unique_topics) if unique_topics else 'Not Available'}")
            
            st.subheader("Final Sentiment Analysis")
            st.write(report["Final Sentiment Analysis"])
            
            st.subheader("Hindi Audio Summary")
            if report["Audio"]:
                st.audio(report["Audio"])
            else:
                st.warning("Audio summary could not be generated.")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
