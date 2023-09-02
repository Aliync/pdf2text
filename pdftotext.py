from pdf2image import convert_from_path,pdfinfo_from_path
import requests
import pytesseract
import glob
import os
class Pdf2Text():
    def __init__(self,langs='fas+eng',tessdata="/langs/",dpi=250):
        self.script_directory = os.path.dirname(os.path.abspath(__file__))
        self.pdf_files = glob.glob(self.script_directory + "/inputs/*.pdf")
        self.tessdata = self.script_directory + tessdata
        self.temp_folder = self.script_directory + "/temp/"
        self.output = self.script_directory + "/output/"
        self.langs = langs
        self.dpi = dpi
        self.tesseract_config = f'--tessdata-dir {self.tessdata}'
        os.makedirs(self.script_directory + "/inputs/",exist_ok=True)
        os.makedirs(self.output,exist_ok=True)
        os.makedirs(self.tessdata,exist_ok=True)
        os.makedirs(self.temp_folder,exist_ok=True)
        os.environ["TESSDATA_PREFIX"] = tessdata
        languages = self.langs.split('+')
        for language in languages:
            response = requests.get("https://github.com/tesseract-ocr/tessdata/raw/main/"+language+".traineddata")
            if response.status_code == 200:
                language_file_path = os.path.join(self.tessdata, language + ".traineddata")
                with open(language_file_path, 'wb') as file:
                    file.write(response.content)
                    print(f"Info: {language} language File downloaded and saved to '{self.tessdata}'.")
            else:
                print("Error:Failed to download the file.")
            
    def logger(self,log_message):
        with open(self.script_directory + "/log.txt",'a') as log:
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
        pgs = int(pdfinfo_from_path(pdf)['Pages'])
        if pgs>=100:
            image_counter = 1
            for i in range(1,pgs):
                pages = convert_from_path(pdf, dpi=self.dpi,fmt='TIFF',first_page=i,last_page=i+1)
                image_name = self.temp_folder + os.path.splitext(os.path.basename(pdf))[0] + '_' + str(image_counter) + '.tiff'
                pages[0].save(image_name, format='TIFF')
                image_counter += 1
        else:
            pages = convert_from_path(pdf, dpi=self.dpi,fmt='TIFF')
            image_counter = 1
            for page in pages:
                image_name = self.temp_folder + os.path.splitext(os.path.basename(pdf))[0] + '_' + str(image_counter) + '.tiff'
                page.save(image_name, format='TIFF')
                image_counter += 1
                


    def pdf_to_text(self):
        self.pdf_files = glob.glob(self.script_directory + "/inputs/*.pdf")
        for pdf in self.pdf_files:
            if pdf.endswith('.pdf'):
                self.pdf_to_images(pdf)
                self.images_to_text()

    
