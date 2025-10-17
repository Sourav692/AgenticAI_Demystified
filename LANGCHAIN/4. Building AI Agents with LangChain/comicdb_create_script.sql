/*******************************************************************************
   ComicStore Database - Version 1.0
   Script: ComicDB_Sqlite.sql
   Description: Creates and populates the ComicStore database.
   DB Server: Sqlite
   Author: Dipanjan (DJ)
********************************************************************************/

/*******************************************************************************
   Drop Tables
********************************************************************************/
DROP TABLE IF EXISTS [SaleTransactions];
DROP TABLE IF EXISTS [Sale];
DROP TABLE IF EXISTS [Inventory];
DROP TABLE IF EXISTS [Comic];
DROP TABLE IF EXISTS [Publisher];
DROP TABLE IF EXISTS [Customer];
DROP TABLE IF EXISTS [Employee];
DROP TABLE IF EXISTS [Branch];

/*******************************************************************************
   Create Tables
********************************************************************************/
CREATE TABLE [Branch] (
    [BranchId] INTEGER NOT NULL,
    [Name] NVARCHAR(100) NOT NULL,
    [City] NVARCHAR(50) NOT NULL,
    [State] NVARCHAR(50),
    [Country] NVARCHAR(50) NOT NULL,
    [PostalCode] NVARCHAR(10),
    CONSTRAINT [PK_Branch] PRIMARY KEY ([BranchId])
);

CREATE TABLE [Employee] (
    [EmployeeId] INTEGER NOT NULL,
    [FirstName] NVARCHAR(50) NOT NULL,
    [LastName] NVARCHAR(50) NOT NULL,
    [Title] NVARCHAR(50),
    [BranchId] INTEGER NOT NULL,
    [HireDate] DATETIME,
    [Email] NVARCHAR(100),
    [Phone] NVARCHAR(20),
    CONSTRAINT [PK_Employee] PRIMARY KEY ([EmployeeId]),
    FOREIGN KEY ([BranchId]) REFERENCES [Branch] ([BranchId])
);

CREATE TABLE [Publisher] (
    [PublisherId] INTEGER NOT NULL,
    [Name] NVARCHAR(100) NOT NULL,
    [Country] NVARCHAR(50),
    [EstablishedYear] INTEGER,
    CONSTRAINT [PK_Publisher] PRIMARY KEY ([PublisherId])
);

CREATE TABLE [Comic] (
    [ComicId] INTEGER NOT NULL,
    [Title] NVARCHAR(100) NOT NULL,
    [PublisherId] INTEGER NOT NULL,
    [Genre] NVARCHAR(50),
    [Price] NUMERIC(10, 2) NOT NULL,
    [ReleaseDate] DATETIME,
    CONSTRAINT [PK_Comic] PRIMARY KEY ([ComicId]),
    FOREIGN KEY ([PublisherId]) REFERENCES [Publisher] ([PublisherId])
);

CREATE TABLE [Inventory] (
    [InventoryId] INTEGER NOT NULL,
    [ComicId] INTEGER NOT NULL,
    [BranchId] INTEGER NOT NULL,
    [Stock] INTEGER NOT NULL,
    CONSTRAINT [PK_Inventory] PRIMARY KEY ([InventoryId]),
    FOREIGN KEY ([ComicId]) REFERENCES [Comic] ([ComicId]),
    FOREIGN KEY ([BranchId]) REFERENCES [Branch] ([BranchId])
);

CREATE TABLE [Customer] (
    [CustomerId] INTEGER NOT NULL,
    [FirstName] NVARCHAR(50) NOT NULL,
    [LastName] NVARCHAR(50) NOT NULL,
    [Email] NVARCHAR(100),
    [Phone] NVARCHAR(20),
    [Address] NVARCHAR(100),
    [City] NVARCHAR(50),
    [State] NVARCHAR(50),
    [Country] NVARCHAR(50) NOT NULL,
    [PostalCode] NVARCHAR(10),
    CONSTRAINT [PK_Customer] PRIMARY KEY ([CustomerId])
);

