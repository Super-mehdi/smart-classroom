db = db.getSiblingDB("smartclass");

db.createUser({
  user: "smartclass",
  pwd: "emi101112",
  roles: [{ role: "readWrite", db: "smartclass" }]
});

db.createCollection("init");