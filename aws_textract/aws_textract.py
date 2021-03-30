import re
import os
import math
import boto3
import config
import argparse
import traceback
import aws_utils as utils
import numpy as np
import pandas as pd
from trp import Document


# Create the parser
my_parser = argparse.ArgumentParser()

# Add the arguments
my_parser.add_argument('Path',
                       metavar='path',
                       type=str,
                       help='the path to file')

# Execute the parse_args() method
args = my_parser.parse_args()

def get_textract():

    textract = None
    try:
        # aws textract object
        textract = boto3.client(
                'textract',
                aws_access_key_id=config.ACCESS_KEY,
                aws_secret_access_key=config.SECRET_KEY,
                )
    except Exception as e:
        print("Error occured in get_textract :- {}".format(e))
        print(traceback.format_exc())
    return textract

def question_ans(table):
    """
    Print extracted questions and answer
    """
    dct = {}
    try:
        # clean the df
        table.replace("\n"," ",regex=True,inplace = True)
        table.replace(" +"," ",regex=True,inplace = True)
        table.columns = ["Questions","Actual_Ans","Written_Ans"]

        # questions are present in 0th colomn
        questions = table["Questions"].values
        # written ans in 1st column
        written_ans = table["Written_Ans"]    

        # it it found that 0 is bieng detected as o in many handwritten cases
        written_ans = written_ans.replace(r"(?i)o",'0',regex=True,)

        for question,answer in zip(questions,written_ans):
            # filtering out noisy answer
            is_number = re.findall(r"\d+",answer,flags=re.IGNORECASE)
            if is_number:
                dct[question] = answer

    except Exception as e:
        print("Error occured in question_ans :- {}".format(e))
        print(traceback.format_exc())    
    return dct


def extract_data(filename):

    question_answer = {}
    try:
        textract = get_textract()
        if textract is not None:

            with open(filename, 'rb') as image:
                # get the response
                response = textract.analyze_document(Document={'Bytes': image.read()},FeatureTypes=['TABLES'])

            # parse the  response_json from aws
            doc = Document(response)

            # getting dataframe for given document
            page_table_dict = utils.get_page_table(doc)
            table_df = utils.get_table_df(page_table_dict)
            
            # since we have only one page
            question_answer = question_ans(table_df[1][0])

            # save the data in excel
            output_path = utils.saveExcel(table_df,filename)

            if output_path:
                    print("Excel saved at {}".format(output_path))            

    except Exception as e:
        print("Error occured in extract_data :- {}".format(e))
        print(traceback.format_exc())        

    return question_answer

                                                                
if __name__=="__main__":
    
    filename = args.Path

    if filename:
       question_answer = extract_data(filename)

       if question_answer:
           for que,ans in question_answer.items():
               print("++++++++++++[Question & Written_ans]+++++++++++++++")
               print("")
               print(que)
               print(ans)
       

    else:
        print("ERROR....!")
        print("Please provide the file path..!!!!")
        