CREATE TABLE [Sale] (
    [SaleId] INTEGER NOT NULL,
    [CustomerId] INTEGER NOT NULL,
    [EmployeeId] INTEGER,
    [SaleDate] DATETIME NOT NULL,
    [TotalAmount] NUMERIC(10, 2) NOT NULL,
    CONSTRAINT [PK_Sale] PRIMARY KEY ([SaleId]),
    FOREIGN KEY ([CustomerId]) REFERENCES [Customer] ([CustomerId]),
    FOREIGN KEY ([EmployeeId]) REFERENCES [Employee] ([EmployeeId])
);

CREATE TABLE [SaleTransactions] (
    [TransactionId] INTEGER NOT NULL,
    [SaleId] INTEGER NOT NULL,
    [ComicId] INTEGER NOT NULL,
    [Quantity] INTEGER NOT NULL,
    [Price] NUMERIC(10, 2) NOT NULL,
    CONSTRAINT [PK_SaleTransactions] PRIMARY KEY ([TransactionId]),
    FOREIGN KEY ([SaleId]) REFERENCES [Sale] ([SaleId]),
    FOREIGN KEY ([ComicId]) REFERENCES [Comic] ([ComicId])
);

/*******************************************************************************
   Populate Tables
********************************************************************************/
INSERT INTO [Branch] ([BranchId], [Name], [City], [State], [Country], [PostalCode]) VALUES
    (1, 'Central Comics', 'New York', 'NY', 'USA', '10001'),
    (2, 'West Comics', 'Los Angeles', 'CA', 'USA', '90001'),
    (3, 'Midwest Comics', 'Chicago', 'IL', 'USA', '60601');

INSERT INTO [Employee] ([EmployeeId], [FirstName], [LastName], [Title], [BranchId], [HireDate], [Email], [Phone]) VALUES
    (1, 'John', 'Doe', 'Manager', 1, '2015-06-01', 'john.doe@comicstore.com', '555-1234'),
    (2, 'Jane', 'Smith', 'Sales Associate', 1, '2017-09-15', 'jane.smith@comicstore.com', '555-5678'),
    (3, 'Alice', 'Brown', 'Sales Associate', 2, '2018-03-12', 'alice.brown@comicstore.com', '555-9876'),
    (4, 'Michael', 'Clark', 'Manager', 2, '2016-02-20', 'michael.clark@comicstore.com', '555-6543'),
    (5, 'Emily', 'White', 'Sales Associate', 3, '2019-07-10', 'emily.white@comicstore.com', '555-4321');

INSERT INTO [Publisher] ([PublisherId], [Name], [Country], [EstablishedYear]) VALUES
    (1, 'Marvel Comics', 'USA', 1939),
    (2, 'DC Comics', 'USA', 1934),
    (3, 'Dark Horse Comics', 'USA', 1986),
    (4, 'Image Comics', 'USA', 1992),
    (5, 'IDW Publishing', 'USA', 1999);

