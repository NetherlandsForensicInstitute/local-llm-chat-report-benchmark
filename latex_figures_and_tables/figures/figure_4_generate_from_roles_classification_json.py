import json
import sys
import os

# --- Static LaTeX components and mappings ---

COLOR_MAP = {
    "LEADERSHIP": "fillPurple",
    "COORDINATION": "fillBlue",
    "LOGISTICS": "fillOrange",
    "INDIRECT PARTICIPANT": "fillGreen",
    "ASSOCIATE": "fillRed",
    "NO ROLE": "fillGrey"
}

# Define the exact order for columns and rows
MODEL_ORDER = [
    "Ground truth", "Gemini (Staged)", "Gemma-3-12b", "Gemma-3-27b",
    "gpt-oss-20b", "phi-4-reasoning", "qwen-14b"
]

INDIVIDUAL_ORDER = [
    "Nerijus Bos", "Antonio Gotta", "Rosie Boudica", "Joseph Prinse",
    "Quan Xiuan", "Figo Johnson", "Liss", "Julia Sheila",
    "Charlie", "nb / NB", "Kate Adriano"
]

LATEX_PREAMBLE = r"""
\begin{figure*}[!t] % Use figure* for full width spanning and [!t] for top placement
    
    % --- TikZ Setup ---
    \def\boxWidth{2.2cm}
    \def\boxHeight{1.1cm}
    \def\boxXDistance{1.5cm}
    \def\boxYDistance{-0.4cm} % INCREASED vertical distance between boxes

    % --- Color Definitions ---
    \definecolor{fillRed}{rgb}{0.89, 0.10, 0.11}      % ASSOCIATE
    \definecolor{fillBlue}{rgb}{0.21, 0.49, 0.72}     % COORDINATION
    \definecolor{fillGreen}{rgb}{0.30, 0.68, 0.29}    % INDIRECT PARTICIPANT
    \definecolor{fillPurple}{rgb}{0.59, 0.30, 0.63}   % LEADERSHIP
    \definecolor{fillOrange}{rgb}{1.0, 0.50, 0.0}     % LOGISTICS
    \definecolor{fillGrey}{rgb}{0.91, 0.91, 0.91}     % NO ROLE
    
    \centering
    \resizebox{\textwidth}{!}{%
    \begin{tikzpicture}[
      text=black,
      box/.style={
        minimum width=\boxWidth,
        minimum height=\boxHeight,
        text=white,
        text width=\boxWidth,
        align=center,
        inner sep=1pt,
        font=\linespread{0.9}\selectfont\scriptsize
      },
      headRow/.style={
        minimum width=\boxWidth,
        minimum height=\boxHeight,
        text=black,
        align=center
      }
    ]
"""

LATEX_POSTAMBLE = r"""
    % ---------- Legend ----------
    \node (legendTitle) [anchor=north, font=\small\bfseries]
      at ([yshift=-4mm]current bounding box.south) {Role Categories};
    
    \matrix (legend) [
      matrix of nodes,
      anchor=north,
      nodes={font=\scriptsize, anchor=west},
      column sep=4mm, row sep=0mm
    ] at ([yshift=0mm]legendTitle.south)
    {
      |[draw, fill=fillRed,    minimum size=5pt]| & Associate &
      |[draw, fill=fillBlue,   minimum size=5pt]| & Coordination &
      |[draw, fill=fillGreen,  minimum size=5pt]| & Indirect Participant \\
      |[draw, fill=fillPurple, minimum size=5pt]| & Leadership &
      |[draw, fill=fillOrange, minimum size=5pt]| & Logistics &
      |[draw, fill=fillGrey,   minimum size=5pt]| & No Role / Irrelevant \\
    };

    \end{tikzpicture}
    }
\caption{Role assignments by the LLMs, with cells coloured by semantic category. While the text in each cell displays the specific role assigned by a model, the background colour corresponds to a broader functional category (e.g., Leadership, Coordination, Logistics), as defined in the legend.}
\label{fig:llm_role_assignments}
\end{figure*}
"""

def escape_latex(text):
    """Escapes special LaTeX characters in a string."""
    return text.replace('&', r'\&').replace('%', r'\%').replace('$', r'\$') \
               .replace('#', r'\#').replace('_', r'\_').replace('{', r'\{') \
               .replace('}', r'\}').replace('~', r'\textasciitilde{}') \
               .replace('^', r'\textasciicircum{}')

