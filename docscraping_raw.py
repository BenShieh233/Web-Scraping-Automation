import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

class DocScraper:
    def __init__(self, url, FILE, headers):
        self.url = url
        self.headers = headers
        self.file = FILE
        self.document = None

    def parsing_file(self):
        r = requests.get(self.url, headers = self.headers)
        raw_file = r.text

        doc_start_pattern = re.compile(r'<DOCUMENT>')
        doc_end_pattern = re.compile(r'</DOCUMENT>')
        type_pattern = re.compile(r'<TYPE>[^\n]+')
        doc_start_is = [x.end() for x in doc_start_pattern.finditer(raw_file)]
        doc_end_is = [x.start() for x in doc_end_pattern.finditer(raw_file)]
        doc_types = [x[len('<TYPE>'):] for x in type_pattern.findall(raw_file)]

        document = {}
        for doc_type, doc_start, doc_end in zip(doc_types, doc_start_is, doc_end_is):
            if doc_type == self.file:
                document[doc_type] = raw_file[doc_start:doc_end]

        regex = re.compile(r'(?i)item.*?business')


        matches = regex.finditer(document[self.file])

        # for match in matches:
        #     print(match)

        # Create the dataframe
        test_df = pd.DataFrame([(x.group(), x.start(), x.end()) for x in matches])

        test_df.columns = ['item', 'start', 'end']
        test_df['item'] = test_df.item.str.lower()

        # Get rid of unnesesary charcters from the dataframe
        test_df.replace('&#160;',' ',regex=True,inplace=True)
        test_df.replace('&nbsp;',' ',regex=True,inplace=True)
        test_df.replace(' ','',regex=True,inplace=True)
        test_df.replace('\.','',regex=True,inplace=True)
        test_df.replace('>','',regex=True,inplace=True)

        # test_df = test_df.drop(test_df.index[-1])

        pos_dat = test_df.sort_values('start', ascending=True)#.drop_duplicates(subset=['item'], keep='last')
        pos_dat.set_index('item', inplace=True)

        self.document = document

        return pos_dat



    # def get_fin(self):

    #     pos_dat = self.parsing_file()

    #     # Create a dictionary to store item content
    #     item_content = {}

    #     # Get Item 1a
    #     item_1a_raw = self.document[self.file][pos_dat['start'].loc['item1a']:pos_dat['start'].loc['item1b']]
    #     item_1a_content = BeautifulSoup(item_1a_raw, 'lxml')
    #     item_content['regulatory_compliance'] = item_1a_content.get_text().replace('\xa0', ' ')

    #     # Get Item 7
    #     item_7_raw = self.document[self.file][pos_dat['start'].loc['item7']:pos_dat['start'].loc['item7a']]
    #     item_7_content = BeautifulSoup(item_7_raw, 'lxml')
    #     item_content['sales_performance'] = item_7_content.get_text().replace('\xa0', ' ')

    #     # Get Item 7a
    #     item_7a_raw = self.document[self.file][pos_dat['start'].loc['item7a']:pos_dat['start'].loc['item8']]
    #     item_7a_content = BeautifulSoup(item_7a_raw, 'lxml')
    #     item_content['market_risks'] = item_7a_content.get_text().replace('\xa0', ' ')
        
    #     return item_content


    def regulatory_compliance(self):
        
        pos_dat = self.parsing_file()

        # Get Item 1a
        item_1a_raw = self.document[self.file][pos_dat['start'].loc['item1a']:pos_dat['start'].loc['item1b']]
        item_1a_content = BeautifulSoup(item_1a_raw, 'lxml')

        regulatory_risks = []
        extract_legal = False

        for div in item_1a_content.find_all("div"):
            text = div.get_text().replace('\xa0', ' ')
            if extract_legal:
                if text.endswith('Risks '):
                    break
                regulatory_risks.append(text)
            elif 'legal' in text.lower() and text.endswith('Risks '):
                extract_legal = True
                regulatory_risks.append(text)  # Add the 'Legal and Regulatory Risks ' as the first line
            # if extract_legal:
            #     regulatory_risks.append(text)
            #     if text.endswith('Risks '):
            #         break
            # elif text.endswith('Legal and Regulatory Risks '):
            #     extract_legal = True
            #     regulatory_risks.append(text)  # Add the 'Legal and Regulatory Risks ' as the first line

        # Join the extracted text if needed
        extracted_text = '\n'.join(regulatory_risks)
        normalized_text = re.sub(r'\n\s*', ' ', extracted_text)
        return normalized_text

    def product_portfolio(self):
        
        pos_dat = self.parsing_file()

        # Get Item 1
        item_1_raw = self.document[self.file][pos_dat['start'].loc['item1']:pos_dat['start'].loc['item1a']]
        item_1_content = BeautifulSoup(item_1_raw, 'lxml')   
        overview = item_1_content.get_text().replace('\xa0', ' ')

        return overview





        


if __name__ == "__main__":
    url = 'https://www.sec.gov/Archives/edgar/data/23217/0001437749-23-019879.txt'
    headers = {"User-Agent": "bxie43@wisc.edu"}
    FILE = '10-K'
    
    parser = DocScraper(url, FILE, headers)
    item = parser.parsing_file()
    print(item)
