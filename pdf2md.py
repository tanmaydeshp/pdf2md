import os 
import layoutparser as lp
from layoutparser.elements import TextBlock, Rectangle
import cv2
from dotenv import load_dotenv
load_dotenv()
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
ocr_model = lp.Detectron2LayoutModel(
    config_path='lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config',
    label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"},
    extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.5]
)
ROOT_DIR = ""
PAGES_DIR = ""
JSON_DIR = ""
MD_DIR = ""
GRAPHICS_DIR = ""

def init_dirs(filepath, model):
    global ROOT_DIR, PAGES_DIR, JSON_DIR, MD_DIR, GRAPHICS_DIR
    pdfname = filepath.split("/")[-1].removesuffix(".pdf")
    ROOT_DIR = os.path.join(model,pdfname) 
    PAGES_DIR = ROOT_DIR + "/pages/"
    JSON_DIR = ROOT_DIR + "/json/"
    MD_DIR = ROOT_DIR + "/md/"
    GRAPHICS_DIR = ROOT_DIR + "/graphics/"
    os.makedirs(ROOT_DIR, exist_ok=True)
    os.makedirs(PAGES_DIR, exist_ok=True)
    os.makedirs(JSON_DIR, exist_ok=True)
    os.makedirs(MD_DIR, exist_ok=True)
    os.makedirs(GRAPHICS_DIR, exist_ok=True)


def pdf_to_img(filepath):
    '''Convert a given PDF file into PNG pages'''
    #print("Creating pages...\n")
    from pdf2image import convert_from_path
    pages = convert_from_path(filepath)
    for i, page in enumerate(pages):
        page.save(os.path.join(PAGES_DIR,f"page{i+1}.png"), "PNG")
    #print("Pages created.\n")
    return 

def encode_image_to_base64(image_path):
        '''Convert a given image into base64 encoding'''
        import base64
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

def expand_textblock(textblock, width, height):
    x1 = max(0, min(textblock.block.x_1 -35, width - 1)) 
    x2 = max(0, min(textblock.block.x_2 + 35, width - 1)) 
    y1 = max(0, min(textblock.block.y_1 - 35, height - 1))
    y2 = max(0, min(textblock.block.y_2 + 35, height -1 )) 
    expanded_textblock = TextBlock(Rectangle(x1, y1, x2, y2), textblock.text, textblock.id, textblock.type, textblock.parent, textblock.next, textblock.score)
    return expanded_textblock

def detect_graphics(image_path, pageno):
    image = cv2.imread(image_path)
    width, height, _ = image.shape
    layout = ocr_model.detect(image)
    i = 1
    for textblock in layout:
        if textblock.type in ["Figure", "Table"]:
            textblock = expand_textblock(textblock, width, height)
            segment = textblock.crop_image(image)
            if segment is None or segment.size == 0:
                continue 
            cv2.imwrite(os.path.join(GRAPHICS_DIR, f"page{pageno}_graphic{i}.png"), segment)
            i = i + 1
    return 
        
def perform_ocr(model):
    '''Perform OCR on a given pdf with the specified LLM. Stores the JSON data from the LLM response and the extracted text in Markdown'''
    #print("Extracting Markdown...\n")
    import requests
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    responses_json = []
    from tqdm import tqdm 
    for _, _, filenames in os.walk(PAGES_DIR):
        for filename in tqdm(filenames):
            image_path = os.path.join(PAGES_DIR, filename)
            pageno = filename.removeprefix("page").removesuffix(".png")
            base64_image = encode_image_to_base64(image_path)
            data_url = f"data:image/png;base64,{base64_image}" 
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Examine the image and return all of the text within it, converted to 
                                    Markdown. Make sure the text reflects how a human being would read this, 
                                    following columns and understanding formatting. Ignore footnotes and 
                                    page numbers - they should not be returned as part of the Markdown. 
                                    If you encounter a figure in the image, put a rectangle representing its bounding box in the Markdown
                                    in its place.
                                    Only generate markdown for the text found on the page. Your output should only contain the Markdown
                                    and no other additional comments or explanations."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": data_url
                            }
                        }
                    ]
                }
            ]
            payload = {
                "model": model,
                "messages": messages
            }
           
            response = requests.post(url, headers=headers, json=payload)
            responses_json.append(response.json())
            #print("Storing JSON...\n")
            import json
            with open(os.path.join(JSON_DIR, f"page{pageno}.json"), "w", encoding="utf-8") as f:
               json.dump(response.json(), f)
            #print("JSON stored.\n")
            #print("Storing Markdown...\n")
            with open(os.path.join(MD_DIR, f"page{pageno}.md"), "w", encoding="utf-8") as f:
               jsondata = json.loads(response.text) 
               f.write(jsondata["choices"][0]["message"]["content"])
            #print("Markdown stored.\n")
            #print("Storing Figures and Tables...\n")
            detect_graphics(image_path, pageno)
            #print("Figures and Tables stored.\n")
            #print(f"Page {pageno} processed.")
    return 


def pdf_to_md(filepath, model):
    init_dirs(filepath, model)
    pdf_to_img(filepath)
    responses_json = perform_ocr(model)
    return responses_json

def main():
    import argparse 
    parser = argparse.ArgumentParser("pdf2md.py")
    parser.add_argument("--file","-f", type=str)
    parser.add_argument("--model", "-m", type=str)
    args = parser.parse_args()
    pdf_to_md(args.file, args.model)
    return 

if __name__=="__main__":
    main()