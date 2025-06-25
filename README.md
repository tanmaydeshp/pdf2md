# pdf2md
A simple python script that uses LLM calls to convert PDF documents into Markdown format, while also extracting figures and tables from them using OCR.
Only LLMs available on OpenRouter (https://openrouter.ai/) are currently supported by this script. You will need an OpenRouter API key stored in a .env file under the name `OPENROUTER_API_KEY`.
To run the pipeline for a file with path `filename.pdf` using an LLM with the OpenRouter model code `model-code`, simply run the following code block:
```
git clone https://github.com/tanmaydeshp/pdf2md.git
bash setup.sh 
python pdf2md.py -f filename.pdf -m model-code
```
For example, `python pdf2md.py -f test.pdf -m google/gemini-2.5-flash` would run the pipeline using Google Gemini 2.5 Flash on the test.pdf file.
The script produces a new directory named according to the model code of the LLM used with a subdirectory for each PDF file it is called upon. The produced directory has the following structure:
```
|model-code   
|    
└───filename   
    └───graphics
    │   │   page1_graphic1.png
    │   │   page2_graphic1.png
    │   │   ...     
    │      
    └───json
    │   │   page1.json
    │   │   page2.json
    │   │   ...
    │    
    └───md
    │   │   page1.md
    │   │   page2.md
    │   │   ...
    │  
    └───pages
    │   │   page1.png
    │   │   page2.png
    │   │   ...
```
Where `pages` stores all the PDF pages converted into PNG files, `json` stores the responses from the LLM calls per page as JSON files, `md` stores the Markdown extracted by the LLM for each page, and `graphics` stores the figures and tables extracted from the document using OCR.
Currently, the results produced by the extraction are not 100% accurate and depend on the layout of the PDF as well as the LLM used. The script enables easy switching between LLMs in order to compare and benchmark them effectively.