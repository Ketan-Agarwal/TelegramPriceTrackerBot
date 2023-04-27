#!/usr/bin/python3
import mysql.connector
import mysql.connector.pooling
#import mysql.connector
#def conn():
#  mydb = mysql.connector.connect(
 #   host="192.168.0.101",
  #  user="admin",
   # password="admin@mysql",
    #database="user_data"
#)


# Define the database connection parameters
config = {
    'host': 'localhost',
    'user': 'admin',
    'password': 'admin@mysql',
    'database': 'user_data'
}

# Create a connection pool with a maximum of 10 connections
pool = mysql.connector.pooling.MySQLConnectionPool(pool_name='mypool',
                                                    pool_size=10,
                                                    **config)

def add_user(id, FirstName, LastName, isPremium):
  mydb = pool.get_connection()
  cursor = mydb.cursor(buffered=True)
  query = "INSERT INTO users(TelegramID, FirstName, LastName, isPremium, time_registered) VALUES (%s, %s, %s, %s, (select unix_timestamp()))"
  if isPremium == None:
    isPremium = False
  else:
    isPremium = True
  values = (id, FirstName, LastName, isPremium)
  print(values)
  cursor.execute(query, values)
  mydb.commit()
  cursor.close()
  mydb.close()

def isPresent(id):
  mydb = pool.get_connection()
  cursor = mydb.cursor(buffered=True)
  query = "SELECT TelegramID, FirstName FROM users WHERE TelegramID = %s"
  values = (id)
  cursor.execute(query, (values,))
  result = cursor.fetchall()
  print(result)
  for (TelegramID, FirstName) in cursor:
    print(TelegramID, FirstName)
    print(id)
  cursor.close()
  mydb.commit()
  mydb.close()
  if result == []:
    return False
  else:
    return True


def add_pincode(id, pincode):
  mydb = pool.get_connection()
  cursor = mydb.cursor(buffered=True)
  query = "UPDATE users SET PinCode = %s WHERE TelegramID = %s;"
  values = (pincode, id)
  cursor.execute(query, values)
  cursor.close()
  mydb.commit()
  mydb.close()

def is_product_present(user_id, pid, fkpid):
  mydb = pool.get_connection()
  cursor = mydb.cursor(buffered=True)
  query = "SELECT UserID, ProductID, DesiredPrice FROM users_products WHERE UserID = (SELECT UserID FROM user_data.users WHERE TelegramID = %s) AND ProductID = (SELECT ProductID FROM user_data.products WHERE AmazonProductID = %s or fkpid = %s)"
  values = (user_id, pid, fkpid)
  cursor.execute(query,values)
  result = cursor.fetchall()
  cursor.close()
  mydb.commit()
  mydb.close()
  if result == []:
    print("No, Product Not Present")
    return False
  else:
    return result
#print(is_product_present(5204718144, 4564564564)[0][2])
def add_product_sql(id, pid, dprice,curr, high, avg, low, name, website, fkpid, fkslug):
  mydb = pool.get_connection()
  cursor = mydb.cursor()
  #query = "INSERT INTO products(AmazonProductID) VALUES (%s); INSERT INTO users_products (UserID, ProductID) VALUES ((select UserID from users WHERE TelegramID = %s), (select ProductID from products WHERE AmazonProductID = %s), %s);"
  query1 = "INSERT INTO products(AmazonProductID, current_price, lowest_price, highest_price, average_price, product_name, website, fkpid, fkslug, time_registered) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, (select unix_timestamp()));"
  query2 = "INSERT INTO users_products (UserID, ProductID, DesiredPrice) VALUES ((select UserID from users WHERE TelegramID = %s), (select ProductID from products WHERE AmazonProductID = %s or fkpid = %s), %s);"
  values1 = (pid, curr, low, high, avg, name, website, fkpid, fkslug)
  values2 = (id, pid, fkpid, dprice)
  cursor.execute(query1, values1)
  cursor.execute(query2, values2)
  cursor.close()
  mydb.commit()
  mydb.close()