def load_and_process_data(json_path):
    """Loads JSON data and restructures it into a grid for easy access."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{json_path}' was not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: The file '{json_path}' is not a valid JSON file.")
        sys.exit(1)
        
    data_grid = {}
    for entry in data:
        individual = entry.get("individual")
        model = entry.get("model_name")
        if individual and model:
            if individual not in data_grid:
                data_grid[individual] = {}
            data_grid[individual][model] = {
                "role": entry.get("assigned_role", ""),
                "category": entry.get("semantic_category", "NO ROLE")
            }
    return data_grid

def generate_grid_code(data_grid):
    """Generates the TikZ code for the main grid of colored boxes."""
    grid_code = []
    
    for i, individual in enumerate(INDIVIDUAL_ORDER):
        row_code = []
        # Row Header (Individual's Name)
        anchor_node = f"R{i}C1" if i > 0 else "R1C1"
        row_header = fr'\node[headRow] (R{i+1}C0) [left of={anchor_node}, xshift=-\boxXDistance-0.5cm] {{\small{{{individual}}}}};'
        
        for j, model in enumerate(MODEL_ORDER):
            entry = data_grid.get(individual, {}).get(model)
            
            if entry:
                role_text = escape_latex(entry['role'])
                color = COLOR_MAP.get(entry['category'], 'fillGrey')
            else:
                role_text = ""
                color = "fillGrey"
            
            node_name = f"R{i+1}C{j+1}"
            
            if j == 0: # First column
                if i == 0: # First row, first column
                    position = ""
                else: # Subsequent rows, first column
                    prev_row_node = f"R{i}C1"
                    position = f"[below of={prev_row_node}, yshift=\\boxYDistance]"
            else: # Subsequent columns
                prev_col_node = f"R{i+1}C{j}"
                position = f"[right of={prev_col_node}, xshift=\\boxXDistance]"
            
            node_code = fr'\node[box, fill={color}] ({node_name}) {position} {{{role_text}}};'
            row_code.append(node_code)

        grid_code.append(f"% Row {i+1}: {individual}")
        if i > 0: # Add the header after the first box is defined for proper positioning
            grid_code.append(row_code[0])
            grid_code.append(row_header)
            grid_code.extend(row_code[1:])
        else: # For the very first row, header comes first
            grid_code.append(row_header.replace(f"left of=R1C1", "")) # remove relative positioning for first header
            grid_code.extend(row_code)
        grid_code.append("\n")

    return "\n    ".join(grid_code)
    
def generate_headers_code():
    """Generates the TikZ code for the model name headers."""
    headers_code = []
    num_rows = len(INDIVIDUAL_ORDER)
    model_name_map = {
        "gpt-oss-20b": "GPT-OSS 20b",
        "phi-4-reasoning": "Phi-4",
        "qwen-14b": "Qwen 14b",
        "Gemma-3-12b": "Gemma 12b",
        "Gemma-3-27b": "Gemma 27b"
    }
    
    headers_code.append(f"% --- Column Headers (Models) ---")
    for j, model in enumerate(MODEL_ORDER):
        node_name = f"H{j+1}"
        anchor_node = f"R{num_rows}C{j+1}"
        position = f"[below of={anchor_node}, yshift=\\boxYDistance]"
        if j > 0:
            prev_node = f"H{j}"
            position = f"[right of={prev_node}, xshift=\\boxXDistance]"
        
        display_name = model_name_map.get(model, model)
        header_node = fr'\node[headRow] ({node_name}) {position} {{\small{{{display_name}}}}};'
        headers_code.append(header_node)
        
    return "\n    ".join(headers_code)

def main():
    """Main function to generate the LaTeX figure file."""
    if len(sys.argv) != 2:
        print("Usage: python generate_figure.py <path_to_json_file>")
        sys.exit(1)

    json_path = sys.argv[1]
    
    # Process data
    data_grid = load_and_process_data(json_path)
    
    # Generate LaTeX components
    grid_code = generate_grid_code(data_grid)
    headers_code = generate_headers_code()
    
    # Assemble final LaTeX string
    final_latex = (
        LATEX_PREAMBLE +
        "\n    " + grid_code +
        "\n    " + headers_code +
        "\n    " + LATEX_POSTAMBLE
    )
    
    # Write to file
    base_name = os.path.splitext(json_path)[0]
    output_path = base_name + ".tex"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_latex)
        
    print(f"Successfully generated LaTeX figure at: {output_path}")

if __name__ == "__main__":
    main()