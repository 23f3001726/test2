# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "chardet",
#     "jupyter",
#     "matplotlib",
#     "numpy",
#     "opencv-python",
#     "pandas",
#     "plotly",
#     "requests",
#     "scikit-learn",
#     "scipy",
#     "seaborn",
#     "statsmodels",
#     "tensorflow",
#     "torch",
#     "scikit-learn",
#     "statsmodels",
#     "networkx"
# ]
# ///

#Importing
import os, sys
import requests,_json
import pandas as pd
import base64, chardet

#Path of csv file
path = str(sys.argv[-1])

#Number of statements to analyse for
number = 4

#Open API Key from env variables
api_key = os.environ["AIPROXY_TOKEN"]

#ChatGpt request api function
def chatgpt(message):
    try:
        # Make the POST request to the OpenAI API
        response = requests.post(
            "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "gpt-4o-mini",
                "messages": message
            }
        )

        # Check if the response status code is 200 (OK)
        if response.status_code == 200:
            try:
                # Parse the response JSON and return the model's message content
                return (response.json()["choices"][0]["message"]["content"])

            except Exception as e:
                print(f"Error parsing JSON response: {str(e)}")
                print(f"Response Content: {response.json()}")

        # If status code isn't 200, handle non-OK responses
        else:
            error_message = response.json().get("error", {}).get("message", "Unknown error occurred.")
            print(f"Error: {response.status_code} - {error_message}")

    except requests.exceptions.RequestException as e:
        # Catch network or request-related errors
        print(f"Request failed: {str(e)}")
    except Exception as e:
        # Catch other unexpected errors
        print(f"An unexpected error occurred: {str(e)}")




#Other Functions

#Change image to base64
def base64_encode(file_path):
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

#Get File Details
def file_details(file_path):
    # Detect the encoding of the file
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']

    # Read the CSV file with the detected encoding
    df = pd.read_csv(file_path, encoding=encoding)

    description = f"File: {file_path}\nEncoding: {encoding}\n"

    for col in df.columns:
        dtype = df[col].dtype
        example = df[col].iloc[0]  # Get the first value as an example
        description += f"Column: {col}\nType: {dtype}\nExample: {example}\n"

    # Summary statistics
    summary_statistics = (df.describe(include='all')).to_string()

    # Checking for missing values
    missing_values = (df.isnull().sum()).to_string()

    details = "File description : " + description + " Summary statistics : " + summary_statistics + " Missing values : " + missing_values
    return details

#Get Graph Type
def graph(statement):
    message =  [
                {"role": "system", "content": "You are an person excelling in data visualisation using Seaborn. Give me the single best graph to use for following problem statement. Give only graph name, without any extra text, or '0' if graph isn't required."},
                {"role": "user", "content": statement }
            ]
    return str(chatgpt(message))

#Get analysis code with graph
def analyse_graph(details, statement, graph, filename):
    message = [
                {"role": "system", "content": "You are an expert of data analysis, data visualisation. Give me code(No extra text) for analysis statement over given file. Code must be error-free with proper exception handling(atleat print error). Don't use outdated methods. Use " + graph + " for visualisation using seaborn(enhance with titles, axis labels, legends, colors, annotations, and enhanced customization). Choose data points judiciously, for visualisation(there might be too much data points on graph, making it cluttered and un-readable)."},
                {"role": "user", "content": "File Details are: " + details +
                 "Analysis Statement: " + statement +"Save the graph with name "+ filename + ". Make sure that graph is clutter-free and human readable."}
            ]
    return chatgpt(message)[9:][:-4]

#Get analysis code without graph
def analyse(details, statement):
    message = [
                {"role": "system", "content": "You are an expert of data analysis. Give me code(No extra text) for analysis statement over given file. Give me code(No extra text) for analysis statement over given file. Code must be error-free with proper exception handling(atleat print error). Don't use outdated methods. Code should store concluding remarks into a varialble 'conclusion' and return it."},
                {"role": "user", "content": "File Details are: " + details +
                 "Analysis Statement: " + statement + "."}
            ]
    return chatgpt(message)[9:][:-4]

#Get summary for analysis(without graph)
def summarise(details, statement, conclusion):
    message = [
                {"role": "system", "content": "You are an expert of data analysis and summarising. Summarise for given problem statement on file with details: " + details + ". Give me summary(descriptive and detailed) only, without any extra text"},
                {"role": "user", "content": "Problem Statement: " + statement +
                 "Analysis Conclusion: " + conclusion }
            ]
    return chatgpt(message)

#Get summary for analysis(with graph)
def summarise_graph(details, statement, base64_image):
    message = [
                {"role": "system", "content": "You are an expert of summarising and analysisng different types of graphs. Summarise the graph for problem statement on file with details: " + details + ". Give me summary(descriptive and detailed) only, without any extra text"},
                {"role": "user", "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "detail": "low",
                            "url": "data:image/png;base64," + base64_image
                        }
                    },
                    {
                        "type": "text",
                        "text": "Problem Statement: " + statement + '. Summarise the graph for given problem statement.'
                    }
                ] }
            ]
    return chatgpt(message)

