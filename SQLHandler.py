import mysql.connector


mydb = mysql.connector.connect(
  host="localhost",
  user="admin",
  password="admin@mysql",
  database="user_data"
)

def add_user(id, FirstName, LastName, isPremium):
  cursor = mydb.cursor(buffered=True)
  query = "INSERT INTO users(TelegramID, FirstName, LastName, isPremium) VALUES (%s, %s, %s, %s)"
  if isPremium == None:
    isPremium = False
  else:
    isPremium = True
  values = (id, FirstName, LastName, isPremium)
  print(values)
  cursor.execute(query, values)
  mydb.commit()
  cursor.close()

def isPresent(id):
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
  if result == []:
    return False
  else:
    return True


def add_pincode(id, pincode):
  cursor = mydb.cursor(buffered=True)
  query = "UPDATE users SET PinCode = %s WHERE TelegramID = %s;"
  values = (pincode, id)
  cursor.execute(query, values)
  cursor.close()
  mydb.commit()
  
def is_product_present(user_id, pid, fkpid):
  cursor = mydb.cursor(buffered=True)
  query = "SELECT UserID, ProductID, DesiredPrice FROM users_products WHERE UserID = (SELECT UserID FROM user_data.users WHERE TelegramID = %s) AND ProductID = (SELECT ProductID FROM user_data.products WHERE AmazonProductID = %s or fkpid = %s)"
  values = (user_id, pid, fkpid)
  cursor.execute(query,values)
  result = cursor.fetchall()
  cursor.close()
  mydb.commit()
  if result == []:
    print("No, Product Not Present")
    return False
  else:
    return result
#print(is_product_present(5204718144, 4564564564)[0][2])
def add_product_sql(id, pid, dprice,curr, high, avg, low, name, website, fkpid, fkslug):
  cursor = mydb.cursor()
  #query = "INSERT INTO products(AmazonProductID) VALUES (%s); INSERT INTO users_products (UserID, ProductID) VALUES ((select UserID from users WHERE TelegramID = %s), (select ProductID from products WHERE AmazonProductID = %s), %s);"
  query1 = "INSERT INTO products(AmazonProductID, current_price, lowest_price, highest_price, average_price, product_name, website, fkpid, fkslug) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
  query2 = "INSERT INTO users_products (UserID, ProductID, DesiredPrice) VALUES ((select UserID from users WHERE TelegramID = %s), (select ProductID from products WHERE AmazonProductID = %s or fkpid = %s), %s);"
  values1 = (pid, curr, low, high, avg, name, website, fkpid, fkslug)
  values2 = (id, pid, fkpid, dprice)
  cursor.execute(query1, values1)
  cursor.execute(query2, values2)
  cursor.close()
  mydb.commit()
  
def watchlist(id):
  cursor = mydb.cursor(buffered=True)
  query = "SELECT products.AmazonProductID, products.fkpid, products.fkslug, products.website , products.product_name, users_products.DesiredPrice, products.current_price FROM products INNER JOIN users_products ON products.ProductID = users_products.ProductID INNER JOIN users ON users_products.UserID = users.UserID WHERE users.TelegramID = %s;"
  values = (id)
  cursor.execute(query,(values,))
  rows = cursor.fetchall()
  cursor.close()
  mydb.commit()
  result_str = ""
  print("hello")
  if rows != []:
    for i, row in enumerate(rows):
      amazonpid, fkid, fkslugg, site, pname, dprice, currprice = row
      if site == 'Amazon':
        result_str += f"{i+1}. {pname}\n   Desired Price: {dprice}\n   Current Price: {currprice}     [Show on Amazon](https://www.amazon.in/dp/{amazonpid})\n\n"
      elif site == 'Flipkart':
        result_str += f"{i+1}. {pname}\n   Desired Price: {dprice}\n   Current Price: {currprice}    [Show On Flipkart](https://www.flipkart.com/{fkslugg}/p/{fkid})\n\n"
    print("--------", result_str, "-----------")
    return result_str
  else:
    return None
#https://www.flipkart.com/{fkslugg}/p/{fkid}  
def get_product_list():
  cursor = mydb.cursor(buffered=True)
  query = "SELECT products.website, products.AmazonProductID, products.fkpid, products.fkslug, products.current_price FROM products"
  cursor.execute(query)
  rows = cursor.fetchall()
  cursor.close()
  return rows

def update_product_list_amazon(pid, curr_price):
  cursor = mydb.cursor(buffered=True)
  query = "UPDATE products SET current_price = %s WHERE AmazonProductID = %s"
  values = (curr_price, pid)
  cursor.execute(query, values)
  cursor.close()
  mydb.commit()
  
def update_product_list_flipkart(fkpid, curr_price):
  cursor = mydb.cursor(buffered=True)
  query = "UPDATE products SET current_price = %s WHERE fkpid = %s"
  values = (curr_price, fkpid)
  cursor.execute(query, values)
  cursor.close()
  mydb.commit()
    
