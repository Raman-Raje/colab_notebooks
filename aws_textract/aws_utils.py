import os
import re
import math
import pandas as pd

def get_page_table(doc):
    """
    This method will give all tabular data in given page.
    """
    page_table_dict = {}
    for page_cnt,page in enumerate(doc.pages,start=1):
        page_table_dict[page_cnt] = []
        for table in page.tables:
            temp_table = []
            for r, row in enumerate(table.rows):
                temp_row = []
                for c, cell in enumerate(row.cells):
                    temp_row.append(cell.text)
                # add ech row to table
                temp_table.append(temp_row)
        
            # add table in page to dict
            page_table_dict[page_cnt].append(temp_table)
        
    
    return page_table_dict
                    
          
def get_table_df(page_table_dict):
    """
    This method will convert the tabular data to dataframe
    """
    table_df = {}
    for page_cnt,tables in page_table_dict.items():
        table_df[page_cnt] = []
        for table in tables:
            df = pd.DataFrame(table)
            if not df.empty:
                table_df[page_cnt].append(df)
    return table_df

def GetFileName(filename,extension = ".xlsx"):
    name = os.path.basename(filename)
    f_name = name.split(".")[0] + extension
    return f_name

# save df to excel for better view
def saveExcel(df_dict,filname,spaces = 1,single_sheet = True):

    try:
        output_path = GetFileName(filname)
        writer = pd.ExcelWriter(output_path,engine='xlsxwriter')
        
        for page_cnt,tables in df_dict.items():
            for table in tables:
                # clean the df
                table= table.replace("\n"," ",regex=True)
                table= table.replace(" +"," ",regex=True)
                table.to_excel(writer,"page_{}".format(page_cnt) , startcol = 0 , startrow = 0)
            
        writer.save()
        return output_path

    except Exception as e:
        print("Error in saveExcel :- {}".format(e))
        print(traceback.format_exc())