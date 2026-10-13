// run with: npm run seed
require("dotenv").config();
const mongoose = require("mongoose");
const Product = require("./models/Product");

const pic = (n) => `https://picsum.photos/seed/campusbag${n}/400/400`;

const bags = [
  { name: "Urban Daypack 25L", description: "Light backpack for classes, 2 compartments.", price: 899, category: "backpack", image: pic(1), stock: 25 },
  { name: "Trek Pro 40L", description: "Big bag for trips and hostel travel, rain cover included.", price: 1799, category: "backpack", image: pic(2), stock: 12 },
  { name: "Campus Black Backpack", description: "Simple black bag with laptop pocket.", price: 1199, category: "backpack", image: pic(3), stock: 30 },
  { name: "Slim Laptop Bag 15.6", description: "Padded sleeve bag for laptops up to 15.6 inch.", price: 1499, category: "laptop bag", image: pic(4), stock: 18 },
  { name: "Office Messenger Laptop Bag", description: "Shoulder strap bag with water resistant cloth.", price: 1299, category: "laptop bag", image: pic(5), stock: 10 },
  { name: "Mini Sling Bag", description: "Small sling for phone, wallet and earphones.", price: 499, category: "sling bag", image: pic(6), stock: 40 },
  { name: "Crossbody Sling Pro", description: "Anti-theft zip sling bag with 3 pockets.", price: 749, category: "sling bag", image: pic(7), stock: 22 },
  { name: "Gym Duffel 30L", description: "Duffel for gym and sports with shoe pocket.", price: 999, category: "duffel", image: pic(8), stock: 15 },
];

async function run() {
  await mongoose.connect(process.env.MONGO_URI);
  await Product.deleteMany({});
  await Product.insertMany(bags);
  console.log(bags.length + " bags added");
  await mongoose.disconnect();
}

run().catch((e) => {
  console.log(e.message);
  process.exit(1);
});
