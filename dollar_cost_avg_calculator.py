import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
import pandas_datareader.data as web
from datetime import datetime, timedelta
import math
import yfinance as yf


def add_row():
    global rows, search_field, add_row_flag, search_button
    new_row = rows + 1
    search_field_label = ttk.Label(StockSearchFrame, text="Stock symbol")
    search_field_label.grid(row=new_row, column=0)
    search_field = ttk.Entry(StockSearchFrame, width=10)
    search_field.grid(row=new_row, column=1)

    search_button = ttk.Button(
        StockSearchFrame, text="Add to graph", command=AddToGraph)
    search_button.grid(row=new_row, column=6)
    rows += 1
    search_button.config(state="enabled")


def AddToGraph():
    global cost, search_button
    ticker = search_field.get()
    time_interval = int(time_interval_input.get())
    investment = int(investment_input.get())
    df = getData(ticker, time_interval)
    date_list, investment_list, _ = cal_investment(
        df, investment)
    add_to_treeview(ticker, investment_list)

    axis.plot(date_list, investment_list, label=f'{ticker} Investment')
    axis.legend()
    canvas.draw()
    search_button.config(state="disabled")


def getData(ticker, time_interval):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365 * time_interval)
    df = yf.download(ticker, start=start_date, end=end_date)
    df = df.sort_values(by='Date')
    df = df[['Close']]  # 保留 'Close' 列，可以根据需要调整
    return df


def cal_investment(df, investment):
    monthly_data = df.resample('MS').first()
    monthly_data = monthly_data.iloc[1:]
    date_list = []
    totalCaptial_list = []
    share_number_list = []
    saving_list = []

    saving = 0
    balance = 0
    share_number = 0
    for index, row in monthly_data.iterrows():
        close = row['Close']
        balance += investment
        canBuy = math.floor(balance / close)
        share_number += canBuy
        balance -= close * canBuy

        saving += investment
        saving_list.append(saving)
        totalCaptial_list.append(balance + share_number * close)
        date_list.append(index)
        share_number_list.append(share_number)
    return date_list, totalCaptial_list, saving_list


def add_to_treeview(ticker, investment_list):
    global cost
    profit = round((investment_list[-1]-cost), 2)
    tree.insert('', tk.END, values=(
        ticker, cost, profit, str(round((profit/cost)*100, 2))+'%'))


def showGraph():
    global cost, add_row_flag

    ticker = search_field.get()
    time_interval = int(time_interval_input.get())
    investment = int(investment_input.get())

    df = getData(ticker, time_interval)
    date_list, investment_list, normal_saving_list = cal_investment(
        df, investment)
    cost = round(normal_saving_list[-1], 2)

    add_to_treeview(ticker, investment_list)
    # 清空當前的圖表
    axis.cla()
    # 繪製原始圖像的直方圖
    axis.plot(date_list, normal_saving_list, label='Normal Saving')
    axis.plot(date_list, investment_list, label=f'{ticker} Investment')

    # 設置圖表標題
    axis.set_title(label="Dollar Cost Averaging Camparsion")
    axis.set_xlabel(xlabel="Date")
    axis.set_ylabel(ylabel="Total Value")
    # 添加圖例
    axis.legend()
    axis.grid(True)
    canvas.draw()
    add_button.config(state="enabled")
    search_button.config(state="disabled")


def on_configure(event):
    main_canvas.configure(scrollregion=main_canvas.bbox('all'))


def initialize_scroll_region():
    main_canvas.configure(scrollregion=main_canvas.bbox('all'))


root = tk.Tk()
root.title("Dollar Cost Averaging Calculator")
root.geometry('1400x1000')

main_canvas = tk.Canvas(root)
main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(root, orient='vertical', command=main_canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill='y')

main_canvas.configure(yscrollcommand=scrollbar.set)
root.after(100, initialize_scroll_region)


main_frame = ttk.Frame(main_canvas)
main_canvas.create_window((0, 0), window=main_frame, anchor='nw')
main_canvas.configure(scrollregion=main_canvas.bbox('all'))
main_canvas.bind('<Configure>', on_configure)


DollarCostAveragingFrame = ttk.Frame(main_frame)
DollarCostAveragingFrame.pack(fill='both', expand=True)

StockSearchFrame = ttk.Frame(DollarCostAveragingFrame)
CanvaFrame = ttk.Frame(DollarCostAveragingFrame)
TableFrame = ttk.Frame(DollarCostAveragingFrame)

StockSearchFrame.pack()
CanvaFrame.pack()
TableFrame.pack()

rows = 0
cost = 0

search_field_label = ttk.Label(StockSearchFrame, text="Stock symbol")
search_field_label.grid(row=0, column=0)
search_field = ttk.Entry(StockSearchFrame, width=10)
search_field.grid(row=0, column=1)
time_interval_label = ttk.Label(StockSearchFrame, text="Time Interval")
time_interval_label.grid(row=0, column=2)
time_interval_input = ttk.Combobox(
    StockSearchFrame, values=[1, 3, 5], width=10)
time_interval_input.grid(row=0, column=3)

investment_label = ttk.Label(StockSearchFrame, text="Monthly investment")
investment_label.grid(row=0, column=4)
investment_input = ttk.Entry(StockSearchFrame, width=10)
investment_input.grid(row=0, column=5)

search_button = ttk.Button(
    StockSearchFrame, text="Add to graph", command=showGraph)
search_button.grid(row=0, column=6)

add_button = ttk.Button(StockSearchFrame, text="+",
                        width=3, command=add_row, state="disabled")
add_button.grid(row=0, column=7)
# Canva Frame
fig = Figure(figsize=(10, 6))
fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

canvas = FigureCanvasTkAgg(fig, CanvaFrame)
canvas.draw()
canvas.get_tk_widget().pack(
    fill=tk.BOTH, expand=True)
axis = fig.add_subplot()

tree = ttk.Treeview(TableFrame, columns=(
    'Stock', 'Cost', 'Profit', 'Return of Investment(ROI)'), show='headings')

tree.heading('Stock', text='Stock')
tree.heading('Cost', text='Cost')
tree.heading('Profit', text='Profit')
tree.heading('Return of Investment(ROI)', text='Return of Investment(ROI)')

tree.pack(padx=10, pady=10)

root.mainloop()
