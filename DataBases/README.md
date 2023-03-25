# Data Population

To create the database and populate the tables with the data provided, source
the `src.sql` file in your mysql session.

The `schema.sql` file is executed first which contains all the table schema
with suitable data types, integrity constraints and indexes. After that for
populating tables with data, there is a `.sql` file correponding to the table
that contains all the information and issues `INSERT` commands. The sample data
has been generated in such a way that it respects all the constraints by their
respective tables.

# Data Types

Data types for attributes have been chosen in a way that is space saving,
suitable for the type of information that particular attribute will be holding
and provide meaning to the data.