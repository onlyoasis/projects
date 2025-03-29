export const mockDiskData = [
  {
    product_name: "WD Elements Desktop 18TB",
    capacity: "18TB",
    price: "$279.99",
    price_per_tb: "$15.56",
    interface: "USB 3.0",
    form_factor: "3.5\"",
    seller: "Amazon",
    product_url: "https://amazon.com",
    seller_url: "https://amazon.com",
    date_scraped: "2023-04-15"
  },
  {
    product_name: "Seagate Exos X18 18TB",
    capacity: "18TB",
    price: "$289.99",
    price_per_tb: "$16.11",
    interface: "SATA 6Gb/s",
    form_factor: "3.5\"",
    seller: "Newegg",
    product_url: "https://newegg.com",
    seller_url: "https://newegg.com",
    date_scraped: "2023-04-15"
  },
  {
    product_name: "Samsung 870 EVO 4TB",
    capacity: "4TB",
    price: "$329.99",
    price_per_tb: "$82.50",
    interface: "SATA 6Gb/s",
    form_factor: "2.5\"",
    seller: "B&H",
    product_url: "https://bhphotovideo.com",
    seller_url: "https://bhphotovideo.com",
    date_scraped: "2023-04-15"
  },
  {
    product_name: "Crucial MX500 2TB",
    capacity: "2TB",
    price: "$159.99",
    price_per_tb: "$80.00",
    interface: "SATA 6Gb/s",
    form_factor: "2.5\"",
    seller: "Amazon",
    product_url: "https://amazon.com",
    seller_url: "https://amazon.com",
    date_scraped: "2023-04-15"
  },
  {
    product_name: "WD Black SN850X 2TB",
    capacity: "2TB",
    price: "$179.99",
    price_per_tb: "$90.00",
    interface: "NVMe",
    form_factor: "M.2",
    seller: "BestBuy",
    product_url: "https://bestbuy.com",
    seller_url: "https://bestbuy.com",
    date_scraped: "2023-04-15"
  },
  {
    product_name: "Samsung 990 PRO 2TB",
    capacity: "2TB",
    price: "$219.99",
    price_per_tb: "$110.00",
    interface: "NVMe",
    form_factor: "M.2",
    seller: "Amazon",
    product_url: "https://amazon.com",
    seller_url: "https://amazon.com",
    date_scraped: "2023-04-15"
  },
  {
    product_name: "Seagate Expansion 5TB",
    capacity: "5TB",
    price: "$109.99",
    price_per_tb: "$22.00",
    interface: "USB 3.0",
    form_factor: "2.5\"",
    seller: "Walmart",
    product_url: "https://walmart.com",
    seller_url: "https://walmart.com",
    date_scraped: "2023-04-15"
  },
  {
    product_name: "Toshiba N300 14TB",
    capacity: "14TB",
    price: "$259.99",
    price_per_tb: "$18.57",
    interface: "SATA 6Gb/s",
    form_factor: "3.5\"",
    seller: "Newegg",
    product_url: "https://newegg.com",
    seller_url: "https://newegg.com",
    date_scraped: "2023-04-15"
  }
];

export const mockStats = {
  total_products: 245,
  seller_distribution: {
    "Amazon": 78,
    "Newegg": 65,
    "B&H": 42,
    "BestBuy": 35,
    "Walmart": 25
  },
  interface_distribution: {
    "SATA 6Gb/s": 120,
    "USB 3.0": 75,
    "NVMe": 50
  },
  form_factor_distribution: {
    "3.5\"": 140,
    "2.5\"": 65,
    "M.2": 40
  }
};

export const mockHistoryData = [
  { date: "2023-04-01", count: 240, avg_price: 16.75 },
  { date: "2023-04-08", count: 242, avg_price: 16.32 },
  { date: "2023-04-15", count: 245, avg_price: 15.89 }
]; 