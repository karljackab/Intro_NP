create table user(
    uname varchar(50) primary key not null,
    bucket_name varchar(50) not null,
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
    upload_file_name varchar(40),
    date_time datetime default current_timestamp,
    foreign key (bname) references board(bname) on delete cascade,
    foreign key (author) references user(uname) on delete cascade
);

create table comment(
    author varchar(50),
    upload_comment_name varchar(40),
    pid integer,
    date_time datetime default current_timestamp,
    foreign key (author) references user(uname) on delete cascade,
    foreign key (pid) references post(pid) on delete cascade
);

create table mail(
    mail_pid integer primary key autoincrement,
    mail_subject varchar(70),
    source_user varchar(50),
    target_user varchar(50),
    upload_mail_name varchar(50),
    date_time datetime default current_timestamp,
    foreign key (source_user) references user(uname) on delete cascade,
    foreign key (target_user) references user(uname) on delete cascade
);