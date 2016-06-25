
conn = connect('localhost:28000');
db = conn.getDB("AAA");

var cursor = db.BBB.find();

while(cursor.hasNext())
{
    r = cursor.next();
    print(r["_id"]);
}
