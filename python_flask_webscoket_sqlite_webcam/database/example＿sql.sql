--
-- File generated with SQLiteStudio v3.2.1 on 週二 7月 23 13:03:55 2024
--
-- Text encoding used: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: Class2PID
DROP TABLE IF EXISTS Class2PID;

CREATE TABLE Class2PID (
    class_id   INTEGER,
    p_id       INTEGER NOT NULL,
    label_name TEXT    NOT NULL,
    PRIMARY KEY (
        class_id
    ),
    FOREIGN KEY (
        p_id
    )
    REFERENCES PRODUCTS (p_id) 
);

INSERT INTO Class2PID (
                          class_id,
                          p_id,
                          label_name
                      )
                      VALUES (
                          0,
                          0,
                          'lollipop'
                      );

INSERT INTO Class2PID (
                          class_id,
                          p_id,
                          label_name
                      )
                      VALUES (
                          1,
                          1,
                          'cookie'
                      );

INSERT INTO Class2PID (
                          class_id,
                          p_id,
                          label_name
                      )
                      VALUES (
                          2,
                          2,
                          'fruit'
                      );

INSERT INTO Class2PID (
                          class_id,
                          p_id,
                          label_name
                      )
                      VALUES (
                          3,
                          3,
                          'noodles'
                      );


-- Table: ORDER_D
DROP TABLE IF EXISTS ORDER_D;

CREATE TABLE ORDER_D (
    o_id    INTEGER,
    o_no    INTEGER,
    p_id    INTEGER,
    p_name  TEXT,
    p_price INTEGER,
    p_qty   INTEGER,
    PRIMARY KEY (
        o_id,
        o_no
    )
);

INSERT INTO ORDER_D (
                        o_id,
                        o_no,
                        p_id,
                        p_name,
                        p_price,
                        p_qty
                    )
                    VALUES (
                        1,
                        1,
                        3,
                        '加州蘋果',
                        30,
                        1
                    );

INSERT INTO ORDER_D (
                        o_id,
                        o_no,
                        p_id,
                        p_name,
                        p_price,
                        p_qty
                    )
                    VALUES (
                        1,
                        2,
                        2,
                        '杏仁巧克力酥片',
                        50,
                        1
                    );

INSERT INTO ORDER_D (
                        o_id,
                        o_no,
                        p_id,
                        p_name,
                        p_price,
                        p_qty
                    )
                    VALUES (
                        1,
                        3,
                        2,
                        '杏仁巧克力酥片',
                        50,
                        1
                    );

INSERT INTO ORDER_D (
                        o_id,
                        o_no,
                        p_id,
                        p_name,
                        p_price,
                        p_qty
                    )
                    VALUES (
                        1,
                        4,
                        2,
                        '杏仁巧克力酥片',
                        50,
                        1
                    );

INSERT INTO ORDER_D (
                        o_id,
                        o_no,
                        p_id,
                        p_name,
                        p_price,
                        p_qty
                    )
                    VALUES (
                        2,
                        1,
                        2,
                        '杏仁巧克力酥片',
                        88,
                        1
                    );

INSERT INTO ORDER_D (
                        o_id,
                        o_no,
                        p_id,
                        p_name,
                        p_price,
                        p_qty
                    )
                    VALUES (
                        2,
                        2,
                        2,
                        '杏仁巧克力酥片',
                        50,
                        1
                    );

INSERT INTO ORDER_D (
                        o_id,
                        o_no,
                        p_id,
                        p_name,
                        p_price,
                        p_qty
                    )
                    VALUES (
                        2,
                        3,
                        2,
                        '杏仁巧克力酥片',
                        50,
                        1
                    );

INSERT INTO ORDER_D (
                        o_id,
                        o_no,
                        p_id,
                        p_name,
                        p_price,
                        p_qty
                    )
                    VALUES (
                        2,
                        4,
                        2,
                        '杏仁巧克力酥片',
                        50,
                        1
                    );

INSERT INTO ORDER_D (
                        o_id,
                        o_no,
                        p_id,
                        p_name,
                        p_price,
                        p_qty
                    )
                    VALUES (
                        2,
                        5,
                        2,
                        '杏仁巧克力酥片',
                        50,
                        1
                    );

INSERT INTO ORDER_D (
                        o_id,
                        o_no,
                        p_id,
                        p_name,
                        p_price,
                        p_qty
                    )
                    VALUES (
                        2,
                        6,
                        2,
                        '杏仁巧克力酥片',
                        50,
                        1
                    );


-- Table: ORDER_M
DROP TABLE IF EXISTS ORDER_M;

CREATE TABLE ORDER_M (
    o_id    INTEGER PRIMARY KEY,
    o_date  TEXT,
    o_total INTEGER
);

INSERT INTO ORDER_M (
                        o_id,
                        o_date,
                        o_total
                    )
                    VALUES (
                        1,
                        '20240718',
                        180
                    );

INSERT INTO ORDER_M (
                        o_id,
                        o_date,
                        o_total
                    )
                    VALUES (
                        2,
                        '20240718',
                        338
                    );


-- Table: PRODUCTS
DROP TABLE IF EXISTS PRODUCTS;

CREATE TABLE PRODUCTS (
    p_id       INTEGER PRIMARY KEY,
    p_category TEXT    NOT NULL,
    p_name     TEXT    NOT NULL,
    p_price    INTEGER DEFAULT 0
);

INSERT INTO PRODUCTS (
                         p_id,
                         p_category,
                         p_name,
                         p_price
                     )
                     VALUES (
                         0,
                         'object',
                         '棒棒糖',
                         12
                     );

INSERT INTO PRODUCTS (
                         p_id,
                         p_category,
                         p_name,
                         p_price
                     )
                     VALUES (
                         1,
                         'object',
                         '餅乾',
                         88
                     );

INSERT INTO PRODUCTS (
                         p_id,
                         p_category,
                         p_name,
                         p_price
                     )
                     VALUES (
                         2,
                         'object',
                         '蘋果',
                         25
                     );

INSERT INTO PRODUCTS (
                         p_id,
                         p_category,
                         p_name,
                         p_price
                     )
                     VALUES (
                         3,
                         'object',
                         '泡麵',
                         30
                     );

INSERT INTO PRODUCTS (
                         p_id,
                         p_category,
                         p_name,
                         p_price
                     )
                     VALUES (
                         4,
                         'object',
                         '大麥紅茶加粉條',
                         100
                     );

INSERT INTO PRODUCTS (
                         p_id,
                         p_category,
                         p_name,
                         p_price
                     )
                     VALUES (
                         5,
                         'Drink',
                         '高山金萱茶',
                         200
                     );

INSERT INTO PRODUCTS (
                         p_id,
                         p_category,
                         p_name,
                         p_price
                     )
                     VALUES (
                         8,
                         'Drink',
                         '焙香決明大麥',
                         85
                     );

INSERT INTO PRODUCTS (
                         p_id,
                         p_category,
                         p_name,
                         p_price
                     )
                     VALUES (
                         9,
                         'object',
                         '好人一枚',
                         888
                     );


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
