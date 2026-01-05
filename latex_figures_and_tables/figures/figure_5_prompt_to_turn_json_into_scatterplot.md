NIce. Next is figure 5 which is a scatterplot using this data. Here is the old version. Can you create a new version? 

% Set a compatibility version for pgfplots for stable output
\pgfplotsset{compat=1.18}

\begin{figure}[ht!]
    \centering
    \resizebox{0.5\textwidth}{!}{    

    \begin{tikzpicture}
        \begin{axis}[
            title={Trade-off: Report Generation Time vs. Performance of Report},
            xlabel={Report Performance Score},
            ylabel={Report Generation Time (minutes)},
            xmin=0.3, xmax=0.9,
            ymin=0, ymax=35,
            axis lines=left,
            grid=major,
            enlarge limits=0.05,
            width=0.95\textwidth, % Ensure the plot fits on the page
            height=8cm,
            % --- LEGEND STYLING ---
            legend style={
                at={(0.03,0.97)}, % Position legend in top-left corner
                anchor=north west,
                align=left,       % Align text within the legend
            },
        ]

        % Plot each model as a separate series to create the legend
        % Each has a unique marker shape and color.
        
        % Deepseek
        \addplot+[only marks, mark=*, mark size=3pt, blue] 
            coordinates {(0.46, 0.87)};
        \addlegendentry{\gls{ds}}

        % Phi 4 Plus
        \addplot+[only marks, mark=square*, mark size=3pt, red]
            coordinates {(0.66, 29.08)};
        \addlegendentry{\gls{phi4}}

        % Gemma 12b
        \addplot+[only marks, mark=triangle*, mark size=3.5pt, green!60!black]
            coordinates {(0.59, 11.28)};
        \addlegendentry{\gls{gemma12b}}

        % Gemma 27b
        \addplot+[only marks, mark=diamond*, mark size=4pt, orange]
            coordinates {(0.64, 33.02)};
        \addlegendentry{\gls{gemma27b}}

        \end{axis}
    \end{tikzpicture}
    }
    \caption{Scatterplot showing the relationship between the overall performance and the time needed to create an investigative report. Each model is represented by a unique marker, identified in the legend.}
    \label{fig:performance_vs_time_legend}
\end{figure}

** Refined the prompt to do a logarithmic Y scale

Can we try logithmic scale on the time access since gemma 27b was really taking a long time