#Data Cleaning and Data Details
message = [
            {"role": "system", "content": "You are an expert data analyst. Write error-free python code(with error handling , atleast print error to terminal) for cleaning data of a csv file. Don't use outdated methods. Do appropriate replacement for missing values and inappropriate cell values. Save the file with its original name. Only code no other text" },
            {"role": "user", "content": file_details(path) + "."}
        ]
try:
    exec(chatgpt(message)[9:][:-4])

except Exception as e:
   print("Data Cleaning Error:", e) #log error to console
   print("Something went wrong : Data Cleaning") #log to console

details = file_details(path)

#Getting problem statements into a list
message = [
            {"role": "system", "content": "You are an expert data analyst. Give me best" + str(number) + "problem statements to analyse for, on the file. Just give a paragraph containing one line each for those statements, seperated by \"|\" without numbering."+ "Here are some probable areas to analyse for(but don't just copy them , use your wit):- Outlier and Anomaly Detection(You might find errors, fraud, or high-impact opportunities), Correlation Analysis, Regression Analysis, and Feature Importance Analysis(You might find what to improve to impact an outcome), Time Series Analysis(You might find patterns that help predict the future), Cluster Analysis(You might find natural groupings for targeted marketing or resource allocation), Network Analysis(You might find what to cross-sell or collaborate with)"},
            {"role": "user", "content": "File Details are: " + details + ". Give me statements that give me best and useful insights."}
        ]
statements = chatgpt(message).split("|")

#Analysis
readme = "" #Variable to store analysis

for i in range(len(statements)):
  statement = statements[i] #Get problem statement
  readme += '#' + "Analysis Statement: " + statement + "\n" #Store problem statements
  print("Statement:", statement) #log to console

  Graph = graph(statement) #Get graph type

  if Graph == "0": #If Graph isn't required
    print("Without Graph") #log to console
    conclusion = ''
    try:
      #add summary to variable
      exec(analyse(details, statement), globals()) #Storing analysis to conclusion

    except Exception as e:
      print('Analysis Error:', e) #log error to console
      print("Something Went Wrong in analysis") #log to console
      if conclusion == '': #if conclusion is empty
        print("Something Went Wrong: Conclusion is Empty") #log to console
        #adding error message (later handled in final summary)
        readme += "Instruction : Something went wrong. Skip this entire section(including analysis statement) in summary.\n"

    try:
      if not (conclusion == ''): #if conclusion isn't empty
        readme += summarise(details, statement, conclusion) + "\n"
        print("Done") #log to console

    except Exception as e:
      print('Summary Generation Error:', e) #log error to console
      print("Something Went Wrong in summary generation") #log to console
      #adding error message (later handled in final summary)
      readme += "Instruction : Something went wrong. Skip this entire section(including analysis statement) in summary.\n"

  else: #If Graph is required
    print("With Graph") #log to console
    t = str(i)+".png" #png file path
    readme += "![Failed To Load Image](" + t + ")\n" #adding image to variable
    try:
      #generate graph for variable  
      exec(analyse_graph(details, statement, Graph, t))
      print("Graph generated and saved")

    except Exception as e:
      print('Graph Generation Error:', e) #log error to console
      print("Something went wrong in graph generation") #log to console

    try:
      #read graph and convert it to base64_image
      base64_image = base64_encode(t)

    except FileNotFoundError as e:
      print('Graph Not Found Error:', e) #log error to console

    except Exception as e:
      print('Graph Encoding Error:', e) #log error to console

    try: 
      #add summary to variable
      readme += summarise_graph(details, statement, base64_image) + "\n"
      print("Done") #log to console

    except Exception as e:
      print('Summary Generation Error:', e) #log error to console
      #adding error message (later handled in final summary)
      readme += "Instruction : Something went wrong. Skip this entire section(including analysis statement and png image) in summary.\n"
      print("Something went wrong in summary generation") #log to console


#Making a story and saving it to README.md
message = [
            {"role": "system", "content": "You are a phenomenol storyteller. Give me just the summary story( detailed and descriptive one ) without any extra text. Ignore the statement part which says 'Something Went Wrong' completely. Don't forget to add png images into the story. You must follow instructions in Further Analysis" + '''
            Describe(as a story):
            The data you received, briefly.
            The analysis you carried out.
            The insights you discovered.
            The implications of your findings (i.e. what to do with the insights).
            '''},
            {"role": "user", "content": "I have analysed a file" +  '''
            I want you to restructure and summarise my analysis of the file, as an interesting story, in markdown format, with embedded png images given in analysis (they will be in root folder only)
            '''+ "Analysis of the file:- Basic Analysis: " + details + ", Further Analysis: " + readme + ". Skip the entire section of a statement , if something went wrong."}
        ]

# Open the README.mkd file in write mode
file = open('README.md', 'w')

# Split the string by newlines and write each line to the file
for line in chatgpt(message).splitlines():
    file.write(line + '\n')  # Write each line followed by a newline

# Save and close the file
file.close()
