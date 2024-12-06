import json
import os
import matplotlib.pyplot as plt
import itertools
from sklearn.metrics import precision_recall_curve, PrecisionRecallDisplay

plt.rcParams['font.family'] = 'CMU Serif'

class Visualiser:
    def __init__(self, path_summarized_data: str, path_diagramm_mapping: str):
        self._data = self._load_data(path_summarized_data)
        
        self.mapping = {
            'aws_textract': 'AWS Textract',
            'azure_document_intelligence': 'Azure Document Intelligence',
            'google_cloud_document_ai': 'Google Cloud Document AI',
            'openai_gpt4o': 'OpenAI GPT-4o',
            'tesseract': 'Tesseract',
        }
        
        self.autor_list = ['lars', 'sarah', 'robin', 'tim', 'pascal']
        self.font_color_list = ['blau', 'schwarz']
        
        self.tool_colors = self._generate_colors('tools')
        self.autor_colors = self._generate_colors('autor')
        self.font_colors = self._generate_colors('schriftfarbe')
        
        self.diagramm_mapping = self._load_data(path_diagramm_mapping)
    
    def _load_data(self, path):
        with open(path, 'r', encoding='utf8') as f:
            return json.load(f)
        
    def _generate_colors(self, case: str):
        # Defining a fixed set of colors, mapping tools to these colors
        colors = ['#ff7f0e', '#1f77b4', '#2ca02c', '#9467bd', '#d62728']
        colors_font = ['#5353ec', '#555555']
        
        if case == 'tools':
            keys = list(self.mapping.keys())
        
        elif case == 'autor':
            keys = self.autor_list
            
        else:
            keys = self.font_color_list
            return {obj: color for obj, color in zip(keys, itertools.cycle(colors_font))}
        
        # Create a color mapping for each tool
        return {obj: color for obj, color in zip(keys, itertools.cycle(colors))}

    def _plot_bar_chart(self, key, data, color_mapping, save_dir, save=False, value_offset=0.02):
        # Extract and map data
        avg_values = []
        names = []
        colors = []

        for name, metrics in data.items():
            if key in metrics:
                avg_values.append(metrics[key])
                names.append(self.mapping.get(name, name) if color_mapping == self.tool_colors else name)
                colors.append(color_mapping.get(name, '#000000'))  # Default to black if not found

        # Sort tools and values
        sorted_data = sorted(zip(avg_values, names, colors), reverse=True)
        
        if key == 'processing_time':
            avg_values, names, colors = zip(*sorted_data[::-1])
        else:
            avg_values, names, colors = zip(*sorted_data)

        # Plot
        fig, ax = plt.subplots(figsize=(15, 9), facecolor='black')
        ax.bar(names, avg_values, color=colors, zorder=3)

        # Styling
        ax.set_facecolor('#111111')
        ax.set_title(self.diagramm_mapping[key]['title'], fontsize=22, color='white')
        ax.set_ylabel(self.diagramm_mapping[key]['y'], fontsize=20, color='white', labelpad=20)
        ax.tick_params(axis='x', labelsize=16, colors='white')
        ax.tick_params(axis='y', colors='white', labelsize=16)

        # Add values on top of bars
        for i, value in enumerate(avg_values):
            ax.text(i, value + value_offset, f'{value:.3f}', ha='center', fontsize=16, color='white')

        # Grid
        ax.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.7, zorder=2)

        # Save and show
        plt.tight_layout()
        os.makedirs(save_dir, exist_ok=True)

        if save:
            plt.savefig(f'{save_dir}/{key}.png', dpi=1200)

        # plt.show()
    
    def plot_precision_recall_curve(self, key, save=False):
        # Initialize the plot
        fig, ax = plt.subplots(figsize=(15, 9), facecolor='black')

        for tool_name in self._data['data']:
            
            # skip weil werte ausgedacht
            if tool_name == 'openai_gpt4o':
                continue
    
            flat_list = [item for sublist in self._data['data'][tool_name]['confidences'][key] for item in sublist]
            
            labels = [row[0] for row in flat_list]
            scores = [row[1] for row in flat_list]

            precision, recall, _ = precision_recall_curve(labels, scores)
            
            # Plot the precision-recall curve for this tool
            ax.plot(
                recall, precision,
                label=self.mapping.get(tool_name, tool_name),
                color=self.tool_colors.get(tool_name, '#000000'),
                linewidth=2
            )
        
        # Styling
        ax.set_facecolor('#111111')
        ax.set_title(f'Precision-Recall Curve ({key.capitalize()})', fontsize=22, color='white')
        ax.set_xlabel('Recall', fontsize=20, color='white', labelpad=20)
        ax.set_ylabel('Precision', fontsize=20, color='white', labelpad=20)
        ax.tick_params(axis='x', labelsize=16, colors='white')
        ax.tick_params(axis='y', colors='white', labelsize=16)
        ax.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.7, zorder=2)

        # Legend
        legend = ax.legend(fontsize=18, loc='lower right', frameon=False)
        plt.setp(legend.get_texts(), color='white')
        legend.set_zorder(3)

        # Save and show
        plt.tight_layout()
        os.makedirs('images', exist_ok=True)

        if save:
            plt.savefig(f'images/{key}_precision_recall.png', dpi=1200)

        plt.show()
        pass

    def plot_probabilities(self, key, save):
        self._plot_bar_chart(
            key=key,
            data=self._data['data'],
            color_mapping=self.tool_colors,
            save_dir='images',
            save=save,
        )

    def plot_autor(self, key, save):
        self._plot_bar_chart(
            key=key,
            data=self._data['other_data']['autor'],
            color_mapping=self.autor_colors,
            save_dir='images/autor',
            save=save,
            value_offset=0.02
        )

    def plot_times(self, key, save):
        self._plot_bar_chart(
            key=key,
            data=self._data['data'],
            color_mapping=self.tool_colors,
            save_dir='images',
            save=save,
            value_offset=1
        )
    
    def plot_font_colors(self, key, save):
        self._plot_bar_chart(
            key=key,
            data=self._data['other_data']['schriftfarbe'],
            color_mapping=self.font_colors,
            save_dir='images/font_colors',
            save=save,
            value_offset=0.02
        )
            
if __name__ == '__main__':
    path = os.path.join('data', 'summarizedData.json')
    mapping_path = os.path.join('data', 'diagrammMapping.json')
    visualizer = Visualiser(path, mapping_path)
    
    metrics = [
        "word_correct_machine", "letter_correct_machine", "word_correct_handwritten",
        "letter_correct_handwritten", "precision_machine", "recall_machine", "f1_machine", 
        "precision_handwritten", "recall_handwritten", "f1_handwritten", "processing_time", 
    ]
    
    # for metric in metrics:
    #     visualizer.plot_probabilities(metric, True)
    #     visualizer.plot_autor(metric, True)
    
    visualizer.plot_precision_recall_curve('handwritten', True)
    visualizer.plot_precision_recall_curve('machine', True)
