from optparse import Values
import psycopg2
import random
import time
import os

# Assignment 5
# (Assignment 4)
# 
# Provide a constantly updating report on the sales of
# all products sold to date every 1 second
# 
# A sales report includes:
# Name of product
# Quantity sold
# Total revenue from sales of that product
# 
# Ordered by total revenue, then units sold,
# then alphabetically by product name, descending (Big $ -> Small $)
# 
# Example Report:
# Product 1 sold 455 total rev $50,000
# Product 2 sold 10  total rev $20
# Product 3 sold 100 total rev $1

# This is the program to show the sales report.

connection = psycopg2.connect("dbname=capstore2 user=postgres password=sponge")

cur = connection.cursor()

# Create necessary views for data processing

cur.execute("""CREATE OR REPLACE VIEW public.reportwithids
 AS
 SELECT round(avg(orders.productid)) AS productid,
    sum(orders.quantity * items.price) AS totalrevenue,
    sum(orders.quantity) AS totalquantity
   FROM orders
     JOIN items ON items.itemid = orders.productid
  GROUP BY orders.productid;

ALTER TABLE public.reportwithids
    OWNER TO postgres;""")

cur.execute("""CREATE OR REPLACE VIEW public.salesreport
 AS
 SELECT items.itemname,
    reportwithids.totalquantity,
    reportwithids.totalrevenue
   FROM items
     JOIN reportwithids ON items.itemid::numeric = reportwithids.productid
  ORDER BY reportwithids.totalrevenue DESC, reportwithids.totalquantity DESC, items.itemname DESC;

ALTER TABLE public.salesreport
    OWNER TO postgres;""")

printcur = connection.cursor()

# infinite loop that updates the sales report every x seconds...
x = 1
while True:
    # Now, show the sales report!

    printcur.execute("SELECT * FROM salesreport")
    report = printcur.fetchone()
    os.system('cls')
    print("[CAP NAME, QUANTITY SOLD, TOTAL REVENUE]")
    while (report):
        print(report)
        report = printcur.fetchone()

    time.sleep(x)