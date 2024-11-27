from optparse import Values
import psycopg2
import random
import time
import os

# This program combines the three other programs into one.

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

# Upon starting program, assign a random max stock to each item from 1 to 5000, so it does not need to be manually reset.
cur.execute("SELECT itemid FROM items ORDER BY itemid DESC")
itemmax = (str(cur.fetchone())) 
itemmax = itemmax.replace('(', '')
itemmax = itemmax.replace(',)', '')
itemmax = int(itemmax)
for i in range(itemmax):
    startingstock = random.randint(1, 5000)
    cur.execute(f"""UPDATE items
                SET stock = {startingstock}
                WHERE itemid = {i};""")

# Clears orders table upon first running the program, so the program can start fresh and not have the table clogged with old orders.
cur.execute("TRUNCATE TABLE orders RESTART IDENTITY")
# RESTART IDENTITY makes the ID start back at 1, instead of where it left off last time. Weird and annoying quirk...
# ...that it doesn't automatically go back when you clear a table or delete elements

# infinite loop that creates new orders every x seconds (and commits them to the table)...
x = 1

# Keep track of current order number
currentorder = 0

while True:
    currentorder += 1
    # Get all customers as a list, and pick a random one.
    cur.execute("SELECT STRING_AGG(customerid::text, ',') FROM customers")
    customerlist = str(cur.fetchone())
    customerlist = customerlist.replace('(', '')
    customerlist = customerlist.replace(',)', '') # These replace lines cut out all the junk.
    customerlist = customerlist.replace("'", "")
    listCustomers = customerlist.split(",")
    randcust = random.choice(listCustomers) # Choose random customer ID to place the order
    loops = random.randint(1, 3) # Customers will order 1 to 3 products, stored in an array of appropriate size
    
    for i in range(loops):
        cur.execute("SELECT STRING_AGG(itemid::text, ',') FROM items WHERE stock > 0")
        itemslist = str(cur.fetchone())
        itemslist = itemslist.replace('(', '')
        itemslist = itemslist.replace(',)', '')
        itemslist = itemslist.replace("'", "")
        listItems = itemslist.split(",")
        if len(listItems) == 0:
            break
        else:
            productid = random.choice(listItems)

            cur.execute(f"SELECT stock FROM items WHERE itemid = {productid}")
            maxStock = str(cur.fetchone())
            maxStock = maxStock.replace('(', '')
            maxStock = maxStock.replace(',)', '')
            maxStock = maxStock.replace("'", "")
            maxStock = int(maxStock)
            if maxStock < 1000:
                quantity = random.randint(1, maxStock)
            else:
                quantity = random.randint(1, 1000) # Chooses a random quantity 
            cur.execute(f"INSERT INTO orders VALUES (DEFAULT, {currentorder}, {randcust}, {productid}, {quantity});")
            newStock = maxStock - quantity
            cur.execute(f"""UPDATE items
                        SET stock = {newStock}
                        WHERE itemid = {productid};""")

        # Now, restock some random items. 
        stockloops = random.randint(1, itemmax) 
        for i in range(stockloops):
            cur.execute("SELECT STRING_AGG(itemid::text, ',') FROM items")
            stockList = str(cur.fetchone())
            stockList = stockList.replace('(', '')
            stockList = stockList.replace(',)', '')
            stockList = stockList.replace("'", "")
            listToStock = stockList.split(",")
            stockid = random.choice(listToStock)
            
            cur.execute(f"SELECT stock FROM items WHERE itemid = {stockid}")
            itemStock = str(cur.fetchone())
            itemStock = itemStock.replace('(', '')
            itemStock = itemStock.replace(',)', '')
            itemStock = itemStock.replace("'", "")
            itemStock = int(itemStock)
            restock = itemStock + random.randint(1, 1000)

            cur.execute(f"""UPDATE items
                        SET stock = {restock}
                        WHERE itemid = {stockid};""")

    connection.commit() # Finally, commmits the new orders and restocks so they can be seen in PGAdmin

    # Now, show the sales report!

    printcur.execute("SELECT * FROM salesreport")
    report = printcur.fetchone()
    os.system('cls')
    print("[CAP NAME, QUANTITY SOLD, TOTAL REVENUE]")
    while (report):
        print(report)
        report = printcur.fetchone()

    time.sleep(x)