def watchlist(id):
  mydb = pool.get_connection()
  cursor = mydb.cursor(buffered=True)
  query = "SELECT products.AmazonProductID, products.fkpid, products.fkslug, products.website , products.product_name, users_products.DesiredPrice, products.current_price FROM products INNER JOIN users_products ON products.ProductID = users_products.ProductID INNER JOIN users ON users_products.UserID = users.UserID WHERE users.TelegramID = %s;"
  values = (id)
  cursor.execute(query,(values,))
  rows = cursor.fetchall()
  cursor.close()
  mydb.commit()
  mydb.close()
  result_str = ""
  print("hello")
  if rows != []:
    for i, row in enumerate(rows):
      amazonpid, fkid, fkslugg, site, pname, dprice, currprice = row
      if site == 'Amazon':
        result_str += f"------------------------------\n{i+1}. {pname}\n   Desired Price: {dprice}\n   Current Price: {currprice}     [Show on Amazon](https://www.amazon.in/dp/{amazonpid}?tag=b2bdeals-21)\n\n"
      elif site == 'Flipkart':
        result_str += f"------------------------------\n{i+1}. {pname}\n   Desired Price: {dprice}\n   Current Price: {currprice}    [Show On Flipkart](https://www.flipkart.com/{fkslugg}/p/{fkid})\n\n"
    print("--------", result_str, "-----------")
    return result_str
  else:
    return None
#https://www.flipkart.com/{fkslugg}/p/{fkid}  
def get_product_list():
  mydb = pool.get_connection()
  cursor = mydb.cursor(buffered=True)
  query = "SELECT products.website, products.AmazonProductID, products.fkpid, products.fkslug, products.current_price, products.lowest_price, products.highest_price, products.average_price FROM products"
  cursor.execute(query)
  rows = cursor.fetchall()
  cursor.close()
  mydb.close()
  return rows

def update_product_list_amazon(pid, curr_price, low, high, avg):
  mydb = pool.get_connection()
  cursor = mydb.cursor(buffered=True)
  query = "UPDATE products SET current_price = %s, lowest_price = %s, highest_price = %s, average_price = %s WHERE AmazonProductID = %s"
  values = (curr_price, low, high, avg, pid)
  cursor.execute(query, values)
  cursor.close()
  mydb.commit()
  mydb.close()

def update_product_list_flipkart(fkpid, curr_price, low, high, avg):
  mydb = pool.get_connection()
  cursor = mydb.cursor(buffered=True)
  query = "UPDATE products SET current_price = %s, lowest_price = %s, highest_price = %s, average_price = %s WHERE fkpid = %s"
  values = (curr_price, fkpid, low, high, avg)
  cursor.execute(query, values)
  cursor.close()
  mydb.commit()
  mydb.close()

def watcher():
  #while True:
  global rows
  mydb = pool.get_connection()
  cur = mydb.cursor()
  cur.execute('SELECT * FROM products')

  new_rows = cur.fetchall()

  # Check if any rows have been added or updated
  if len(new_rows) == len(rows):
    if new_rows != rows:
        print('Data has changed:')
        for row in new_rows:
          if row not in rows:
            rows = new_rows
            return True, row
    else:
      print("not changed")
  else:
    rows = new_rows
    print('new entry added')

  mydb.commit()
  cur.close()
  mydb.close()
  #time.sleep(10)


def watching():
  mydb1 = pool.get_connection()
  global rows
  cursor = mydb1.cursor(buffered=True)
  cursor.execute('SELECT * FROM products')
  rows = cursor.fetchall()

  print("watching rowss-----",rows)
  mydb1.commit()
  cursor.close()
  mydb1.close()
def get_users_for_product(pid):
  mydb = pool.get_connection()
  cursor = mydb.cursor()
  query = "SELECT u.TelegramID, up.DesiredPrice FROM users u INNER JOIN users_products up ON u.UserID = up.UserID INNER JOIN products p ON up.ProductID = p.ProductID WHERE p.ProductID = %s;"
  cursor.execute(query, (pid, ))
  rows = cursor.fetchall()
  print(rows)
  cursor.close()
  mydb.close()
  return rows