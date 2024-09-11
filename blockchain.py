import sqlite3,datetime,hashlib,cryptography,rsa
from rsa import PublicKey,PrivateKey
def init_db():
    db = sqlite3.connect("blockchain.db")
    db.execute("""
CREATE TABLE "main" (
	"id"	INTEGER,
	"previous_hash"	VARCHAR(255),
	"encrypted_data"	VARCHAR(1000),
	"current_hash"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
); """)
    db.commit()
    db.execute("""

CREATE TABLE "users" (
	"user"	user VARCHAR(255) NOT NULL,
	PRIMARY KEY("user")
);
    """)
    db.commit()

class User:
    def __init__(self,user) -> None:
        self.user = user
        if not self.user_exists():
            self.create_user()


    def add_data(self,json):
        # public_key = PublicKey(119845583484721490047179543470690197458047524894767391229304996950443495337477389049036448729623643878342907947912318406228925500656037406046246145989800934966807164534321143821583476727859563166759552902058446487093496999131201300454285226805315482275423282780644716357955351440279587457988348960025024274049, 65537)
        # private_key = PrivateKey(119845583484721490047179543470690197458047524894767391229304996950443495337477389049036448729623643878342907947912318406228925500656037406046246145989800934966807164534321143821583476727859563166759552902058446487093496999131201300454285226805315482275423282780644716357955351440279587457988348960025024274049, 65537, 16789024550608480707434813748026408026951711644702372993518915681249091821312844787817624178504885399805701174447762260823470177480249010862727702620261846721939086023289086110248436593700367522921274363384557589718509072497769276420431953426435291505313585044406010939510356725470630620887683549392018920193, 45714874385722092873631685292217233317749135383595479695117458646132104128260337850791258569009206649096452080691189566971947098796101414648153661670613702321826481, 2621588380042717244367969252401070560545395601383484965178801377405093129469781621434360132001997870388028905760358234428575526317081046072018129)

        
        time = str(datetime.datetime.now())
        data = str( {
            "username" : self.user,
            "time" : time,
            "data" : str(json)
        })
        # encrypted_data =  rsa.encrypt(str(data).encode("utf-8"),public_key)
        
        # current_hash = hashlib.sha256(str(first_hash + str(encrypted_data)).encode("utf-8")).hexdigest()

        db = sqlite3.connect("blockchain.db")
        cur = db.cursor()
        
        row = db.execute("SELECT * FROM main WHERE id=(SELECT max(id) FROM main);").fetchone()
        if row == None:
            previous_hash = "AEGIS"
        else:
            row = db.execute("SELECT * FROM main WHERE id=(SELECT max(id) FROM main);").fetchone()
            previous_hash = row[3]

        current_hash = hashlib.sha256(str(previous_hash + str(data)).encode("utf-8")).hexdigest()

        cur.execute(f"""INSERT INTO main(previous_hash,encrypted_data,current_hash) VALUES(?,?,?);""",(previous_hash,data,current_hash))
        db.commit()
        id = cur.lastrowid
        print(id)
        cur.execute(f"""INSERT INTO {self.user}(id,previous_hash,data,current_hash) VALUES(?,?,?,?)""",(id,previous_hash,data,current_hash))
        db.commit()
        if "location" in data:
            print(data)
            print(type(data))
            cur.execute(f"""INSERT INTO {self.user}_location(timestamp,location) VALUES(?,?)""",(time,json["location"]))
            db.commit()
        factors = self.crash_happened()
        if factors:
            if "location" in data:
                cur.execute(f"""INSERT INTO {self.user}_crash(timestamp,location,factors) VALUES(?,?,?)""",(time,json["location"],factors))
            cur.execute(f"""INSERT INTO {self.user}_crash(timestamp,location,factors) VALUES(?,?,?)""",(time,json["location"],factors))

            
            
        
        

    def fetch_data(self):
        db = sqlite3.connect("blockchain.db")
        results = db.execute(f"""SELECT * FROM {self.user}""").fetchall()
        return results


    def create_user(self):
        db = sqlite3.connect("blockchain.db")

        print("this was run")
        db.execute(f"""CREATE TABLE {self.user}(
                    id INT NOT NULL PRIMARY KEY,
                    previous_hash  VARCHAR(255) NOT NULL,
                    data VARCHAR(1000),
                    current_hash  VARCHAR(255) NOT NULL
                )""")
        db.commit()
        
        db.execute(f"""
        CREATE TABLE {self.user}_crash(
        "id" INTEGER,
        "timestamp" TEXT,
        "factors" TEXT,
        "location" TEXT,
        PRIMARY KEY("id" AUTOINCREMENT)
        );
        """)
        # Factors is the data like speed, rotational speed,
        # that was used to determine that a crash happened.
        db.commit()

        db.execute(f"""
        CREATE TABLE {self.user}_location(
        "id" INTEGER,
        "timestamp" TEXT,
        "location" TEXT,
        PRIMARY KEY("id" AUTOINCREMENT)
        )
        """)
        db.commit()
        # location will be in latitude longitude.
        print("user did not exist so tables were created.")
        return


    def crash_happened(self):
        # Determine whether a crash happened
        # or not based on past data for the 3 seconds or so.
        # So the server would have to constantly check if a crash
        # happened or not.
        return False

    def return_location_data(self):
        with sqlite3.connect("blockchain.db") as db:
            rows = db.execute(f"SELECT * FROM {self.user}_location").fetchall()
            return rows
    def return_crash_data(self):
        with sqlite3.connect("blockchain.db") as db:
            rows = db.execute(f"SELECT * FROM {self.user}_crash").fetchall()
            return rows

            
        

    def user_exists(self):
        db = sqlite3.connect("blockchain.db")
        found = db.execute("SELECT * FROM users WHERE username=?",(self.user,)).fetchall()
        if len(found) == 0:
            
            return False
        return True


if __name__ == "__main__":

    user = User("admin")
    user.add_data("Some Data")

    # This can be any type of data. Including bytes-like object and json.
    # can input video, image etc and also values like velocity. 
    data = {"favorite" : "coffee", "pet" : "cat"}
    user.add_data(data)

    # data is fetched using fetch_data()
    # this fetches all the data about the specific user
    print(user.fetch_data())

    # OUTPUT
    # [(1, 'AEGIS', "{'username': 'admin', 'time': '2024-08-09 19:16:59.646325', 'data': 'Some Data'}", 'e1c8a14e734789b63767f5a3a55b899944975d0cc05daef42066609559e6dad4'), (2, 'e1c8a14e734789b63767f5a3a55b899944975d0cc05daef42066609559e6dad4', '{\'username\': \'admin\', \'time\': \'2024-08-09 19:16:59.655035\', \'data\': "{\'favorite\': \'coffee\', \'pet\': \'cat\'}"}', 'e11010dd6a47a3798523d6aeb9034e21c5dd78c8eb515f4ea69b4e32dcb80fa2')]