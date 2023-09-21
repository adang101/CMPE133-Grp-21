drop database if exists casso;

create database if not exists casso;

use casso;

create table account (
    username varchar(36) primary key,
    nickname varchar(36),
    email varchar(36) not null ,
    password varchar(255) not null,
    profile longblob not null,
    description varchar(500),
    creationDate timestamp not null
);

create table followers (
    username varchar(36),
    followers varchar(36),
    primary key (username, followers),
    foreign key (username) references account(username) on delete cascade ,
    foreign key (followers) references account(username) on delete cascade
);

create table posts (
    id int auto_increment primary key,
    username varchar(36) not null,
    creationDate timestamp not null,
    image longblob,
    text varchar(1000),
    foreign key (username) references account(username) on delete cascade
);

create table likes (
    id int,
    username varchar(36),
    primary key (id, username),
    foreign key (id) references posts(id) on delete cascade,
    foreign key (username) references account(username) on delete cascade
);

create table comments (
    cid int auto_increment primary key,
    id int,
    username varchar(36),
    creationDate timestamp not null,
    image longblob,
    text varchar(1000),
    foreign key (id) references posts(id) on delete cascade,
    foreign key (username) references account(username) on delete cascade
);

create table share (
    id int,
    username varchar(36),
    primary key (id, username),
    foreign key (id) references posts(id) on delete cascade,
    foreign key (username) references account(username) on delete cascade
);

create table artist (
    username varchar(36) primary key,
    commissionLimit int not null default 0,
    foreign key (username) references account(username) on delete cascade
);

create table commissionTransaction (
    id int auto_increment primary key,
    artist varchar(36) not null,
    client varchar(36) not null,
    amount decimal(13, 2) not null,
    status enum('Requested', 'Active', 'Completed') default 'Requested',
    foreign key (artist) references artist(username),
    foreign key (client) references account(username)
);

create table review (
    id int,
    client varchar(36),
    text varchar(500),
    image longblob,
    stars int not null default 0,
    primary key (id, client),
    foreign key (id) references commissionTransaction(id),
    foreign key (client) references commissionTransaction(client)
)