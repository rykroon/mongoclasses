# Conversions


Mongoclasses uses the `cattrs` library under the hood for data structuring and unstructuring.


## Python to MongoDB
When inserting or updating a mongoclass into the database, the mongoclass is
transformed into a dictionary and any types that are not compatible with MongoDB will
be converted into an appropriate type if applicable.

For example, the native `decimal.Decimal` type is not accepted by MongoDB, so it
will be converted into a `bson.Decimal128` type.

Below are the conversions when going from python to MongoDB.

| Original type | Converted type |
|---|---|
| decimal.Decimal | bson.Decimal128 |
| datetime.date | datetime.datetime |
| set | list |
| frozenset | list|
| enum.Enum | (The data type of the value of the enum) |


## MongoDB to Python
Additionally when querying the database using find() or find_one(), mongoclasses will
attempt to convert the values from MongoDB to the types defined on your mongoclass.

Going off the previous example, if a field in the database is of type
`bson.Decimal128` but is defined as a `decimal.Decimal` on your mongoclass, then it
will be converted to `decimal.Decimal` on your mongoclass instance.

