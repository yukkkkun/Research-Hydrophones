
#インポートの仕方が毎回混乱する。要勉強
# from . import trendline
#これが正しいはずなのだが、これだとうまく行かない
import trendline
from matplotlib import pyplot as plt

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
            set_fig_title_labels(axes[i], title='Tot({})'.format(i+1), ylabel=list_y_names[i], xlabel=list_x_names[i])
                    
        pass
    else:
        plt.figure(figsize=figsize)
        axes = []
        for i in range(num_graphs):
            ax = plt.subplot(3, 4, i+1)
            ax.scatter(df[list_x_names[i]], df[list_y_names[i]], alpha=alpha)
            set_fig_title_labels(ax, title='Tot({})'.format(i+1), ylabel=list_y_names[i], xlabel=list_x_names[i])
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
    
        
def set_xy_lims_for_current_graph(xlim, ylim):
    plt.ylim(ylim)
    plt.xlim(xlim)
    pass


# def histogram(df)
            
def test():
    print("done")
    
# class Time_series_graph(Graph):
#     def __init__(self, df, figsize=(5,3)):
#         self.df = df
#         self.figsize= figsize
        
#     def graph_pit(self):
# #     plt.rcParams['font.family'] = 'Times New Roman'
# #     plt.subplot(121)
#         df['Load_Avg'].plot(ls='none', marker='.', markersize=1)
# #     plt.ylabel('Pit weight[kg]')
# #     plt.subplot(122)
# #     df_2017['Load_Avg'].plot(ls='none', marker='.', markersize=1)
# #     plt.ylabel('Pit weight[kg]')