INSERT INTO [Comic] ([ComicId], [Title], [PublisherId], [Genre], [Price], [ReleaseDate]) VALUES
    (1, 'Spider-Man: Homecoming', 1, 'Superhero', 19.99, '2017-07-07'),
    (2, 'Batman: Year One', 2, 'Superhero', 14.99, '1987-02-01'),
    (3, 'Hellboy: Seed of Destruction', 3, 'Supernatural', 24.99, '1994-10-01'),
    (4, 'Saga Volume 1', 4, 'Fantasy', 12.99, '2012-03-14'),
    (5, 'Transformers: All Hail Megatron', 5, 'Science Fiction', 25.99, '2008-09-01'),
    (6, 'X-Men: Days of Future Past', 1, 'Superhero', 18.99, '1981-01-01'),
    (7, 'The Killing Joke', 2, 'Superhero', 14.99, '1988-03-29'),
    (8, 'Sin City: The Hard Goodbye', 4, 'Noir', 22.99, '1991-06-01'),
    (9, 'Usagi Yojimbo Volume 1', 5, 'Adventure', 20.99, '1987-09-01'),
    (10, 'Deadpool: Merc with a Mouth', 1, 'Superhero', 16.99, '2009-08-05'),
    (11, 'Watchmen', 2, 'Superhero', 19.99, '1986-09-01'),
    (12, 'Spawn Volume 1', 4, 'Supernatural', 14.99, '1992-05-01'),
    (13, 'Ghost Rider: Trail of Tears', 1, 'Superhero', 17.99, '2007-03-01'),
    (14, 'Fables Volume 1', 5, 'Fantasy', 13.99, '2002-07-01'),
    (15, 'Black Hammer Volume 1', 3, 'Superhero', 20.99, '2016-05-01'),
    (16, 'Preacher Volume 1', 2, 'Fantasy', 18.99, '1995-01-01'),
    (17, 'Doctor Strange: The Oath', 1, 'Superhero', 14.99, '2006-10-01'),
    (18, 'Invincible Volume 1', 4, 'Superhero', 12.99, '2003-01-01'),
    (19, 'The Walking Dead Volume 1', 4, 'Horror', 10.99, '2004-05-01'),
    (20, 'Sandman Volume 1', 2, 'Fantasy', 16.99, '1989-01-01'),
    (21, 'Punisher: Welcome Back, Frank', 1, 'Action', 13.99, '2000-01-01'),
    (22, 'Hellblazer: Original Sins', 2, 'Fantasy', 14.99, '1988-01-01'),
    (23, '300', 4, 'Historical', 19.99, '1998-05-01'),
    (24, 'Thor: God of Thunder Volume 1', 1, 'Superhero', 17.99, '2013-01-01'),
    (25, 'Lumberjanes Volume 1', 5, 'Adventure', 11.99, '2015-04-01'),
    (26, 'The Boys Volume 1', 3, 'Action', 18.99, '2006-10-01'),
    (27, 'Captain Marvel Volume 1', 1, 'Superhero', 16.99, '2012-07-01'),
    (28, 'Elektra: Assassin', 1, 'Action', 13.99, '1986-01-01'),
    (29, 'V for Vendetta', 2, 'Dystopian', 19.99, '1988-03-01'),
    (30, 'The Umbrella Academy Volume 1', 3, 'Fantasy', 16.99, '2007-09-01'),
    (31, 'Wolverine: Old Man Logan', 1, 'Superhero', 20.99, '2008-08-01'),
    (32, 'Locke & Key Volume 1', 5, 'Horror', 15.99, '2008-02-01'),
    (33, 'Harley Quinn: Hot in the City', 2, 'Superhero', 17.99, '2013-11-01'),
    (34, 'Justice League: Origin', 2, 'Superhero', 14.99, '2011-12-01'),
    (35, 'Iron Man: Extremis', 1, 'Superhero', 18.99, '2005-01-01'),
    (36, 'Ms. Marvel Volume 1', 1, 'Superhero', 14.99, '2014-02-01'),
    (37, 'Superman: Red Son', 2, 'Superhero', 19.99, '2003-04-01'),
    (38, 'Black Panther: A Nation Under Our Feet', 1, 'Superhero', 16.99, '2016-01-01'),
    (39, 'Y: The Last Man Volume 1', 4, 'Science Fiction', 14.99, '2002-09-01'),
    (40, 'Silver Surfer: Requiem', 1, 'Superhero', 13.99, '2007-01-01'),
    (41, 'Hawkeye: My Life as a Weapon', 1, 'Superhero', 15.99, '2012-08-01'),
    (42, 'Batman: Hush', 2, 'Superhero', 22.99, '2002-01-01'),
    (43, 'Green Lantern: Rebirth', 2, 'Superhero', 16.99, '2004-01-01'),
    (44, 'Daredevil: Born Again', 1, 'Superhero', 14.99, '1986-01-01'),
    (45, 'Fantastic Four: The Coming of Galactus', 1, 'Superhero', 18.99, '1966-01-01'),
    (46, 'The Flash: Rebirth', 2, 'Superhero', 15.99, '2009-04-01'),
    (47, 'Jessica Jones: Alias', 1, 'Superhero', 19.99, '2001-01-01'),
    (48, 'The Authority Volume 1', 3, 'Superhero', 18.99, '1999-07-01'),
    (49, 'Deadly Class Volume 1', 4, 'Action', 10.99, '2014-01-01'),
    (50, 'Moon Knight Volume 1', 1, 'Superhero', 16.99, '2014-04-01');

