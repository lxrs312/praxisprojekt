import json
import os
import matplotlib.pyplot as plt
import itertools

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

        plt.show()

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
    visualizer.plot_font_colors('word_correct_handwritten', False)
    #visualizer.plot_autor('precision_handwritten', False)
    # visualizer.plot_times('processing_time', False)
    # visualizer.plot_probabilities('word_correct_handwritten', False)