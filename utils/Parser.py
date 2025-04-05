import unicodedata
from datetime import datetime
from lxml import html, etree

class Parser:
    @staticmethod
    def format(key: str) -> str:
        return key.replace(' ', '_').replace('.', '')

    @staticmethod
    def parse_html_table(interval, date_string: str, history_table: list) -> dict:
        last_children = None


        table_rows = [tr for tr in history_table[0].xpath('//tr') if len(tr) == 11] #header material
        for tr in table_rows:
            tr.remove(tr[-1]) #last child element is some weird stuff that needs to go
        headers_list = []
        data_rows = []

        for header in table_rows[0]:
            #print(header.text_content())
            headers_list.append(header.text_content())
        for j, tr in enumerate(table_rows[1:]): # this is necessary for interval selection
            row_dict = {}


            children = tr.getchildren()
            if j>0:
                #print(((datetime.strptime(children[0].text_content(), "%I:%M %p") - datetime.strptime(last_children[0].text_content(), "%I:%M %p")).total_seconds() / 60))
                if interval > ((datetime.strptime(children[0].text_content(), "%I:%M %p") - datetime.strptime(last_children[0].text_content(), "%I:%M %p")).total_seconds() / 60):
                    #print("interval exception reached")
                    #print("j was {}".format(j))
                    continue
            for i, td in enumerate(children):

                td_content = unicodedata.normalize("NFKD", td.text_content())
                #print(td_content)
                #print(i)


                # set date and time in the first 2 columns
                if i == 0:
                    time = datetime.strptime(td_content, "%I:%M %p")
                    date = datetime.strptime(date_string, "%Y-%m-%d")
                    row_dict['Date'] = date.strftime('%Y-%m-%d')
                    row_dict['Time'] = time.strftime('%I:%M %p')

                else:
                    #print(headers_list[i])
                    #exit()
                    row_dict[Parser.format(headers_list[i])] = td_content
            #print("i td enumerate children loop fin")

            if j != len(table_rows)-1:
                last_children = children

            data_rows.append(row_dict)

        
        #print(data_rows)
        #exit()
        return data_rows