INSERT INTO [Customer] ([CustomerId], [FirstName], [LastName], [Email], [Phone], [Address], [City], [State], [Country], [PostalCode]) VALUES
    (1, 'Robert', 'Taylor', 'robert.taylor@example.com', '555-1111', '123 Main St', 'New York', 'NY', 'USA', '10001'),
    (2, 'Emily', 'Davis', 'emily.davis@example.com', '555-2222', '456 Oak St', 'Los Angeles', 'CA', 'USA', '90001'),
    (3, 'Sarah', 'Connor', 'sarah.connor@example.com', '555-3333', '789 Pine St', 'Chicago', 'IL', 'USA', '60601'),
    (4, 'James', 'Bond', 'james.bond@example.com', '555-4444', '007 Secret Ln', 'Los Angeles', 'CA', 'USA', '90001'),
    (5, 'Laura', 'Croft', 'laura.croft@example.com', '555-5555', '500 Adventure Blvd', 'Chicago', 'IL', 'USA', '60601'),
    (6, 'Tony', 'Stark', 'tony.stark@example.com', '555-6666', '100 Stark Tower', 'New York', 'NY', 'USA', '10001'),
    (7, 'Bruce', 'Wayne', 'bruce.wayne@example.com', '555-7777', 'Wayne Manor', 'Gotham', 'NJ', 'USA', '07001'),
    (8, 'Diana', 'Prince', 'diana.prince@example.com', '555-8888', '200 Themyscira Blvd', 'Metropolis', 'IL', 'USA', '60602'),
    (9, 'Clark', 'Kent', 'clark.kent@example.com', '555-9999', '300 Daily Planet St', 'Metropolis', 'IL', 'USA', '60603'),
    (10, 'Natasha', 'Romanoff', 'natasha.romanoff@example.com', '555-1010', '400 Widow Ave', 'New York', 'NY', 'USA', '10002'),
    (11, 'Peter', 'Parker', 'peter.parker@example.com', '555-1212', '500 Queens Blvd', 'New York', 'NY', 'USA', '10003'),
    (12, 'Steve', 'Rogers', 'steve.rogers@example.com', '555-1313', '600 Shield St', 'Brooklyn', 'NY', 'USA', '10004'),
    (13, 'Bruce', 'Banner', 'bruce.banner@example.com', '555-1414', '700 Hulk Way', 'New York', 'NY', 'USA', '10005'),
    (14, 'Logan', 'Howlett', 'logan.howlett@example.com', '555-1515', '800 Wolverine Ln', 'Westchester', 'NY', 'USA', '10006'),
    (15, 'Wanda', 'Maximoff', 'wanda.maximoff@example.com', '555-1616', '900 Chaos Ave', 'Sokovia', 'NY', 'USA', '10007'),
    (16, 'Scott', 'Lang', 'scott.lang@example.com', '555-1717', '1000 Ant-Man St', 'San Francisco', 'CA', 'USA', '90002'),
    (17, 'TChalla', 'Black Panther', 'tchalla@example.com', '555-1818', '1100 Wakanda Blvd', 'Wakanda', 'NA', 'WAK', '00000'),
    (18, 'Matt', 'Murdock', 'matt.murdock@example.com', '555-1919', '1200 Daredevil Ave', 'New York', 'NY', 'USA', '10008'),
    (19, 'Barry', 'Allen', 'barry.allen@example.com', '555-2020', '1300 Flash Ln', 'Central City', 'MO', 'USA', '64015'),
    (20, 'Hal', 'Jordan', 'hal.jordan@example.com', '555-2121', '1400 Green Lantern Blvd', 'Coast City', 'CA', 'USA', '90003');

INSERT INTO [Inventory] ([InventoryId], [ComicId], [BranchId], [Stock]) VALUES
    (1, 1, 1, 50),
    (2, 2, 1, 30),
    (3, 3, 2, 20),
    (4, 4, 2, 40),
    (5, 5, 3, 25),
    (6, 6, 3, 15),
    (7, 7, 1, 35),
    (8, 8, 2, 20),
    (9, 9, 3, 10),
    (10, 10, 1, 45),
    (11, 11, 1, 50),
    (12, 12, 2, 25),
    (13, 13, 3, 30),
    (14, 14, 3, 20),
    (15, 15, 1, 50),
    (16, 16, 1, 30),
    (17, 17, 2, 20),
    (18, 18, 2, 40),
    (19, 19, 3, 25),
    (20, 20, 3, 15),
    (21, 21, 1, 35),
    (22, 22, 2, 20),
    (23, 23, 3, 10),
    (24, 24, 1, 45),
    (25, 25, 1, 50),
    (26, 26, 2, 25),
    (27, 27, 3, 30),
    (28, 28, 3, 20),
    (29, 29, 1, 50),
    (30, 30, 1, 30),
    (31, 31, 2, 20),
    (32, 32, 2, 40),
    (33, 33, 3, 25),
    (34, 34, 3, 15),
    (35, 35, 1, 35),
    (36, 36, 2, 20),
    (37, 37, 3, 10),
    (38, 38, 1, 45),
    (39, 39, 1, 50),
    (40, 40, 2, 25),
    (41, 41, 3, 30),
    (42, 42, 3, 20),
    (43, 43, 1, 50),
    (44, 44, 1, 30),
    (45, 45, 2, 20),
    (46, 46, 2, 40),
    (47, 47, 3, 25),
    (48, 48, 3, 15),
    (49, 49, 1, 35),
    (50, 50, 2, 20);

