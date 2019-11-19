
#インポートの仕方が毎回混乱する。要勉強
# from . import trendline
#これが正しいはずなのだが、これだとうまく行かない
import trendline
from matplotlib import pyplot as plt

# スロットナンバーと倍率を対応させる
amplification_factor = {'Tot(1)': '1024', 'Tot(2)': '512', 'Tot(3)': '256', 'Tot(4)': '128',
                        'Tot(5)': '64', 'Tot(6)': '32', 'Tot(7)': '16', 'Tot(8)': '8',
                        'Tot(9)': '4', 'Tot(10)': '2'}

def set_fig_title_labels(ax, title='Title', ylabel='y_name', xlabel='x_name'):
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
        
def add_least_squares(x, y, ax):
    result = trendline.least_squares_method(x, y)
    trendline.plot_least_squares_result(result, x, ax)      
        
        
def time_series_graph(df, col_name='Load_Avg'):

    ax = plt.subplot(1, 1, 1)
    df[col_name].plot(ax=ax, ls='none', marker='.', markersize=1)
    
def scatter_graph(df, y_name, x_name, figsize=(5,5), title='Title',
                      ylabel='y_name', xlabel='x_name', alpha=1.0, least_squares=False, linear_regression=False):

    plt.figure(figsize=figsize)
    ax = plt.subplot(1, 1, 1)
    ax.scatter(df[x_name],df[y_name], alpha=alpha)
    set_fig_title_labels(ax, title=title, ylabel=ylabel, xlabel=xlabel)
        
    if least_squares:
            add_least_squares(df[x_name], df[y_name], ax)
            
    if linear_regression:
            trendline.add_linear_regression(df[x_name], df[y_name], color='r')
            
        
def scatter_graphs(df, list_y_names, list_x_names, figsize=(5,5), title='Title', 
                        ylabel='y_name', xlabel='x_name', least_squares=False,
                        alpha=1.0, overlap=False, axes=None):
    """
    前にあるグラフに重ねたいとき：overlap=True, かつ、axesを設定する。
    axesはoverlap=Falseのときにreturnで取得できる。
    """
    
    num_graphs = len(list_y_names)
    if overlap:
        for i in range(num_graphs):
            axes[i].scatter(df[list_x_names[i]], df[list_y_names[i]], alpha=alpha)
            set_fig_title_labels(axes[i], title=list(amplification_factor.keys())[i] + ' : ' + list(amplification_factor.values())[i], ylabel=list_y_names[i], xlabel=list_x_names[i])
                    
        pass
    else:
        plt.figure(figsize=figsize)
        axes = []
        for i in range(num_graphs):
            ax = plt.subplot(3, 4, i+1)
            ax.scatter(df[list_x_names[i]], df[list_y_names[i]], alpha=alpha)
            set_fig_title_labels(ax, title=list(amplification_factor.keys())[i] + ' : ' + list(amplification_factor.values())[i], ylabel=list_y_names[i], xlabel=list_x_names[i])
            axes.append(ax)

    if least_squares:
        add_least_squares(df[list_x_names[i]], df[list_y_names[i]], ax)
#             result = least_squares_method(df[list_x_names[i]], df[list_y_names[i]])
#             plot_least_squares_result(result, df[list_x_names[i]], ax)
            
    plt.tight_layout()

    if overlap:
        return
    else:
        return axes
    
def compare_graphs_time_series(df1, df2, start=None, end=None, figsize=(6,4)):
    if start== None:
        start = str(df1.axes[0][0])
        print(start)
    else:
        pass

    if end == None:
        end = str(df1.axes[0][-1])
        print(end)

    else:
        pass

    plt.figure(figsize=figsize)
    ax = plt.subplot(1, 1, 1)
    ax.plot(df1[start:end])
    ax.plot(df2[start:end])

def compare_graphs_scatter(df1, df2, start=None, end=None, figsize=(5,5), least_squares=None, linear_regression=None):
    if start== None:
        start = str(df1.axes[0][0])
        print(start)
    else:
        pass

    if end == None:
        end = str(df1.axes[0][-1])
        print(end)

    else:
        pass

    plt.figure(figsize=figsize)
    ax = plt.subplot(1, 1, 1)
    ax.scatter(df1[start:end], df2[start:end])

    if least_squares:
            add_least_squares(df1[start:end], df2[start:end], ax)
            
    if linear_regression:
            trendline.add_linear_regression(df1[start:end], df2[start:end], color='r')

def set_xy_lims_for_current_graph(xlim, ylim):
    plt.ylim(ylim)
    plt.xlim(xlim)