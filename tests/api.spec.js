// @ts-check
const { test, expect } = require("@playwright/test");

// Shared state across serial tests (safe because workers: 1 in playwright.config.js)
const ctx = {
  token: "",
  userId: null,
  itemId: null,
  orderId: null,
};

const ts = Date.now();
const email = `test_${ts}@example.com`;
const password = "password";

const auth = () => ({ Authorization: `Bearer ${ctx.token}` });
const json = () => ({ "Content-Type": "application/json" });

// ─── Health ──────────────────────────────────────────────────────────────────

test("GET /health → 200", async ({ request }) => {
  const res = await request.get("/health");
  expect(res.status()).toBe(200);
  expect((await res.json()).status).toBe("ok");
});

// ─── Auth ─────────────────────────────────────────────────────────────────────

test.describe.serial("Auth", () => {
  test("POST /auth/signup → 201 + token", async ({ request }) => {
    const res = await request.post("/auth/signup", {
      headers: json(),
      data: { email, password },
    });
    expect(res.status()).toBe(201);
    const body = await res.json();
    expect(body).toHaveProperty("access_token");
    ctx.token = body.access_token;
  });

  test("POST /auth/login → 200 + token", async ({ request }) => {
    const res = await request.post("/auth/login", {
      headers: json(),
      data: { email, password },
    });
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty("access_token");
    ctx.token = body.access_token; // refresh
  });

  test("POST /auth/login wrong password → 401", async ({ request }) => {
    const res = await request.post("/auth/login", {
      headers: json(),
      data: { email, password: "badpassword" },
    });
    expect(res.status()).toBe(401);
  });
});

// ─── Users ────────────────────────────────────────────────────────────────────

test.describe.serial("Users", () => {
  test("GET /users → 200 list", async ({ request }) => {
    const res = await request.get("/users");
    expect(res.status()).toBe(200);
    expect(Array.isArray((await res.json()).users)).toBe(true);
  });

  test("POST /users no auth → 403", async ({ request }) => {
    const res = await request.post("/users", {
      headers: json(),
      data: { name: "X", email: "x@x.com", age: 20 },
    });
    expect(res.status()).toBe(403);
  });

  test("POST /users → 201", async ({ request }) => {
    const res = await request.post("/users", {
      headers: { ...json(), ...auth() },
      data: { name: "Test User", email: `user_${ts}@example.com`, age: 30 },
    });
    expect(res.status()).toBe(201);
    const body = await res.json();
    expect(body).toHaveProperty("id");
    ctx.userId = body.id;
  });

  test("GET /users/:id → 200", async ({ request }) => {
    const res = await request.get(`/users/${ctx.userId}`);
    expect(res.status()).toBe(200);
    expect((await res.json()).id).toBe(ctx.userId);
  });

  test("GET /users/999999999 → 404", async ({ request }) => {
    const res = await request.get("/users/999999999");
    expect(res.status()).toBe(404);
  });

  test("PUT /users/:id → 200 updated name", async ({ request }) => {
    const res = await request.put(`/users/${ctx.userId}`, {
      headers: { ...json(), ...auth() },
      data: { name: "Updated Name" },
    });
    expect(res.status()).toBe(200);
    expect((await res.json()).name).toBe("Updated Name");
  });

  test("DELETE /users/:id → 204", async ({ request }) => {
    const res = await request.delete(`/users/${ctx.userId}`, {
      headers: auth(),
    });
    expect(res.status()).toBe(204);
  });
});

// ─── Items ────────────────────────────────────────────────────────────────────

test.describe.serial("Items", () => {
  test("GET /items → 200 list", async ({ request }) => {
    const res = await request.get("/items");
    expect(res.status()).toBe(200);
    expect(Array.isArray((await res.json()).items)).toBe(true);
  });

  test("GET /items?in_stock=true → 200", async ({ request }) => {
    const res = await request.get("/items?in_stock=true");
    expect(res.status()).toBe(200);
    expect(Array.isArray((await res.json()).items)).toBe(true);
  });

  test("POST /items no auth → 403", async ({ request }) => {
    const res = await request.post("/items", {
      headers: json(),
      data: { title: "X", description: "x", price: 1, in_stock: true },
    });
    expect(res.status()).toBe(403);
  });

  test("POST /items → 201", async ({ request }) => {
    const res = await request.post("/items", {
      headers: { ...json(), ...auth() },
      data: {
        title: "Test Item",
        description: "A product",
        price: 9.99,
        in_stock: true,
      },
    });
    expect(res.status()).toBe(201);
    const body = await res.json();
    expect(body).toHaveProperty("id");
    ctx.itemId = body.id;
  });

  test("GET /items/:id → 200", async ({ request }) => {
    const res = await request.get(`/items/${ctx.itemId}`);
    expect(res.status()).toBe(200);
    expect((await res.json()).id).toBe(ctx.itemId);
  });

  test("GET /items/999999999 → 404", async ({ request }) => {
    const res = await request.get("/items/999999999");
    expect(res.status()).toBe(404);
  });

  test("PUT /items/:id → 200 updated price", async ({ request }) => {
    const res = await request.put(`/items/${ctx.itemId}`, {
      headers: { ...json(), ...auth() },
      data: { price: 19.99 },
    });
    expect(res.status()).toBe(200);
    expect((await res.json()).price).toBe(19.99);
  });

  test("DELETE /items/:id → 204", async ({ request }) => {
    const res = await request.delete(`/items/${ctx.itemId}`, {
      headers: auth(),
    });
    expect(res.status()).toBe(204);
  });
});

// ─── Orders ───────────────────────────────────────────────────────────────────

test.describe.serial("Orders", () => {
  // Holds the item created for ordering (cleaned up after order tests)
  let orderItemId = null;

  test("GET /orders no auth → 403", async ({ request }) => {
    const res = await request.get("/orders");
    expect(res.status()).toBe(403);
  });

  test("POST /orders → 201 pending", async ({ request }) => {
    // Create a dedicated item to satisfy the FK constraint
    const itemRes = await request.post("/items", {
      headers: { ...json(), ...auth() },
      data: {
        title: "Order Item",
        description: "For order test",
        price: 5.0,
        in_stock: true,
      },
    });
    expect(itemRes.status()).toBe(201);
    orderItemId = (await itemRes.json()).id;

    const res = await request.post("/orders", {
      headers: { ...json(), ...auth() },
      data: {
        item_id: orderItemId,
        quantity: 2,
        shipping_address: "123 Test St",
      },
    });
    expect(res.status()).toBe(201);
    const body = await res.json();
    expect(body).toHaveProperty("id");
    expect(body.status).toBe("pending");
    ctx.orderId = body.id;
  });

  test("GET /orders/:id → 200", async ({ request }) => {
    const res = await request.get(`/orders/${ctx.orderId}`, {
      headers: auth(),
    });
    expect(res.status()).toBe(200);
    expect((await res.json()).id).toBe(ctx.orderId);
  });

  test("GET /orders/999999999 → 404", async ({ request }) => {
    const res = await request.get("/orders/999999999", {
      headers: auth(),
    });
    expect(res.status()).toBe(404);
  });
});
