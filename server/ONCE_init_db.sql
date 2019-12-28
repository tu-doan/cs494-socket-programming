CREATE TABLE my_user(  
  id integer PRIMARY KEY,
  name varchar(100) UNIQUE NOT NULL,
  password varchar(12) NOT NULL,
  date varchar(100) default NULL,
  note text
);
