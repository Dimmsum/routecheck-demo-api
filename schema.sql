create table users (
  id    bigserial primary key,
  name  text      not null,
  email text      not null,
  age   integer   not null
);

create table items (
  id          bigserial primary key,
  title       text             not null,
  description text             not null,
  price       double precision not null,
  in_stock    boolean          not null
);

create table orders (
  id               bigserial primary key,
  item_id          bigint not null references items(id),
  quantity         integer not null,
  shipping_address text    not null,
  status           text    not null default 'pending'
);
