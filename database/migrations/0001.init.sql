PRAGMA foreign_keys = ON;

create table supplier (
  supplier_id integer primary key,
  supplier_name varchar(120) not null unique
);

create table brand (
    brand_id integer primary key,
    title varchar(120) not null unique
);

create table nomenclature_type (
    type_id integer primary key,
    title varchar(50)
);

INSERT INTO nomenclature_type (type_id, title)
VALUES
    (1, 'Автокамера'),
    (2, 'Автошина'),
    (3, 'Диск'),
    (4, 'Ободная лента');

create table nomenclature (
  nomenclature_id integer primary key,
  supplier_id integer,
  title varchar(500) not null,
  code varchar(150),
  price decimal not null,
  price_purchase decimal not null,
  rest integer not null,
  condition smallint not null default 1,
  brand integer,
  n_type integer,
  foreign key(supplier_id) references supplier(supplier_id),
  foreign key(brand) references brand(brand_id),
  foreign key(n_type) references nomenclature_type(type_id),
  unique(supplier_id, title, code),
  CHECK ( price_purchase < price ),
  CHECK ( condition IN (0, 1) )
);