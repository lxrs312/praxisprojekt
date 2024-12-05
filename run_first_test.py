import matplotlib.pyplot as plt
import os, json, sys

# Load the data from the JSON file
with open(os.path.join('data', 'evaluatedData.json'), 'r', encoding="utf8") as f:
    data = json.load(f)
    
aws = data['aws_textract']
aws['name'] = 'AWS Textract'

azure = data['azure_document_intelligence']
azure['name'] = 'Azure Document Intelligence'

google = data['google_cloud_document_ai']
google['name'] = 'Google Cloud Document AI'

gpt4o = data['openai_gpt4o']
gpt4o['name'] = 'OpenAI GPT-4o'

tesseract = data['tesseract']
tesseract['name'] = 'Tesseract'

tool_list = [aws, azure, google, gpt4o, tesseract]

# Calculate average processing time for each tool
avg_values = []
tool_names = []

def calc_average(input_list, size):
    summe = 0
    for num in input_list:
        summe += num
    
    return summe / size

def run(keys):
    for key in keys:
        tool_names = []
        avg_values = []
        for tool in tool_list:
            data_dict = {}
            data_list = []
            for document in range(1, 11):
                for exemplar in range(1, 11):
                    data_list.append(tool[str(document)][str(exemplar)][key])

            avg_value = calc_average(data_list, 100)
            avg_values.append(avg_value)
            tool_names.append(tool['name'])
        
        data_dict[key] = avg_values
    
        if key == 'processing_time':
            # Sort tools and times by average processing times
            sorted_data = sorted(zip(avg_values, tool_names))
            avg_values, tool_names = zip(*sorted_data)  # Unzip sorted data
                
            # Plot the bar graph
            fig, ax = plt.subplots(figsize=(10, 6), facecolor='black')

            # Create the bar chart
            ax.bar(tool_names, avg_values, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])

            # Manually style the chart
            ax.set_facecolor('#111111')  # Background color of the plot
            ax.set_title('Average Processing Time for OCR Tools', fontsize=16, color='white')
            ax.set_xlabel('Tools', fontsize=14, color='white')
            ax.set_ylabel('Average Time (s)', fontsize=14, color='white')
            ax.tick_params(axis='x', colors='white')
            ax.tick_params(axis='y', colors='white')

            # Add values on top of each bar
            for i, value in enumerate(avg_values):
                ax.text(i, value + 0.5, f'{value:.2f}', ha='center', fontsize=12, color='white')


            # Add gridlines for better visibility
            ax.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.7)

            # Show plot
            plt.tight_layout()
            plt.show()
        else:
            # Sort tools and times by average processing times
            sorted_data = sorted(zip(avg_values, tool_names))
            avg_values, tool_names = zip(*sorted_data[::-1])  # Unzip sorted data
                
            # Plot the bar graph
            fig, ax = plt.subplots(figsize=(10, 6), facecolor='black')

            # Create the bar chart
            ax.bar(tool_names, avg_values, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])

            # Manually style the chart
            ax.set_facecolor('#111111')  # Background color of the plot
            ax.set_title(f'{key}', fontsize=16, color='white')
            ax.set_xlabel('Tools', fontsize=14, color='white')
            ax.set_ylabel('Average Time (s)', fontsize=14, color='white')
            ax.tick_params(axis='x', colors='white')
            ax.tick_params(axis='y', colors='white')

            # Add values on top of each bar
            for i, value in enumerate(avg_values):
                ax.text(i, value + 0.02, f'{value:.2f}', ha='center', fontsize=12, color='white')


            # Add gridlines for better visibility
            ax.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.7)

            # Show plot
            plt.tight_layout()
            plt.show()

keys = ['processing_time', 'word_correct_machine', 'letter_correct_machine', 'word_correct_handwritten', 'letter_correct_handwritten']
run(keys)