INSERT INTO [Sale] ([SaleId], [CustomerId], [EmployeeId], [SaleDate], [TotalAmount]) VALUES
    (1, 1, 1, '2023-01-15', 54.97),
    (2, 2, 2, '2023-01-20', 49.97),
    (3, 3, 3, '2023-01-25', 59.97),
    (4, 4, 4, '2023-01-30', 45.98),
    (5, 5, 5, '2023-02-05', 29.97),
    (6, 6, 1, '2023-02-10', 74.97),
    (7, 7, 2, '2023-02-15', 64.97),
    (8, 8, 3, '2023-02-20', 49.99),
    (9, 9, 4, '2023-02-25', 49.97),
    (10, 10, 5, '2023-03-01', 65.98),
    (11, 1, 1, '2023-03-05', 35.98),
    (12, 2, 2, '2023-03-10', 44.97),
    (13, 3, 3, '2023-03-15', 64.99),
    (14, 4, 4, '2023-03-20', 39.97),
    (15, 5, 5, '2023-03-25', 49.97),
    (16, 6, 1, '2023-03-30', 89.97),
    (17, 7, 2, '2023-04-05', 74.97),
    (18, 8, 3, '2023-04-10', 59.99),
    (19, 9, 4, '2023-04-15', 64.99),
    (20, 10, 5, '2023-04-20', 45.98);

INSERT INTO [SaleTransactions] ([TransactionId], [SaleId], [ComicId], [Quantity], [Price]) VALUES
    (1, 1, 1, 1, 19.99),
    (2, 1, 2, 2, 14.99),
    (3, 2, 3, 1, 24.99),
    (4, 2, 4, 1, 24.98),
    (5, 3, 5, 2, 29.99),
    (6, 3, 6, 1, 29.98),
    (7, 4, 7, 2, 22.99),
    (8, 4, 8, 1, 22.99),
    (9, 5, 9, 2, 14.99),
    (10, 6, 10, 2, 29.99),
    (11, 6, 11, 1, 14.99),
    (12, 7, 12, 1, 24.99),
    (13, 7, 13, 1, 14.99),
    (14, 8, 14, 1, 24.99),
    (15, 8, 15, 1, 24.99),
    (16, 9, 16, 2, 24.99),
    (17, 9, 17, 1, 24.99),
    (18, 10, 18, 2, 24.99),
    (19, 10, 19, 1, 16.99),
    (20, 10, 20, 1, 24.99),
    (21, 11, 21, 2, 14.99),
    (22, 11, 22, 1, 19.99),
    (23, 12, 23, 1, 24.99),
    (24, 12, 24, 1, 19.98),
    (25, 13, 25, 2, 29.99),
    (26, 13, 26, 2, 17.99),
    (27, 14, 27, 1, 24.99),
    (28, 14, 28, 1, 14.98),
    (29, 15, 29, 2, 24.99),
    (30, 15, 30, 1, 19.98),
    (31, 16, 31, 3, 29.99),
    (32, 16, 32, 2, 14.99),
    (33, 17, 33, 1, 24.99),
    (34, 17, 34, 1, 24.99),
    (35, 18, 35, 2, 24.99),
    (36, 18, 36, 2, 19.99),
    (37, 19, 37, 2, 29.99),
    (38, 19, 38, 1, 14.99),
    (39, 20, 39, 1, 24.99),
    (40, 20, 40, 1, 19.99);

    