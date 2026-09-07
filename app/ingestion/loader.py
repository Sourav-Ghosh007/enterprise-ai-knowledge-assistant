'''
from app.ingestion.document import Document
from pypdf import PdfReader
from pathlib import Path
import csv
import json

## Loading PDF files only
def load_pdf(path):
    reader = PdfReader(path)
    pages=[]
    for page in reader.pages:
        pages.append(page.extract_text())
    #return "\n".join(pages)
    return Document("\n".join(pages), str(path), {"type": "pdf"})

## Loading TXT files only
def load_txt(path):
    with open(path, "r", encoding="utf-8") as file:
        #return file.read()
        return Document(path.read_text(encoding="utf-8"), str(path), {"type": "txt"})


## Loading CSV files only
def load_csv(path):
    with open(path, newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))
        #return Document(str(list(csv.DictReader(file))), str(path), {"type": "csv"})


## Loading SQL Files only
def load_sql(path):
    with open(path, "r", encoding="utf-8") as file:
        return file.read()



def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as file:
        json_data = load_jsonl("data/evaluation/questions.jsonl")
        print("\n--- questions.jsonl ---")
        print(json_data)
        print(f"Loaded {len(json_data)} evaluation questions")

        

## Here we are loading all the PDF files in a folder automatically
def load_all_pdfs(folder):
    paths = Path(folder).glob("*.pdf")
    return {path.name: load_pdf(path) for path in paths}


## Here we are loading all the TXT files in a folder automatically
def load_all_txt(folder):
    paths = Path(folder).glob("*.txt")
    return {path.name: load_txt(path) for path in paths}


def load_documents(folder):
    documents = list(load_all_pdfs(folder).values())
    documents.extend(load_all_txt(folder).values())

'''

'''
## Here we are loading all the CSV files in a folder automatically
def load_all_csv(folder):
    paths = Path(folder).glob("*.csv")
    return {path.name: load_csv(path) for path in paths}
'''


'''
## Below are the temporary testing code

if __name__ == "__main__":
    ## Loading a single TXT file
    txt = load_txt("data/documents/Employee_Handbook.txt")
    print("\n--- Employee_Handbook.txt ---")
    print(txt[:500])


    ## let's combine PDF + TXT discovery.
    txt_documents = load_all_txt("data/documents")
    for name, text in txt_documents.items():
        print(f"\n--- {name} ---")


    ## Loading a single CSV file
    csv_data = load_csv("data/structured/employees.csv")
    print("\n--- employees.csv ---")
    print(csv_data)


    ## Loading a single SQL file
    sql_data = load_sql("data/structured/company.sql")
    print("\n--- company.sql ---")
    print(sql_data)



documents = load_all_pdfs("data/documents")
for name, text in documents.items():
    print(f"\n--- {name} , {text[:100]}---")


'''
'''
## Here we are manually loading the PDF file
pdf_path = Path("data/documents/HR_Policy.pdf")
text = load_pdf(pdf_path)
print(text[:1000])
'''
'''
'''
'''
'''



from app.ingestion.document import Document
from pathlib import Path
from pypdf import PdfReader
from app.ingestion.document import Document


def load_pdf(path: Path) -> Document:
    reader = PdfReader(path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return Document("\n".join(pages), str(path), {"type": "pdf"})


def load_txt(path: Path) -> Document:
    content = path.read_text(encoding="utf-8")
    return Document(content, str(path), {"type": "txt"})


def load_documents(folder: str) -> list[Document]:
    folder_path = Path(folder)
    documents = []

    for path in folder_path.glob("*"):
        if path.suffix.lower() == ".pdf":
            documents.append(load_pdf(path))
        elif path.suffix.lower() == ".txt":
            documents.append(load_txt(path))

    return documents


if __name__ == "__main__":
    documents = load_documents("data/documents")

    print(f"Loaded {len(documents)} documents")

    for document in documents:
        print(f"\n--- {document.source} ---")
        print(document.content[:300])


## To run the script, execute the following command in your terminal:
##    ------->>>>>>>>>>>>>>     python -m app.ingestion.loader