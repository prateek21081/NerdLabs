# Transactions

Searching for a product using its `prod_id`
```python
  cnx.start_transaction()
  cur.execute(f'SELECT * FROM product WHERE product.prod_id = %s', [prod_id])
  cur.execute(f'SELECT * FROM {category} WHERE {category}.prod_id = %s', [prod_id])
  cur.execute('SELECT * FROM review WHERE review.prod_id = %s', [prod_id])
  cnx.commit()
```


Deleting a product having a particular `prod_id`
```python
  cnx.start_transaction()
  cur.execute("SET FOREIGN_KEY_CHECKS=0")
  cur.execute(f"DELETE FROM {category} where prod_id=%s", [prod_id])
  cur.execute(f"DELETE FROM product where prod_id=%s", [prod_id])
  cur.execute("SET FOREIGN_KEY_CHECKS=1")
  cnx.commit()
```

Updating details of a product (replacing the product with new details)
```python
cnx.start_transaction()
cur.execute("SET FOREIGN_KEY_CHECKS=0")
cur.execute(f"DELETE FROM {category} where prod_id=%s", [prod_id])
cur.execute(f"DELETE FROM product where prod_id=%s", [prod_id])
cur.execute("SET FOREIGN_KEY_CHECKS=1")
cur.execute('INSERT INTO product VALUES (%s)', [values])
cur.execute(f'INSERT INTO {category} VALUES (%s)', [values])
cnx.commit()
```

Adding a new product in the store
```python
cnx.start_transaction()
cur.execute('INSERT INTO product VALUES (%s)', [values])
cur.execute(f'INSERT INTO {category} VALUES (%s)', [values])
cnx.commit()
```

# Conflicting Transactions

* admin updates a product
  T1
begin
r(product)
r(category)
product.qty=y
w(product)
category.a=b
w(category)
commit

* customer browsing a product
  T2
begin
r(product)
r(category)
r(review)
commit

* customer buying a product
  T3
begin
r(cart)
r(product)
product.qty=x
w(cart)
r(invoice)
w(invoice)
w(product)
commit

## conflict serializable schedule

      T1        T2
begin
r(product)
r(category)
                begin
                r(product)
product.qty=y
w(product)
category.a=b
                r(category)
w(category)
                r(review)
commit
                commit

Write after Read conflict on product from T2 to T1
Read after Write conflict on category from T1 to T2
This can be resolved to a serial schedule <T1, T2> by swapping non-conflicting operations.

      T1        T2
begin
r(product)
r(category)
product.qty=y
w(product)
category.a=b
w(category)
commit
                begin
                r(product)
                r(category)
                r(review)
                commit

## conflict serializable schedule

      T1        T3
begin
r(product)
r(category)
                begin
                r(cart)
product.qty=y
w(product)
                r(product)
                product.qty=x
                w(cart)
category.a=b
                r(invoice)
                w(invoice)
w(category)
                w(product)
commit
                commit

Write after Read conflict on product from T2 to T1
Read after Write conflict on category from T1 to T2
This can be resolved to a serial schedule <T1, T2> by swapping non-conflicting operations.

      T1        T3
begin
r(product)
r(category)
product.qty=y
w(product)
category.a=b
w(category)
commit
                begin
                r(cart)
                r(product)
                product.qty=x
                w(cart)
                r(invoice)
                w(invoice)
                w(product)
                commit

## not-conflict serializable schedule

      T1                T2
begin
r(product)
r(category)
                      begin
product.qty=y            
w(product)             
                      r(product)
                      product.qty=x

category.a=b
w(category)
                      r(category)
                      r(review)
commit
                      commit
                      


      T1                 T3
begin
r(product)
r(category)
                      begin
                      r(cart)
product.qty=y
                      r(product)
                      product.qty=x
                      w(cart)
w(product)
category.a=b
                      r(invoice)
                      w(invoice)
w(category)
                      w(product)
commit
                      commit

The precedence graph of above schedules contain a cycle, making them not conflict serializable.

### Resolved schedule using locks

      T1                T2
begin
lock-x(product)
lock-x(category)
r(product)
r(category)
                      begin
                      lock-x(product)
product.qty=y          |
w(product)             |
unlock-x(product)      |
                      r(product)

category.a=b
w(category)
unlock-x(category)
                      lock-x(category)
                      r(category)
                      lock-x(review)
                      r(review)
commit
                      commit
                      unlock-x(product)
                      unlock-x(category)
                      unlock-x(review)


      T1                 T3
begin
lock-x(product)
lock-x(category)
r(product)
r(category)
                      begin
                      lock-x(cart)
                      r(cart)
product.qty=y
                      lock-x(product)
w(product)              |
unlock(product)         |
                      r(product)
                      product.qty=x
                      w(cart)
category.a=b
                      r(invoice)
                      lock-x(invoice)
                      w(invoice)
w(category)
unlock-x(category)
                      w(product)
commit
                      commit
                      unlock(cart)
                      unlock(product)
                      unlock(invoice)
