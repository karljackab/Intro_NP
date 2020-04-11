create table user(
    uname varchar(50) primary key not null,
    email varchar(70),
    pwd varhcar(50) not null
);

create table board(
    bname varchar(50) primary key not null,
    moderator varhcar(50),
    foreign key (moderator) references user(uname) on delete cascade
);

create table post(
    pid integer primary key autoincrement,
    bname varchar(50),
    title varchar(70),
    author varchar(50),
    content varchar(1000),
    date_time datetime default current_timestamp,
    foreign key (bname) references board(bname) on delete cascade,
    foreign key (author) references user(uname) on delete cascade
);

create table comment(
    author varchar(50),
    content varchar(1000),
    pid integer,
    date_time datetime default current_timestamp,
    foreign key (author) references user(uname) on delete cascade,
    foreign key (pid) references post(pid) on delete cascade
);