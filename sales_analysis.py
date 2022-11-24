import pandas as pd
import os
import numpy as np
import streamlit as st
from itertools import combinations
from collections import Counter

def read_dataset():
  files = [f for f in os.listdir('data') if len(f.split('.')) > 1 and f.split('.')[1] == 'csv']
  all_dataset = pd.DataFrame()
  for f in files:
    dataset = pd.read_csv("data/" + f)
    all_dataset = pd.concat([all_dataset, dataset])
  all_dataset = all_dataset.dropna(how='all')
  return all_dataset

def add_month_column(dataset):
  dataset['Month'] = dataset['Order Date'].str[0:2]
  dataset = dataset[dataset['Month'] != 'Or']
  dataset['Month'] = dataset['Month'].astype('int32')
  return dataset

def add_sales_column(dataset):
  dataset['Quantity Ordered'] = pd.to_numeric(dataset['Quantity Ordered'])
  dataset['Price Each'] = pd.to_numeric(dataset['Price Each'])

  dataset['Sales'] = dataset['Quantity Ordered'] * dataset['Price Each']
  return dataset

def add_city_column(dataset):
  dataset['City'] = dataset['Purchase Address'].apply(lambda x: x.split(',')[1])
  return dataset

def add_day_name_column(dataset):
  dataset['Order Date'] = pd.to_datetime(dataset['Order Date'])
  dataset['Day Name'] = dataset['Order Date'].apply(lambda x: x.day_name())
  return dataset

st.title("Sales Analysis")

st.header("Data Example")


dataset = read_dataset()
st.dataframe(dataset.head(10))

choice = st.selectbox("Select analysis topic: ", 
                        [ "Month with the biggest sales", 
                          "City with the biggest sales",
                          "Product with the biggest sales quantity",
                          "Products that are likely to be purchased together",
                          "Which day generates most sales frequency"])

if choice == "Month with the biggest sales":
  st.subheader("Month with the biggest sales")
  
  dataset = add_month_column(dataset)
  dataset = add_sales_column(dataset)

  results = dataset.groupby('Month').sum()

  st.bar_chart(results['Sales'])
  st.write("Month with the biggest sales is December")
elif choice == "City with the biggest sales":
  st.subheader("City with the biggest sales")

  dataset = add_month_column(dataset)
  dataset = add_sales_column(dataset)
  dataset = add_city_column(dataset)

  results = dataset.groupby('City').sum()
  st.bar_chart(results['Sales'])
  st.write("City with the biggest sales is Austin")
elif choice == "Product with the biggest sales quantity":
  st.subheader("Product with the biggest sales quantity")

  dataset = add_month_column(dataset)
  dataset = add_sales_column(dataset)
  product_group = dataset.groupby('Product')
  results = product_group.sum()['Quantity Ordered']
  st.bar_chart(results)
  st.write("Product with the biggest sales quantity is AAA Batteries (4-pack)")
elif choice == "Products that are likely to be purchased together":
  st.subheader("Products that are likely to be purchased together")

  dataset = add_month_column(dataset)
  dataset = add_sales_column(dataset)
  new_dataset = dataset[dataset['Order ID'].duplicated(keep=False)]
  new_dataset['Product_Bundle'] = new_dataset.groupby('Order ID')['Product'].transform(lambda x: ','.join(x))
  new_dataset = new_dataset[['Order ID', 'Product_Bundle']].drop_duplicates()

  count = Counter()

  for row in new_dataset['Product_Bundle']:
    row_list = row.split(',')
    count.update(Counter(combinations(row_list, 2)))
  
  products_bundle = list()
  res = pd.DataFrame(count.most_common(10))
  res = res.rename(columns={0: "items", 1: "totals"})
  items_col = res['items'].copy()
  totals_col = res['totals'].copy()

  new_index = list()

  for row in res['items']:
    new_index.append(row[0] + " & "  + row[1])

  st.bar_chart(count.most_common(10))
  st.write("Items by index: ", new_index)
  st.write("Products that are likely to be purchased together are iPhone & Lightning Charging Cable with 1005 occurances")

elif choice == "Which day generates most sales frequency":
  st.subheader("Which day generates most sales frequency")

  dataset = add_month_column(dataset)
  dataset = add_sales_column(dataset)
  dataset = add_day_name_column(dataset)
  dataset = dataset[['Order ID', 'Day Name']].drop_duplicates()
  results = dataset.groupby('Day Name').count()

  st.bar_chart(results)
  st.write("Day with highest sales frequency is Tuesday")
