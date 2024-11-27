from optparse import Values
import psycopg2
import random
import time
import os

# Assignment 5
# Keep track of the quantity of products in stock for each product type
# Decrease the available stock when an item is sold (by your Assignment 3 program)
# Modify your Assignment 3 program to NOT order products that are out of stock.
#   Constrain the random product choice to available in-stock products
#   Constrain the random product quantities to available quantities.
#   If no products are available when attempting an order, place no order, try again next order interval.

# This is the program to buy items.

connection = psycopg2.connect("dbname=capstore2 user=postgres password=sponge")

cur = connection.cursor()

# Upon starting program, assign a random max stock to each item from 1 to 5000, so it does not need to be manually reset.
cur.execute("SELECT itemid FROM items ORDER BY itemid DESC")
itemmax = (str(cur.fetchone())) 
itemmax = itemmax.replace('(', '')
itemmax = itemmax.replace(',)', '')
itemmax = int(itemmax)
for i in range(itemmax + 1):
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

        productid = random.choice(listItems)
        if(str(productid).upper() != "NONE"): # If the query returns "none", do NOT buy anything, because there's nothing left.
            cur.execute(f"SELECT stock FROM items WHERE itemid = {productid}")
            maxStock = str(cur.fetchone())
            maxStock = maxStock.replace('(', '')
            maxStock = maxStock.replace(',)', '')
            maxStock = maxStock.replace("'", "")
            maxStock = int(maxStock)     # Checking how much can be bought.
            if maxStock < 1000:
                quantity = random.randint(1, maxStock)
            else:
                quantity = random.randint(1, 1000) # Chooses a random quantity 
            cur.execute(f"INSERT INTO orders VALUES (DEFAULT, {currentorder}, {randcust}, {productid}, {quantity});")
            newStock = maxStock - quantity
            cur.execute(f"""UPDATE items
                        SET stock = {newStock}
                        WHERE itemid = {productid};""")
            listItems.remove(productid)

    connection.commit() # Finally, commmits the new orders so they can be seen in PGAdmin

    os.system('cls')
    print(f"Total orders placed: {currentorder}.")

    time.sleep(x)