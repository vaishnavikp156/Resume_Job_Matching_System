\# Resume Job Matching System



A Python-based Resume and Job Matching System that analyzes a user's resume and recommends relevant job postings using text similarity and skill matching.



\## Features



\- Upload resume in PDF or DOCX format

\- Extract resume text

\- Extract technical skills

\- Retrieve job postings using Adzuna API

\- Preprocess job data

\- Perform exploratory data analysis

\- Calculate TF-IDF text similarity

\- Calculate skill overlap

\- Generate a combined match score

\- Rank job recommendations

\- Streamlit-based user interface



\## Matching Methodology



The system combines two components:



\- TF-IDF cosine similarity: 70%

\- Skill matching score: 30%



Final Match Score:



Final Score = 0.70 × Text Similarity + 0.30 × Skill Score



The result is used to rank job postings according to similarity with the uploaded resume.



\## Technologies Used



\- Python

\- Pandas

\- NumPy

\- Scikit-learn

\- NLTK

\- Matplotlib

\- Seaborn

\- Streamlit

\- PyPDF

\- python-docx

\- Adzuna API



\## Project Structure



```text

Resume\_Job\_Matching\_System/

│

├── app.py

├── collect\_jobs.py

├── eda.py

├── inspect\_data.py

├── match\_jobs.py

├── preprocess\_data.py

├── resume\_parser.py

├── skill\_extractor.py

├── job\_skill\_extractor.py

├── job\_skill\_analysis.py

├── test\_adzuna.py

├── README.md

├── .gitignore

│

└── datasets/

