# pandas and numpy for data manipulation
import pandas as pd
import numpy as np

from bokeh.io import show, output_notebook, push_notebook
from bokeh.plotting import figure

from bokeh.models import CategoricalColorMapper, HoverTool, ColumnDataSource, Panel,CustomJS,LinearAxis, Grid,Plot
from bokeh.models.ranges import FactorRange
from bokeh.models.widgets import CheckboxGroup, Slider, RangeSlider, Tabs,Button,Paragraph
from bokeh.models.glyphs import HBar

from bokeh.layouts import column, row, WidgetBox,gridplot
from bokeh.palettes import Category20_17

from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application


# os methods for manipulating paths
from os.path import dirname, join

def histogram_tab(car):
    factors = list(car.columns[7:])

    def make_dataset(factor_list, range_start = 0, range_end = 20000, bin_width = 10):
        by_factor = pd.DataFrame(columns=['count', 'left', 'right', 
                                      'f_count', 'f_interval','color'])
        range_extent = range_end - range_start
    
        subset=car
        
        # Iterate through all the factors
        for i, factor_name in enumerate(factor_list):

            # Subset to the factor
            subset = subset[subset[factor_name]==True]
        
        
        # Create a histogram with specified bins and range
        arr_hist, edges = np.histogram(subset['賠償金額_千'], 
                                        bins = int(range_extent / bin_width), 
                                        range = [range_start, range_end])
        
        arr_df = pd.DataFrame({'count': arr_hist, 
                            'left': edges[:-1], 'right': edges[1:] })
        # Format the count
        arr_df['f_count'] = ['%d' % int(proportion) for proportion in arr_df['count']]
    
        # Format the interval
        arr_df['f_interval'] = ['%d to %d NT$ (單位:千元)' % (left, right) for left, 
                                right in zip(arr_df['left'], arr_df['right'])]

        # Color each carrier differently
        arr_df['color'] = Category20_17[0]

        # Add to the overall dataframe
        by_factor = by_factor.append(arr_df)

        # Overall dataframe
        by_factor = by_factor.sort_values(['left'])
        
        return ColumnDataSource(by_factor),subset.shape[0]
    
    def make_dataset_law_range(factor_list):
        subset=car
        # Iterate through all the factors
        for i, factor_name in enumerate(factor_list):
            # Subset to the factor
            subset = subset[subset[factor_name]==True]
        
        subset_law=subset[['法條1','法條2','法條3']] 
        subset=subset[['賠償金額_千']]

        subset_law=subset_law.apply(pd.Series.value_counts)
        subset_law=subset_law.fillna(0)
        subset_law=subset_law.apply(lambda x:sum(x),axis=1)
        subset_law=pd.DataFrame(subset_law)
        subset_law.reset_index(level=0, inplace=True)
        subset_law=pd.DataFrame(subset_law)
        subset_law.columns=['law','value']
        subset_law.sort_values(ascending=False,by='value',inplace=True)
        subset_law=subset_law.iloc[0:3,:]
        subset_law['value']=subset_law['value'].apply(lambda x:int(x))
        subset_law=pd.DataFrame(subset_law)
        
        return round(subset['賠償金額_千'].quantile(0.25),1),round(subset['賠償金額_千'].quantile(0.5),1),round(subset['賠償金額_千'].quantile(0.75),1),ColumnDataSource(subset_law)          
    
    def make_plot(src):
        # Blank plot with correct labels
        p = figure(plot_width = 400, plot_height = 300,
          x_axis_label = '賠償金額 (單位:千元)', y_axis_label = '案件數量')

        # Quad glyphs to create a histogram
        p.quad(source = src, bottom = 0, top = 'count', left = 'left', right = 'right',
               color = 'color', fill_alpha = 0.7, hover_fill_color = 'color',
               hover_fill_alpha = 1.0)

        # Hover tool with vline mode
        hover = HoverTool(tooltips=[('金額', '@f_interval'),
                                     ('數量', '@f_count')],
                          mode='vline')
        p.title.text = '台北市車禍賠償金額分布圖'

        p.add_tools(hover)
        
        # Styling
        p = style(p)

        return p
    
    def style(p):
        # Title 
        p.title.align = 'center'
        p.title.text_font_size = '17pt'
        p.title.text_font = 'serif'

        # Axis titles
        p.xaxis.axis_label_text_font_size = '14pt'
        p.xaxis.axis_label_text_font_style = 'bold'
        p.yaxis.axis_label_text_font_size = '14pt'
        p.yaxis.axis_label_text_font_style = 'bold'

        # Tick labels
        p.xaxis.major_label_text_font_size = '12pt'
        p.yaxis.major_label_text_font_size = '12pt'

        return p    

    def update(attr, old, new):
        factors_to_plot = [factor_selection.labels[i] for i in factor_selection.active]
        
        new_src,length= make_dataset(factors_to_plot,
                               range_start = range_select.value[0],
                               range_end = range_select.value[1],
                               bin_width = binwidth_select.value)
        
        src.data.update(new_src.data)
        p.title.text = '台北市車禍賠償金額分布圖 %s 案件' % length  
        
    def update_law_range(attr,old,new):
        factors_to_plot = [factor_selection.labels[i] for i in factor_selection.active]
        first,second,third,new_bar=make_dataset_law_range(factors_to_plot)
        bar.data.update(new_bar.data)
        if len(bar.data['law'])>0:
            law_text_1.update(text='%s：%s'%(bar.data['law'][0],bar.data['value'][0]),style={'font-size': '150%','font-family':'SimHei','color':'goldenrod'})    
            law_text_2.update(text='%s：%s'%(bar.data['law'][1],bar.data['value'][1]),style={'font-size': '150%','font-family':'SimHei','color':'goldenrod'})    
            law_text_3.update(text='%s：%s'%(bar.data['law'][2],bar.data['value'][2]),style={'font-size': '150%','font-family':'SimHei','color':'goldenrod'}) 
        
            money_text_1.update(text=' 25 percent：%s'%(first),style={'font-size': '150%','font-family':'SimHei','color':'saddlebrown'})    
            money_text_2.update(text=' 50 percent：%s '%(second),style={'font-size': '150%','font-family':'SimHei','color':'saddlebrown'})    
            money_text_3.update(text=' 75 percent：%s'%(third),style={'font-size': '150%','font-family':'SimHei','color':'saddlebrown'})   
    def update_download():
        def make_dataset_factor(factor_list,range_start = 0, range_end = 20000):
            subset=car
            for i, factor_name in enumerate(factor_list):
                # Subset to the factor
                subset = subset[subset[factor_name]==True]
            subset=subset[['案由','全文_摘要','法院見解_摘要','賠償金額_千']]
            subset=subset[(subset['賠償金額_千']>=range_start) & (subset['賠償金額_千']<=range_end)]
            subset.sort_values('賠償金額_千',inplace=True,ascending=False)
            return ColumnDataSource(subset)         
        
        def update_data(attr, old, new):
            factors_to_plot = [factor_selection.labels[i] for i in factor_selection.active]  
        
            new_factor_src= make_dataset_factor(factors_to_plot, range_start = range_select.value[0],
                               range_end = range_select.value[1])
            factor_src.data.update(new_factor_src.data)
        
        factor_selection.on_change('active', update_data)
        range_select.on_change('value', update_data)
        
        initial_factors = [factor_selection.labels[i] for i in factor_selection.active]
        
        factor_src = make_dataset_factor(initial_factors,range_start = range_select.value[0],
                               range_end = range_select.value[1])
        button.callback = CustomJS(args=dict(source=factor_src),code=open(join(dirname(__file__),'download.js')).read())

    #widget
    factor_selection = CheckboxGroup(labels=factors, active = [0, 1])
    factor_selection.on_change('active', update)
    factor_selection.on_change('active', update_law_range)
    
    binwidth_select = Slider(start = 1, end = 100, 
                         step = 1, value = 10,
                         title = '一單位金額大小 $NTD(單位:千元)')
    binwidth_select.on_change('value', update)
    
    range_select = RangeSlider(start = 0, end = 20000, value = (0,20000),
                               step = 1, title = '賠償金額範圍 $NTD(單位:千元)')
    range_select.on_change('value', update)
    
    button = Button(label="所選條件之判決書下載", button_type="success")
    button.on_click(update_download)
    
    #dataset and appearance
    initial_factors = [factor_selection.labels[i] for i in factor_selection.active]
    
    src,length= make_dataset(initial_factors,
                      range_start = range_select.value[0],
                      range_end = range_select.value[1],
                      bin_width = binwidth_select.value)
    
    first,second,third,bar=make_dataset_law_range(initial_factors)
    
    law_text=Paragraph(text='TOP 3 法條',style={'font-size': '185%','font-family':'SimHei','text_alignment':'right'})    
    law_text_1=Paragraph(text='%s：%s'%(bar.data['law'][0],bar.data['value'][0]),style={'font-size': '150%','font-family':'SimHei','color':'goldenrod'})    
    law_text_1.on_change('text',update_law_range)
    law_text_2=Paragraph(text='%s：%s'%(bar.data['law'][1],bar.data['value'][1]),style={'font-size': '150%','font-family':'SimHei','color':'goldenrod'})    
    law_text_2.on_change('text',update_law_range)
    law_text_3=Paragraph(text='%s：%s'%(bar.data['law'][2],bar.data['value'][2]),style={'font-size': '150%','font-family':'SimHei','color':'goldenrod',
                                                                                          }) 
    law_text_3.on_change('text',update_law_range)     
    
    money_text=Paragraph(text=' 賠償金額四分位數',style={'font-size': '180%','font-family':'SimHei'})    
    money_text_1=Paragraph(text=' 25 percent：%s'%(first),style={'font-size': '150%','font-family':'SimHei','color':'saddlebrown'})    
    money_text_1.on_change('text',update_law_range)
    money_text_2=Paragraph(text=' 50 percent：%s '%(second),style={'font-size': '150%','font-family':'SimHei','color':'saddlebrown'})    
    money_text_2.on_change('text',update_law_range)
    money_text_3=Paragraph(text=' 75 percent：%s'%(third),style={'font-size': '150%','font-family':'SimHei','color':'saddlebrown'})    
    money_text_3.on_change('text',update_law_range)
    
    p_text=Paragraph(text='肇事原因',width=80,height=55)
    p_text_1=Paragraph(text='人車影響',width=80,height=230)
    p_text_2=Paragraph(text='上訴對象',width=80,height=10)
    
    p = make_plot(src)
    
    
    # Put controls in a single element
    controls = WidgetBox(factor_selection, binwidth_select,range_select,button)
    
    # Create a layout
    label=column(p_text,p_text_1,p_text_2)
    left=gridplot([label,controls],ncols=2)
    money=column(money_text,money_text_1,money_text_3,money_text_2)
    law=column(law_text,law_text_1,law_text_2,law_text_3)
    texts=gridplot([money,law],ncols=1,spacing=7)
    layout = gridplot([left,p,texts],plot_width=500, plot_height=500,ncols=3)
    
    # Make a tab with the layout 
    tab = Panel(child=layout, title = '車禍判決書互動式查詢系統')
    return tab
