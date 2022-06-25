-- Inserts into user_logins using our temp postgres table to cross join laterally and populate it

insert into user_logins (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date)
select p.* from user_logins_info l cross join lateral json_populate_recordset(null::user_logins, info) as p

