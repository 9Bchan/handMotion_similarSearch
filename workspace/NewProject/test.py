"""
MatplotlibのグラフをCanvasに埋め込む

"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import PySimpleGUI as sg

fig = plt.figure(figsize=(5, 4))
ax = fig.add_subplot(111)

def make_data_fig(fig,make = True):

    if make:
        # x = np.linspace(0, 2*np.pi, 500)
        x = np.arange(0, 2*np.pi, 0.05*np.pi)
        ax.plot(x, np.sin(x))
        return fig

    else:
        ax.cla()
        return fig

def draw_figure(canvas, figure):
    figure_canvas = FigureCanvasTkAgg(figure, canvas)
    figure_canvas.draw()
    figure_canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas


sg.theme('Light Blue 2')

layout = [[sg.Text('Graph Diasplay')],
          [sg.Button('Display',key='-display-'), sg.Button('clear',key='-clear-'), sg.Cancel()],
          [sg.Canvas(key='-CANVAS-')]
          ]

window = sg.Window('Plot', layout, location =(100,100), finalize=True)

# figとCanvasを関連付ける
fig_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)

while True:
    event, values = window.read(timeout=100)

    if event in (None, 'Cancel'):
        break
    fig = make_data_fig(fig, make=True)
    fig_agg.draw()
    print("a")
    
    """
    elif event == '-display-':
        fig = make_data_fig(fig, make=True)
        fig_agg.draw()

    elif event == '-clear-':
        fig = make_data_fig(fig, make=False)
        fig_agg.draw()"""

window.close()

