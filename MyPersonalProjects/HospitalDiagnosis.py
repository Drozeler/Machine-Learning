import streamlit as st
import spacy
from spacy.tokens import Span
from spacy.training import Example
from transformers import pipeline
nlp = spacy.load("en_core_web_sm")
labels = ["PATIENT", "AGE", "CHIEF_COMPLAINT", "MEDICAL_HISTORY", "MEDICATION", "EXAMINATION", "DIAGNOSIS"]

for label in labels:
  nlp.get_pipe("ner").add_label(label)

TRAIN_DATA = [
    ("Patient: John Doe Age: 45 Chief Complaint: Severe headache and dizziness", {
        "entities": [(8, 16, "PATIENT"), (22, 24, "AGE"), (41, 69, "CHIEF_COMPLAINT")]
    }),
    ("Medical Histroy: Hypertension, Type 2 Diabetes. ", {
        "entities": [(16, 29, "MEDICAL_HISTORY"), (31, 46, "MEDICAN_HUSTORY")]
    }),
    ("Current Medications: Metformin, Lisinporil.", {
        "entities": [(20, 29, "MEDICATION"), (31, 41, "MEDICATION")]
    }),
    ("Physical Examination: BP 150/90 mmHG, HR 88 bpm.", {
        "entities": [(20, 29, "EXAMINATION"), (31, 37, "EXAMINATION")]
    }),
    ("Diagnosis: Possible migraine, needs further evaluation.", {
        "entities": [(10, 27, "DIAGNOSIS")]
    })
]

optimizer = nlp.create_optimizer()
for text, annotations in TRAIN_DATA:
  doc = nlp.make_doc(text)
  example = Example.from_dict(doc, annotations)
  nlp.update([example], sgd=optimizer)

summarizer = pipeline("summarization")
st.title("Medical Chatbot")
st.set_page_config(layout="wide")
st.title("Clinical Note Analysis")

# Function to create text input fields
def create_text_input(label, default_value=""):
  return st.text_input(label, default_value)
# Sidebar Input
with st.sidebar:
  patient_name = create_text_input("Patient Name")
  patient_age = create_text_input("Age")
  chief_complaint = create_text_input("Chief Complaint")
  medical_history = create_text_input("Medical History")
  current_medications = create_text_input("Current Medications")
  physical_examination = create_text_input("Physical Examination")
  diagnosis = create_text_input("Diagnosis")
  submit_button = st.button("Summarize")
# Main Page Output
if submit_button:
  # Check if all input fields are empty
  if all([
      not patient_name,
      not patient_age,
      not chief_complaint,
      not medical_history,
      not current_medications,
      not physical_examination,
      not diagnosis
  ]):
    st.error("Please fill in at least one field.")
  else:
    clinical_note = f"""
    Patient: {patient_name}, Age: {patient_age}, Chief Complaint: {chief_complaint}
    Medical History: {medical_history}
    Current Medications: {current_medications}
    Physical Examination: {physical_examination}
    Diagnosis: {diagnosis}
    """
    doc = nlp(clinical_note)
    st.subheader("Named Entities")
    for ent in doc.ents:
      st.write(f"{ent.text} ({ent.label_})")
    st.subheader("Summary")
    summary = summarizer(clinical_note, max_length=50, min_length=25, do_sample=False)
    st.write(summary[0]['summary_text'])
