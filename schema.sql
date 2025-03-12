drop table if exists users;
drop table if exists messages;

create table if not exists users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firstname varchar(120) not null,
    familyname varchar(120) not null,
    email varchar(120) not null,
    password varchar(120) not null,
    gender varchar(120) not null,
    city varchar(120) not null,
    country varchar(120) not null,
    token varchar(36)
);

create table if not exists messages(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    receiver_id INTEGER not null,
    writer_id INTEGER not null,
    content TEXT not null,
    FOREIGN KEY (receiver_id) references users(id),
    FOREIGN KEY (writer_id) references users(id)
);