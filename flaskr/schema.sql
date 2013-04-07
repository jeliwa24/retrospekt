drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  category string not null,
  count integer not null
);