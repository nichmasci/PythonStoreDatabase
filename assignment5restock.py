from optparse import Values
import psycopg2
import random
import time
import os

# Assignment 5
# Write a program that runs indefinitely and periodically (every X seconds, X is a positive hard-coded integer unrelated to other intervals) 
# adds a random amount (1-1000) of stock to a random set of products.

# This is the program to restock items.

connection = psycopg2.connect("dbname=capstore2 user=postgres password=sponge")

cur = connection.cursor()
printcur = connection.cursor()

# Find the maximum item index in the list, for use in restocking.
cur.execute("SELECT itemid FROM items ORDER BY itemid DESC")
itemmax = (str(cur.fetchone())) 
itemmax = itemmax.replace('(', '')
itemmax = itemmax.replace(',)', '')
itemmax = int(itemmax)

# infinite loop that restocks every x seconds (and commits it to the table)...
x = 1

while True:
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

        connection.commit() # Finally, commmits the restocks so they can be seen in PGAdmin

        # Let's see what we've just restocked...

        printcur.execute(f"SELECT itemname FROM items WHERE itemid = {stockid}")
        itemname = str(printcur.fetchone())
        itemname = itemname.replace('(', '')
        itemname = itemname.replace(',)', '')
        itemname = itemname.replace("'", "")

        print(f"{itemname} was restocked with {restock - itemStock} units. The total stock is now {restock}.")
        # F-strings are quite helpful for this.
    time.sleep(x)