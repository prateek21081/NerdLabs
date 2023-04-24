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
product.x=y
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


## conflict serializable schedule

      T1        T2
begin
r(product)
r(category)
                begin
                r(product)
product.x=y
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

## not-conflict serializable schedule

      T1                T2
begin
r(product)
r(category)
                      begin
product.x=y            
w(product)             
                      r(product)

category.a=b
w(category)
                      r(category)
                      r(review)
commit
                      commit

### Resolved schedule for T1, T2 using locks

      T1                T2
begin
lock-x(product)
lock-x(category)
r(product)
r(category)
                      begin
                      lock-x(product)
product.x=y            |
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
