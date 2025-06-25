# pdf2md
A simple python script that uses LLM calls to convert PDF documents into Markdown format, while also extracting figures and tables from them using OCR.
Only LLMs available on OpenRouter (https://openrouter.ai/) are currently supported by this script. You will need an OpenRouter API key stored in a .env file.
To run the pipeline for a file `filename.pdf` using an LLM with the OpenRouter model code `model-code`, simply run the following code block:
```
git clone https://github.com/tanmaydeshp/pdf2md.git
pip install -r requirements.txt 
python pdf2md.py -f filename.pdf -m model-code
```
