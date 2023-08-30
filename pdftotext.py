from pdf2image import convert_from_path
import requests
import pytesseract
import glob
import os
class Pdf2Text():
    def __init__(self,tesseract_config=f'--tessdata-dir "{os.getcwd()}/pdf2text/langs/"',langs='fas+eng',tessdata="/pdf2text/langs/"):
        self.pdf_files = glob.glob(os.getcwd() + "/pdf2text/inputs/*.pdf")
        self.tessdata = os.getcwd() + tessdata
        self.temp_folder = os.getcwd() + "/pdf2text/temp/"
        self.output = os.getcwd() + "/pdf2text/output/"
        self.langs = langs
        self.tesseract_config = tesseract_config
        os.environ["TESSDATA_PREFIX"] = tessdata
        languages = self.langs.split('+')
        for language in languages:
            response = requests.get("https://github.com/tesseract-ocr/tessdata/raw/main/"+language+".traineddata")
            if response.status_code == 200:
                language_file_path = os.path.join(self.tessdata, language + ".traineddata")
                print(language_file_path)
                with open(language_file_path, 'wb') as file:
                    file.write(response.content)
                    print(f"Info: {language} language File downloaded and saved to '{self.tessdata}'.")
            else:
                print("Error:Failed to download the file.")
            
    def logger(self,log_message):
        with open(os.getcwd() + "/pdf2text/log.txt",'a') as log:
            log.write(log_message + " \n")
    
    def clear_temp(self):
        try:
            for filename in os.listdir(self.temp_folder):
                file_path = os.path.join(self.temp_folder, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            self.logger(f"Info:Folder '{self.temp_folder}' cleared successfully.")
        except Exception as e:
            self.logger(f"Error:An error occurred: {e}")


    def write_output(self,filename, text):
        outfile = os.path.join(self.output, f'out_{os.path.splitext(os.path.basename(filename))[0]}.txt')
        self.logger(f"Info: text file {os.path.splitext(os.path.basename(filename))[0]} is being processed in write_output")
        with open(outfile, 'w', encoding='utf-8') as text_file:
            text_file.write(text)
            
    def images_to_text(self):
        img_ext = ['.png', '.jpg', '.jpeg', '.tiff']
        image_files = glob.glob(self.temp_folder + "*")
        self.logger(f"Info: PDF Page Images is being processed in images_to_text")
        for image in image_files:
            if image.endswith(tuple(img_ext)):
                #img = preprocessor.process_image(image)

                # Recognize the text as string in image using pytesserct
                text = str(pytesseract.image_to_string(image, lang=self.langs, config=self.tesseract_config))

                # Remove empty lines of text - s.strip() removes lines with spaces
                text = os.linesep.join([s for s in text.splitlines() if s.strip()])

                # Creating a text file to write the output
                self.write_output(image, text)

        self.clear_temp()

                
    def pdf_to_images(self,pdf):
        self.logger(f"Info: PDF {pdf} is being processed in pdf_to_images")
        pages = convert_from_path(pdf, dpi=500,fmt='TIFF')
        image_counter = 1
        for page in pages:
            image_name = self.temp_folder + os.path.splitext(os.path.basename(pdf))[0] + '_' + str(image_counter) + '.tiff'
            page.save(image_name, format='TIFF')
            image_counter += 1
                


    def pdf_to_text(self):
        for pdf in self.pdf_files:
            if pdf.endswith('.pdf'):
                self.pdf_to_images(pdf)
                self.images_to_text()

    