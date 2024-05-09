CREATE TABLE user
(
  username TEXT NOT NULL,
  user_id INTEGER NOT NULL,
  password TEXT NOT NULL,
  PRIMARY KEY (user_id),
  UNIQUE (username)
);
CREATE TABLE session
(
  session_key INTEGER NOT NULL,
  session_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  PRIMARY KEY (session_id),
  FOREIGN KEY (user_id) REFERENCES user(user_id),
  UNIQUE (session_key)
);
CREATE TABLE public_keys
(
  key_id INTEGER NOT NULL,
  public_key_exp INTEGER NOT NULL,
  public_key_n INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  PRIMARY KEY (key_id),
  FOREIGN KEY (user_id) REFERENCES user(user_id)
);
