create database toutiao default charset=utf8;  # 创建数据库
create user heima  identified by 'hm123456';  # 创建用户&密码
grant all on toutiao.* to 'heima'@'%';  # 给用户heima开启数据库toutiao的所有操作权限
flush privileges;  # 刷新权限
